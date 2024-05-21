from typing import List
from eflexcan2mqtt.mqtt_client import MQTTClient

class MockMQTTClient(MQTTClient):

    _payload: List[dict] | None
    
    def publish(self, payload: List[dict]) -> None:
        self._payload = payload
        return
    
    @property
    def payload(self):
        return self._payload