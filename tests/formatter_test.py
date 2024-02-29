import os
import threading

from formatter import JsonLogFormatter
from providers.extra import ExtraProvider
from utils import logger_factory, read_stream_log_line

DEFAULT_ATTRIBUTES = {"timestamp", "status", "message", "location", "file", "thread", "process", "task"}


def test_formatter():
    logger, stream = logger_factory(JsonLogFormatter())

    logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert record.keys() == DEFAULT_ATTRIBUTES
    assert isinstance(record["timestamp"], float)
    assert record["status"] == "INFO"
    assert record["message"] == "hello world!"
    assert record["location"] == "formatter_test-test_formatter#14"
    assert record["file"] == __file__
    assert record["thread"] == f"MainThread ({threading.get_ident()})"
    assert record["process"] == f"MainProcess ({os.getpid()})"
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


def test_formatter_truncate_message():
    formatter = JsonLogFormatter()
    logger, stream = logger_factory(formatter)

    logger.info("hello world" + "*" * formatter.message_size_limit)

    record = read_stream_log_line(stream)
    assert len(record["message"]) == formatter.message_size_limit
    assert record["message"].startswith("hello world")
    assert record["message"].endswith("...[TRUNCATED]")


def test_formatter_disable_truncate_message():
    formatter = JsonLogFormatter()
    formatter.message_size_limit = None
    logger, stream = logger_factory(formatter)

    logger.info("*" * 100_000)

    record = read_stream_log_line(stream)
    assert len(record["message"]) == 100_000
    assert not record["message"].endswith("...[TRUNCATED]")


def test_formatter_not_truncate_message():
    formatter = JsonLogFormatter()
    logger, stream = logger_factory(formatter)

    logger.info("*" * formatter.message_size_limit)

    record = read_stream_log_line(stream)
    assert len(record["message"]) == formatter.message_size_limit
    assert not record["message"].endswith("...[TRUNCATED]")


def test_formatter_truncate_stack_info():
    formatter = JsonLogFormatter()
    formatter.formatStack = lambda _: "hello world" + "*" * formatter.stack_size_limit
    logger, stream = logger_factory(formatter)

    logger.info("hello world!", stack_info=True)

    record = read_stream_log_line(stream)
    assert len(record["stack_info"]) == formatter.stack_size_limit
    assert record["stack_info"].startswith("hello world")
    assert record["stack_info"].endswith("...[TRUNCATED]")


def test_formatter_truncate_exception():
    formatter = JsonLogFormatter()
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


def test_formatter_with_thread():
    logger, stream = logger_factory(JsonLogFormatter())

    thread = threading.Thread(
        name="MyThread",
        target=lambda: logger.info("hello world!"),
    )
    thread.start()
    thread.join()

    record = read_stream_log_line(stream)
    assert record["thread"] == f"MyThread ({thread.ident})"


def test_formatter_with_extra():
    logger, stream = logger_factory(JsonLogFormatter([ExtraProvider()]))
    logger.info("hello world!", extra={"extra": "value"})

    record = read_stream_log_line(stream)
    assert record.keys() == DEFAULT_ATTRIBUTES | {"extra"}
    assert record["extra"] == "value"


def test_formatter_with_extra_no_override():
    logger, stream = logger_factory(JsonLogFormatter([ExtraProvider()]))
    logger.info("hello world!", extra={"status": "value"})

    record = read_stream_log_line(stream)
    assert record.keys() == DEFAULT_ATTRIBUTES
    assert record["status"] == "INFO"
