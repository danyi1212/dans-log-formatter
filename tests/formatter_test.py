from datetime import datetime
import logging.config
from io import StringIO

from dans_log_formatter.formatter import JsonLogFormatter, TextLogFormatter
from dans_log_formatter.providers.context import ContextProvider, inject_log_context
from dans_log_formatter.providers.extra import ExtraProvider
from tests.utils import logger_factory, read_stream_log_line

DEFAULT_ATTRIBUTES = {"timestamp", "status", "message", "location", "file"}


def test_formatter():
    logger, stream = logger_factory(JsonLogFormatter())

    logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert record.keys() == DEFAULT_ATTRIBUTES
    assert datetime.fromisoformat(record["timestamp"])
    assert record["status"] == "INFO"
    assert record["message"] == "hello world!"
    assert record["location"] == "formatter_test-test_formatter#16"
    assert record["file"] == __file__
    assert stream.readline() == ""


def test_formatter_with_exception():
    logger, stream = logger_factory(JsonLogFormatter())

    try:
        raise ValueError("error")
    except ValueError:
        logger.exception("hello world!")

    record = read_stream_log_line(stream)
    assert "ValueError: error" in record["error"]


def test_formatter_with_stack_info():
    logger, stream = logger_factory(JsonLogFormatter())

    logger.info("hello world!", stack_info=True)

    record = read_stream_log_line(stream)
    assert "test_formatter_with_stack_info" in record["stack_info"]


def test_truncate_message():
    formatter = JsonLogFormatter()
    assert formatter.message_size_limit is not None

    logger, stream = logger_factory(formatter)

    logger.info("hello world" + "*" * formatter.message_size_limit)

    record = read_stream_log_line(stream)
    assert len(record["message"]) == formatter.message_size_limit
    assert record["message"].startswith("hello world")
    assert record["message"].endswith("...[TRUNCATED]")
    assert "'message' value is too long" in record["formatter_errors"]


def test_disable_truncate_message():
    formatter = JsonLogFormatter(message_size_limit=None)
    logger, stream = logger_factory(formatter)

    logger.info("*" * 100_000)

    record = read_stream_log_line(stream)
    assert len(record["message"]) == 100_000
    assert not record["message"].endswith("...[TRUNCATED]")
    assert "formatter_errors" not in record


def test_not_truncate_message():
    formatter = JsonLogFormatter(message_size_limit=100)
    assert formatter.message_size_limit is not None
    logger, stream = logger_factory(formatter)

    logger.info("*" * formatter.message_size_limit)

    record = read_stream_log_line(stream)
    assert len(record["message"]) == formatter.message_size_limit
    assert not record["message"].endswith("...[TRUNCATED]")
    assert "formatter_errors" not in record


def test_truncate_stack_info():
    formatter = JsonLogFormatter(stack_size_limit=100)
    formatter.formatStack = lambda _: "hello world" + "*" * formatter.stack_size_limit  # type: ignore
    logger, stream = logger_factory(formatter)

    logger.info("hello world!", stack_info=True)

    record = read_stream_log_line(stream)
    assert len(record["stack_info"]) == formatter.stack_size_limit
    assert record["stack_info"].startswith("hello world")
    assert record["stack_info"].endswith("...[TRUNCATED]")
    assert "'stack_info' value is too long" in record["formatter_errors"]


def test_truncate_exception():
    formatter = JsonLogFormatter(stack_size_limit=300)
    assert formatter.stack_size_limit is not None
    logger, stream = logger_factory(formatter)

    try:
        raise ValueError("hello world" + "*" * formatter.stack_size_limit)
    except ValueError:
        logger.exception("hello world!")

    record = read_stream_log_line(stream)
    assert len(record["error"]) == formatter.stack_size_limit
    assert record["error"].startswith("Traceback (most recent call last):")
    assert "ValueError: hello world" in record["error"]
    assert record["error"].endswith("...[TRUNCATED]")
    assert "'error' value is too long" in record["formatter_errors"]


def test_provider_cannot_override_attributes():
    logger, stream = logger_factory(JsonLogFormatter([ExtraProvider()]))
    logger.info("hello world!", extra={"status": "value"})

    record = read_stream_log_line(stream)
    assert record.keys() == DEFAULT_ATTRIBUTES
    assert record["status"] == "INFO"


def test_provider_order_attribute_override():
    logger, stream = logger_factory(
        JsonLogFormatter(
            [
                ContextProvider(),
                ExtraProvider(),
            ]
        )
    )
    with inject_log_context({"a": 1, "b": 2, "status": "value"}):
        logger.info("hello world!", extra={"b": "override", "c": 3, "status": "override"})

    record = read_stream_log_line(stream)
    assert record.keys() == DEFAULT_ATTRIBUTES | {"a", "b", "c"}
    assert record["a"] == 1
    assert record["b"] == "override"
    assert record["c"] == 3
    assert record["status"] == "INFO"


def test_text_formatter():
    logger, stream = logger_factory(
        TextLogFormatter(
            "{levelname} - {location}, {status} | {message}",
            style="{",
            providers=[ExtraProvider()],
        )
    )

    logger.info("hello world!", extra={"status": "extra value"})

    stream.seek(0)
    record = stream.readline()
    assert record == "INFO - formatter_test-test_text_formatter#159, extra value | hello world!\n"
    assert stream.readline() == ""


def test_logging_dict_config():
    stream = StringIO()
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "json": {
                    "()": "dans_log_formatter.JsonLogFormatter",
                    "providers": [
                        ContextProvider(),
                    ],
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": stream,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            },
        }
    )
    logger = logging.getLogger("test")

    with inject_log_context({"context": "something"}):
        logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert record.keys() == DEFAULT_ATTRIBUTES | {"context"}
    assert datetime.fromisoformat(record["timestamp"])
    assert record["status"] == "INFO"
    assert record["message"] == "hello world!"
    assert record["context"] == "something"
