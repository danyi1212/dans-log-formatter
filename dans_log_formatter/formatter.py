import json
import sys
from logging import Formatter, LogRecord
from typing import Literal, Mapping, Any

from dans_log_formatter.providers.abstract import AbstractProvider
from formatter_error import FormatterError

DEFAULT_MESSAGE_SIZE_LIMIT = 64 * 1024
DEFAULT_STACK_SIZE_LIMIT = 128 * 1024


# noinspection PyMethodMayBeStatic
class TextLogFormatter(Formatter):
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,  # noqa FBT001, FBT002
        providers: list[AbstractProvider] | None = None,
        *,
        defaults: Mapping[str, Any] | None = None,
        message_size_limit: int | None = DEFAULT_MESSAGE_SIZE_LIMIT,
        stack_size_limit: int | None = DEFAULT_STACK_SIZE_LIMIT,
    ):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        self.providers = providers or []
        self.message_size_limit = message_size_limit
        self.stack_size_limit = stack_size_limit
        self._formatter_errors: list[FormatterError] = []

    def get_providers(self, record: LogRecord) -> list[AbstractProvider]:  # noqa ARG002
        return self.providers

    def format(self, record: LogRecord) -> str:
        for attribute, value in self.get_attributes(record).items():
            if not hasattr(record, attribute):
                try:  # noqa SIM105
                    setattr(record, attribute, value)
                except AttributeError:
                    pass

        return super().format(record)

    def get_attributes(self, record: LogRecord) -> dict:
        result = {}
        for index, provider in enumerate(self.get_providers(record)):
            provider_data = self.get_provider_attributes(index, provider, record)
            if provider_data is not None:
                result.update(provider_data)

        result["timestamp"] = self.format_timestamp(record)
        result["status"] = self.format_status(record)
        result["message"] = self.format_message(record)
        result["location"] = self.format_location(record)
        result["file"] = self.format_file(record)

        if record.exc_info is not None:
            result["error"] = self.format_exception(record)

        if record.stack_info is not None:
            result["stack_info"] = self.format_stack(record)

        if self._formatter_errors:
            result["formatter_errors"] = self._get_formatter_errors()

        return result

    def format_timestamp(self, record: LogRecord):
        return self.formatTime(record)

    def format_status(self, record: LogRecord) -> str:
        return record.levelname

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

    def get_provider_attributes(self, index: int, provider: AbstractProvider, record: LogRecord) -> dict:
        try:
            provider_data = provider.get_attributes(record)
        except Exception as e:  # noqa BLE001
            self.record_error(f"Provider index {index} ({provider.__class__.__name__}) raised an exception: {e}")
        else:
            self._formatter_errors.extend(
                FormatterError(
                    f"Provider index {index} ({provider.__class__.__name__}): {error.message}",
                    error.exc_info,
                )
                for error in provider.get_errors()
            )
            return provider_data

    def record_error(self, message: str) -> None:
        self._formatter_errors.append(FormatterError(message, sys.exc_info()))

    def _get_formatter_errors(self) -> str:
        return self.truncate_string(
            "\n\n".join(
                f"{error.message}\n{self.formatException(error.exc_info)}" if error.exc_info else error.message
                for error in self._formatter_errors
            ),
            self.stack_size_limit,
        )


class JsonLogFormatter(TextLogFormatter):
    def __init__(
        self,
        providers: list[AbstractProvider] | None = None,
        *,
        message_size_limit: int | None = DEFAULT_MESSAGE_SIZE_LIMIT,
        stack_size_limit: int | None = DEFAULT_STACK_SIZE_LIMIT,
    ):
        super().__init__(providers=providers, message_size_limit=message_size_limit, stack_size_limit=stack_size_limit)

    def format(self, record: LogRecord) -> str:
        return json.dumps(self.get_attributes(record))

    def format_timestamp(self, record: LogRecord):
        return record.created
