from logging import LogRecord

from dans_log_formatter.formatter import JsonLogFormatter, DEFAULT_STACK_SIZE_LIMIT
from dans_log_formatter.providers.abstract import AbstractProvider
from tests.utils import logger_factory, read_stream_log_line


class ExceptionProvider(AbstractProvider):
    def get_attributes(self, record: LogRecord):  # noqa ARG002
        raise ValueError("Something went wrong")


class InternalErrorProvider(AbstractProvider):
    def get_attributes(self, record: LogRecord):  # noqa ARG002
        self.record_error("Something went wrong, but it's not an exception")
        return {"something": 123}


class LongExceptionProvider(AbstractProvider):
    def get_attributes(self, record: LogRecord):  # noqa ARG002
        raise ValueError("Something went wrong" + "*" * DEFAULT_STACK_SIZE_LIMIT)


def test_provider_exception():
    logger, stream = logger_factory(JsonLogFormatter([ExceptionProvider()]))

    logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert ExceptionProvider.__name__ in record["formatter_errors"]
    assert "ValueError: Something went wrong" in record["formatter_errors"]
    assert record["message"] == "hello world!"
    assert record["status"] == "INFO"


def test_provider_internal_error():
    logger, stream = logger_factory(JsonLogFormatter([InternalErrorProvider()]))

    logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert InternalErrorProvider.__name__ in record["formatter_errors"]
    assert "Something went wrong, but it's not an exception" in record["formatter_errors"]
    assert record["message"] == "hello world!"
    assert record["status"] == "INFO"
    assert record["something"] == 123


def test_provider_truncate_error_message():
    formatter = JsonLogFormatter([LongExceptionProvider()])
    logger, stream = logger_factory(formatter)

    logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert len(record["formatter_errors"]) == formatter.stack_size_limit
    assert record["formatter_errors"].startswith("Provider index 0 (LongExceptionProvider) raised an exception: ")
    assert "Something went wrong" in record["formatter_errors"]
    assert record["formatter_errors"].endswith("...[TRUNCATED]")
    assert record["message"] == "hello world!"
    assert record["status"] == "INFO"
