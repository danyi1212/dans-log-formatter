import pytest

from formatter import JsonLogFormatter
from providers.context import ContextProvider, inject_log_context
from utils import logger_factory, read_stream_log_line


def test_custom_context():
    logger, stream = logger_factory(JsonLogFormatter([ContextProvider()]))

    with inject_log_context({"a": 1, "b": 2}):
        logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert record["a"] == 1
    assert record["b"] == 2


def test_custom_context_nested():
    logger, stream = logger_factory(JsonLogFormatter([ContextProvider()]))

    with inject_log_context({"a": 1}):
        with inject_log_context({"b": 2}):
            logger.info("inner")
        logger.info("outer")
    logger.info("outside")

    record1 = read_stream_log_line(stream)
    assert record1["message"] == "inner"
    assert record1["a"] == 1
    assert record1["b"] == 2

    record2 = read_stream_log_line(stream, seek=False)
    assert record2["message"] == "outer"
    assert record2["a"] == 1
    assert "b" not in record2

    record3 = read_stream_log_line(stream, seek=False)
    assert record3["message"] == "outside"
    assert "a" not in record3
    assert "b" not in record3


def test_custom_context_as_decorator():
    logger, stream = logger_factory(JsonLogFormatter([ContextProvider()]))

    @inject_log_context({"a": 1})
    def inner():
        logger.info("inner")

    inner()
    logger.info("outer")

    record1 = read_stream_log_line(stream)
    assert record1["message"] == "inner"
    assert record1["a"] == 1

    record2 = read_stream_log_line(stream, seek=False)
    assert record2["message"] == "outer"
    assert "a" not in record2


def test_custom_context_override():
    logger, stream = logger_factory(JsonLogFormatter([ContextProvider()]))

    with pytest.raises(AttributeError, match="a"):  # noqa SIM117
        with inject_log_context({"a": 1}):
            with inject_log_context({"a": 2}):
                logger.info("hello world!")


def test_custom_context_override_enable():
    logger, stream = logger_factory(JsonLogFormatter([ContextProvider()]))

    with inject_log_context({"a": 1}, override=True):  # noqa SIM117
        with inject_log_context({"a": 2}, override=True):
            logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert record["a"] == 2
