from dans_log_formatter.formatter import JsonLogFormatter
from formatter_test import DEFAULT_ATTRIBUTES
from dans_log_formatter.providers.extra import ExtraProvider
from tests.utils import logger_factory, read_stream_log_line


def test_extra_provider():
    logger, stream = logger_factory(JsonLogFormatter([ExtraProvider()]))
    logger.info("hello world!", extra={"extra": "value"})

    record = read_stream_log_line(stream)
    assert record.keys() == DEFAULT_ATTRIBUTES | {"extra"}
    assert record["extra"] == "value"
