import json
from logging import Formatter, LogRecord

from dans_log_formatter.providers.abstract import AbstractProvider


# noinspection PyMethodMayBeStatic
class JsonLogFormatter(Formatter):
    message_size_limit = 64 * 1024
    stack_size_limit = 128 * 1024

    providers: list[AbstractProvider]

    def __init__(self, providers: list[AbstractProvider] | None = None):
        super().__init__()
        self.providers = providers or []

    def get_providers(self, record: LogRecord) -> list[AbstractProvider]:  # noqa ARG002
        return self.providers

    def format(self, record: LogRecord) -> str:
        return json.dumps(self.get_attributes(record))

    def get_attributes(self, record: LogRecord) -> dict:
        result = {}
        for provider in self.get_providers(record):
            provider_data = provider.get_attributes(record)
            if provider_data is not None:
                result.update(provider_data)

        result["timestamp"] = self.format_timestamp(record)
        result["status"] = record.levelname
        result["message"] = self.format_message(record)
        result["location"] = self.format_location(record)
        result["file"] = self.format_file(record)
        result["thread"] = self.format_thread(record)
        result["process"] = self.format_process(record)
        result["task"] = self.format_task(record)

        if record.exc_info is not None:
            result["error"] = self.format_exception(record)

        if record.stack_info is not None:
            result["stack_info"] = self.format_stack(record)

        return result

    def format_timestamp(self, record: LogRecord):
        return record.created

    def format_message(self, record: LogRecord) -> str:
        return self.truncate_string(record.getMessage(), self.message_size_limit)

    def format_exception(self, record: LogRecord) -> str:
        return self.truncate_string(self.formatException(record.exc_info), self.stack_size_limit)

    def format_stack(self, record: LogRecord) -> str:
        return self.truncate_string(self.formatStack(record.stack_info), self.stack_size_limit)

    def truncate_string(self, string: str, limit: int | None) -> str:
        if limit is not None and len(string) > limit:
            return string[: limit - 14] + "...[TRUNCATED]"
        else:
            return string

    def format_location(self, record: LogRecord):
        return f"{record.module}-{record.funcName}#{record.lineno}"

    def format_file(self, record: LogRecord):
        return record.pathname

    def format_thread(self, record: LogRecord):
        return f"{record.threadName} ({record.thread})"

    def format_process(self, record: LogRecord):
        return f"{record.processName} ({record.process})"

    def format_task(self, record: LogRecord):
        return record.taskName
