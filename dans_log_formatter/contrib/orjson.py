from logging import LogRecord

import orjson

from dans_log_formatter.formatter import JsonLogFormatter


class OrJsonLogFormatter(JsonLogFormatter):
    def format(self, record: LogRecord) -> str:
        return str(orjson.dumps(self.get_attributes(record)), "utf-8")
