import logging
import timeit

import pytest

from contrib.orjson import OrJsonLogFormatter
from contrib.ujson import UJsonLogFormatter
from formatter import JsonLogFormatter
from utils import logger_factory

EXECUTION_COUNT = 1_000


@pytest.mark.parametrize(
    "formatter",
    [
        pytest.param(JsonLogFormatter(), id="json"),
        pytest.param(UJsonLogFormatter(), id="ujson"),
        pytest.param(OrJsonLogFormatter(), id="orjson"),
    ],
)
def test_formatter_performance(formatter: logging.Formatter):
    logger, stream = logger_factory(formatter)

    execution_time = timeit.timeit(lambda: logger.info("hello world!"), number=EXECUTION_COUNT)

    assert execution_time < 0.01


@pytest.mark.xfail()
def test_formatter_faster_than_vanilla():
    formatter = JsonLogFormatter()
    logger, stream = logger_factory(formatter)

    vanilla_formatter = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d] %(levelname)s - %(name)s:%(lineno)d | %(message)s",
        datefmt="%H:%M:%S",
    )
    vanilla_logger, vanilla_stream = logger_factory(vanilla_formatter)

    execution_time = timeit.timeit(lambda: logger.info("hello world!"), number=EXECUTION_COUNT)
    vanilla_execution_time = timeit.timeit(lambda: vanilla_logger.info("hello world!"), number=EXECUTION_COUNT)

    stream.seek(0)
    vanilla_stream.seek(0)
    assert len(stream.readlines()) == len(vanilla_stream.readlines())
    assert execution_time < vanilla_execution_time * 1.1  # Up to 10% slower
