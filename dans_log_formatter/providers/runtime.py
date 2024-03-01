from logging import LogRecord
from typing import Any

from providers.abstract import AbstractProvider


class RuntimeProvider(AbstractProvider):
    """
    Add runtime information about thread, process and asyncio task to the log record.
    """

    def get_attributes(self, record: LogRecord) -> None | dict[str, Any]:
        result = {}
        if record.process is not None:
            result["process"] = f"{record.processName} ({record.process})"

        if record.thread is not None:
            result["thread"] = f"{record.threadName} ({record.thread})"

        if (task_name := getattr(record, "taskName", None)) is not None:
            result["task"] = task_name

        return result if result else None
