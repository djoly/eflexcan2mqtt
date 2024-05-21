import asyncio
import signal
import logging
import logging.handlers
import os
import argparse
import json
from typing import List
import psutil
import can
from can.notifier import MessageRecipient
from eflexcan2mqtt.message_handler import MessageHandler
from eflexcan2mqtt.paho_client import PahoClient
from eflexcan2mqtt.mqtt_publisher import MQTTPublisher

pid = os.getpid()
process = psutil.Process(pid)

#logFilename = os.getenv('LOG_FILENAME', '/var/log/app/eflex-data-publisher.out')
logFilename = os.getenv('LOG_FILENAME', './logs/eflexcan2mqtt.out')

logger = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(logFilename, maxBytes=524288, backupCount=5)

formatter = logging.Formatter(
    '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))

parser = argparse.ArgumentParser(description="Fortress eFlex Battery CAN 2 MQTT Shell Script")
parser.add_argument("--mqtt_host",help="The hostname of the MQTT server", default="localhost")
parser.add_argument("--mqtt_port",help="The port of the MQTT server", type=int, default=1883)
parser.add_argument("--mqtt_topic",help="The topic the data is published to.", default="eflexbatteries")
parser.add_argument("--mqtt_client_id", help="MQTT client id", default="")
parser.add_argument("--mqtt_keepalive", help="MQTT keepalive time", type=int, default=60)
parser.add_argument("--mqtt_qos", help="MQTT QoS", type=int, default=2)
parser.add_argument("--publish_interval", help="MQTT publish interval, in seconds", type=int, default=60)
parser.add_argument("--can_interface",help="The CAN interface (e.g. socketcan)", default="socketcan")
parser.add_argument("--can_channel",help="The CAN channel (i.e. can0, vcan0, etc)", default="vcan0")
parser.add_argument("--can_log_file",help="The CAN logfile", default="eflexbatteries-can-message-log.asc")
parser.add_argument("--profile", help="Enable memory profiling", action="store_const", const=True, default=False)

args = parser.parse_args()
logger.info("Running process ID is %s", pid)
logger.info("Running with args: %s", args)


def add_signal_handlers():
    """
    Adds signal handler to gracefully shutdown running tasks.    
    """
    loop = asyncio.get_running_loop()

    async def shutdown(sig: signal.Signals) -> None:
        """
        Cancel all running async tasks (other than this one) when called.
        By catching asyncio.CancelledError, any running task can perform
        any necessary cleanup when it's cancelled.
        """
        tasks = []
        for task in asyncio.all_tasks(loop):
            if task is not asyncio.current_task(loop):
                task.cancel()
                tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Finished awaiting cancelled tasks, results: %s", results)

        loop.stop()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(sig)))


# async def shutdown(signal, loop) -> None:
#     """Cleanup tasks tied to the service's shutdown."""
#     logging.info("Received exit signal... %s", signal.name)
#     tasks = [t for t in asyncio.all_tasks() if t is not
#              asyncio.current_task()]

#     for task in tasks:
#         task.cancel()

#     logging.info("Cancelling %s outstanding tasks", len(tasks))
#     await asyncio.gather(*tasks)
#     loop.stop()

# async def publish_task() -> None:
#     """publish task"""
#     while True:

#         if args.profile:
#             mem_info = process.memory_info()
#             logger.info("Current memory usage of process %s: RSS %s, VMS %s", pid, mem_info.rss, mem_info.vms)

#         await asyncio.sleep(args.publish_interval)
#         publish_data()

async def main() -> None:
    with can.Bus(
        interface=args.can_interface, channel=args.can_channel
    ) as bus:
        
        message_handler = MessageHandler(logger)
        mqtt_client = PahoClient(
            topic = args.mqtt_topic,
            hostname = args.mqtt_host,
            port = args.mqtt_port,
            client_id = args.mqtt_client_id,
            qos = args.mqtt_qos,
            keepalive = args.mqtt_keepalive
        )
        mqtt_publisher = MQTTPublisher(logger = logger, mqtt_client = mqtt_client, message_handler = message_handler)

        listeners: List[MessageRecipient] = [
            message_handler
        ]

        loop = asyncio.get_running_loop()
        notifier = can.Notifier(bus, listeners, loop = loop)

        try:
            while True:
                if args.profile:
                    mem_info = process.memory_info()
                    logger.info("Current memory usage of process %s: RSS %s, VMS %s", pid, mem_info.rss, mem_info.vms)

                await asyncio.sleep(args.publish_interval)
                mqtt_publisher.publish_data()

        except asyncio.CancelledError:
            logger.info("Shutting down")

        finally:
            #Clean-up
            notifier.stop()


if __name__ == "__main__":
    asyncio.run(main())



