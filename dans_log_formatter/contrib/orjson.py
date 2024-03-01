from logging import LogRecord

import orjson

from formatter import JsonLogFormatter


class OrJsonLogFormatter(JsonLogFormatter):
    def format(self, record: LogRecord) -> str:
        return str(orjson.dumps(self.get_attributes(record)), "utf-8")
