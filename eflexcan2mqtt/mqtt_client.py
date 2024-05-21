
from typing import List
from abc import ABCMeta, abstractmethod
from typing import Any

class MQTTClient(metaclass=ABCMeta):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def publish(self, payload: List[dict]) -> None:
        """
        Publish payload to an MQTT server
        """