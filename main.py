import asyncio
import configparser
import signal
import logging
import logging.handlers
import os
import sys
import argparse
from typing import List
import psutil
import can
from can.notifier import MessageRecipient
from can.bus import BusABC
from eflexcan2mqtt.message_handler import MessageHandler
from eflexcan2mqtt.paho_client import PahoClient
from eflexcan2mqtt.mqtt_publisher import MQTTPublisher

# Ensure we don't blow up if there's no such thing as stdout on the system.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

pid = os.getpid()
process = psutil.Process(pid)

parser = argparse.ArgumentParser(description="Fortress eFlex Battery CAN 2 MQTT Service")
parser.add_argument("--config_path",help="The path to the configuration file", default="./conf/eflexcan2mqtt.ini")
args = parser.parse_args()

if not os.path.isfile(args.config_path):
    print ("Configuration file %s not found. Shutting down.", args.config_path)
    sys.exit(1)

config_parser = configparser.ConfigParser()
config_parser.read(args.config_path)

config = {
    'log_dir': config_parser['logging'].get('log_dir'),
    'log_level': config_parser['logging'].get('log_level', "INFO"),
    'profile': config_parser['logging'].getboolean('profile', 'no'),
    'can_interface': config_parser['can'].get('interface', 'socketcan'),
    'can_channel': config_parser['can'].get('channel'),
    'mqtt_hostname' : config_parser['mqtt'].get('hostname'),
    'mqtt_port' : int(config_parser['mqtt'].get('port', '1883')),
    'mqtt_topic' : config_parser['mqtt'].get('topic'),
    'mqtt_keepalive' : int(config_parser['mqtt'].get('keepalive', '60')),
    'mqtt_client_id' : config_parser['mqtt'].get('client_id'),
    'mqtt_publish_interval' : int(config_parser['mqtt'].get('publish_interval', '60')),
    'mqtt_qos' : int(config_parser['mqtt'].get('qos', '2')),
}

if not os.path.isdir(config['log_dir']):
    print ("Specified log directy %s is not a directory. Shutting down.", config['log_dir'])
    sys.exit(1)

logFilename: str = str(config['log_dir']).rstrip('/') + '/eflexcan2mqtt.out'

logger = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(logFilename, maxBytes=524288, backupCount=5)

formatter = logging.Formatter(
    '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(config['log_level'])


logger.info("Running process ID is %s", pid)
logger.info("Running with config: %s", config)


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


def log_memory_info(msg: str):
    """Logs memory info"""
    mem_info = process.memory_info()
    logger.info("%s Current memory usage of process %s: RSS %s, VMS %s", msg, pid, mem_info.rss, mem_info.vms)

def _on_message_available(self, bus: BusABC) -> None:
    """This is a patch for the standard can.Notifier._on_message_available method,
    which does not capture CAN network errors. During real-world operation, socketcan
    network interfaces will sometimes do down. The interface can be configured at the OS level
    to recover, but if the error is not handled no more CAN bus messages will be processed by
    the event handler when the network interface is back up. There are two error codes observed
    when the network goes down:
        - Error code 100 is "Network is down".
        - Error code 19 is "No such device".
    """
    try:
        if msg := bus.recv(0):
            self._on_message_received(msg)
    except can.CanOperationError as e:
        if e.error_code in (100, 19):
            logger.error("CAN network down.")
        else:
            raise
            
can.Notifier._on_message_available =  _on_message_available


async def main() -> None:
    with can.Bus(
        interface=config['can_interface'], channel=config['can_channel']
    ) as bus:
        
        add_signal_handlers()

        message_handler = MessageHandler(logger)
        mqtt_client = PahoClient(
            topic = config['mqtt_topic'],
            hostname = config['mqtt_hostname'],
            port = config['mqtt_port'],
            client_id = config['mqtt_client_id'],
            qos = config['mqtt_qos'],
            keepalive = config['mqtt_keepalive']
        )
        mqtt_publisher = MQTTPublisher(logger = logger, mqtt_client = mqtt_client, message_handler = message_handler)

        listeners: List[MessageRecipient] = [
            message_handler
        ]

        loop = asyncio.get_running_loop()

        log_memory_info("Memory Before can.Notifier initialization.")

        notifier = can.Notifier(bus, listeners, loop = loop)

        try:
            while True:
                await asyncio.sleep(config['mqtt_publish_interval'])
                mqtt_publisher.publish_data()
                if config['profile']: log_memory_info("In main task loop, after mqtt publish.")

        except asyncio.CancelledError as e:
            logger.info("Got shut down signal")
            log_memory_info("Shuting down...")

        finally:
            notifier.stop()


if __name__ == "__main__":
    try:
        logger.info("Starting event loop...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shut down complete.")



