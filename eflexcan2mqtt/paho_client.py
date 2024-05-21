import json
from typing import List
from .mqtt_client import MQTTClient
import paho.mqtt.publish as publish

class PahoClient(MQTTClient):
    """Paho MQTT Client"""

    def __init__(self, topic: str,
                 hostname: str, port:int, keepalive: int, qos: int, client_id: str):
        self._topic = topic
        self._hostname = hostname
        self._port = port
        self._keepalive = keepalive
        self._qos = qos
        self._client_id = client_id

    def publish(self, payload: List[dict]):

        publish.single(
            topic = self._topic,
            hostname = self._hostname,
            port = self._port,
            client_id = self._client_id,
            qos = self._qos,
            keepalive = self._keepalive,
            payload = json.dumps(payload)
        )
        