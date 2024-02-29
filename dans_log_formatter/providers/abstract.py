from abc import ABC, abstractmethod
from logging import LogRecord
from typing import Any


class AbstractProvider(ABC):
    @abstractmethod
    def get_attributes(self, record: LogRecord) -> None | dict[str, Any]:
        raise NotImplementedError()
