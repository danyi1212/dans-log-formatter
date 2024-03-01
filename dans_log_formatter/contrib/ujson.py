from logging import LogRecord

import ujson

from formatter import JsonLogFormatter


class UJsonLogFormatter(JsonLogFormatter):
    def format(self, record: LogRecord) -> str:
        return ujson.dumps(self.get_attributes(record))
