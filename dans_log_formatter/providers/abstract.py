import sys
from abc import ABC, abstractmethod
from logging import LogRecord
from typing import Any

from formatter_error import FormatterError


class AbstractProvider(ABC):
    def __init__(self):
        self._formatter_errors: list[FormatterError] = []

    @abstractmethod
    def get_attributes(self, record: LogRecord) -> None | dict[str, Any]:
        raise NotImplementedError()

    def record_error(self, message: str) -> None:
        self._formatter_errors.append(FormatterError(message, sys.exc_info()))

    def get_errors(self) -> list[FormatterError]:
        return self._formatter_errors
