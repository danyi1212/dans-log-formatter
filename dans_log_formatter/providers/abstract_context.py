from abc import abstractmethod, ABC
from contextvars import ContextVar
from logging import LogRecord
from typing import Any

from dans_log_formatter.providers.abstract import AbstractProvider


class AbstractContextProvider(AbstractProvider, ABC):
    def __init__(self, context: ContextVar):
        super().__init__()
        self.context = context

    def get_attributes(self, record: LogRecord) -> None | dict[str, Any]:
        value = self.context.get()
        if value is None:
            return

        return self.get_context_attributes(record, value)

    @abstractmethod
    def get_context_attributes(self, record: LogRecord, context_value) -> None | dict[str, Any]:
        raise NotImplementedError()
