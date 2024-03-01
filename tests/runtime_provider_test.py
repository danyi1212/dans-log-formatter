import asyncio
import os
import threading

from formatter import JsonLogFormatter
from providers.runtime import RuntimeProvider
from utils import logger_factory, read_stream_log_line


def test_runtime_provider():
    logger, stream = logger_factory(JsonLogFormatter([RuntimeProvider()]))

    logger.info("hello world!")

    record = read_stream_log_line(stream)
    assert record["thread"] == f"MainThread ({threading.get_ident()})"
    assert record["process"] == f"MainProcess ({os.getpid()})"


def test_runtime_provider_in_thread():
    logger, stream = logger_factory(JsonLogFormatter([RuntimeProvider()]))

    thread = threading.Thread(
        name="MyThread",
        target=lambda: logger.info("hello world!"),
    )
    thread.start()
    thread.join()

    record = read_stream_log_line(stream)
    assert record["thread"] == f"MyThread ({thread.ident})"


def test_runtime_provider_in_task():
    logger, stream = logger_factory(JsonLogFormatter([RuntimeProvider()]))

    async def run():
        logger.info("hello world!")

    async def main():
        await asyncio.create_task(run(), name="MyTask")

    asyncio.run(main())
    record = read_stream_log_line(stream)
    assert record["task"] == "MyTask"
