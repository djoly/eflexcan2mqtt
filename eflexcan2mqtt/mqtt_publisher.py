
import json
from logging import Logger
from .message_handler import MessageHandler
from .decode import parse_battery_data
from .mqtt_client import MQTTClient

class MQTTPublisher():
    """
    This MQTT Publisher class publishes the latest battery data
    aggregated and compiled by the MessageHandler.
    """

    # Timestamp of the last publish time for a given node id. This is used as a sanity check to
    # ensure messages are not needlessly being republished if there's an interruption in the CAN
    # messages.
    _published_timestamps: dict[str, float] = {}

    def __init__(self, logger: Logger, message_handler: MessageHandler, mqtt_client: MQTTClient):
        self._logger = logger
        self._message_handler = message_handler
        self._mqtt_client = mqtt_client


    def publish_data(self) -> None:
        """
        Publish all battery data where both type 10X and type 60X messages have been aggregated and compiled.
        Timestamp of last 60X message is added to published timestamps. If, for any reason, messages are processed out
        of order, such that an older last 60X message is received after a more recent one has been published, publishing is skipped
        for that node.
        """
        timestamps = self._message_handler.timestamps
        compiled_message10X_data = self._message_handler.compiled_message10X_data
        compiled_message60X_data = self._message_handler.compiled_message60X_data

        self._logger.debug("Publish initiated.")
        self._logger.debug("Current compiled 10X messages is: %s", compiled_message10X_data)
        self._logger.debug("Current compiled 60X messages is: %s", compiled_message60X_data)

        all_battery_data = []
        new_published_timestamps: dict[str, float] = {}

        for node_id, data10 in compiled_message10X_data.items():
            if (node_id in compiled_message60X_data):
                if not (node_id in self._published_timestamps and self._published_timestamps[node_id] >= timestamps[node_id]):
                    battery_data = parse_battery_data(data10, compiled_message60X_data[node_id])
                    battery_data['time'] = round(timestamps[node_id])

                    self._logger.debug("Parsed battery data %s", battery_data)

                    all_battery_data.append(battery_data)
                    new_published_timestamps[node_id] = timestamps[node_id] 
                else:
                    self._logger.warning("Most recent data for battery %s was already published at timestamp %s. Won't republish.", node_id, self._published_timestamps[node_id])
        
        if len(all_battery_data) > 0:

            self._logger.debug("Publishing battery data to mqtt: %s", all_battery_data)

            self._mqtt_client.publish(all_battery_data)

            self._published_timestamps.update(new_published_timestamps)
        return

