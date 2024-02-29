import json
import logging
from io import StringIO
from typing import TextIO


def logger_factory(formatter: logging.Formatter) -> (logging.Logger, StringIO):
    logger = logging.getLogger("tests")
    logger.setLevel(logging.DEBUG)
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger, stream


def read_stream_log_line(stream: TextIO) -> dict:
    stream.seek(0)
    line = stream.readline()
    return json.loads(line)
