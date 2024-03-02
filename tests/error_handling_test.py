from logging import LogRecord

from formatter import JsonLogFormatter
from providers.abstract import AbstractProvider
from utils import logger_factory, read_stream_log_line


class ExceptionProvider(AbstractProvider):
    def get_attributes(self, record: LogRecord):  # noqa ARG002
        raise ValueError("Something went wrong")


class InternalErrorProvider(AbstractProvider):
    def get_attributes(self, record: LogRecord):  # noqa ARG002
        self.record_error("Something went wrong, but it's not an exception")
        return {"something": 123}


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
