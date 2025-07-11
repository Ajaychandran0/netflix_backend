from abc import ABC, abstractmethod
from typing import Dict

class BaseQueueProducer(ABC):
    @abstractmethod
    def publish(self, stream_name: str, data: Dict) -> None:
        pass
