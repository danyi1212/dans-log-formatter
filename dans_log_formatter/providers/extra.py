from logging import LogRecord
from typing import Any, ClassVar

from providers.abstract import AbstractProvider


class ExtraProvider(AbstractProvider):
    builtin_attrs: ClassVar[set[str]] = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    }

    def extract_extra(self, record: LogRecord) -> dict:
        return {
            attr_name: record.__dict__[attr_name]
            for attr_name in record.__dict__
            if attr_name not in self.builtin_attrs
        }

    def get_attributes(self, record: LogRecord) -> None | dict[str, Any]:
        extra = self.extract_extra(record)
        if extra:
            return extra
