import json
import logging
from io import StringIO
from typing import TextIO
from uuid import uuid4


def logger_factory(formatter: logging.Formatter) -> tuple[logging.Logger, StringIO]:
    logger = logging.getLogger(str(uuid4()))
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger, stream


def read_stream_log_line(stream: TextIO, *, seek: bool = True) -> dict:
    if seek:
        stream.seek(0)
    line = stream.readline()
    return json.loads(line)
