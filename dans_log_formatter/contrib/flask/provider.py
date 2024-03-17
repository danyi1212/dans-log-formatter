from logging import LogRecord
from typing import Any, Optional

from flask import has_request_context, request

from dans_log_formatter.providers.abstract import AbstractProvider


class FlaskRequestProvider(AbstractProvider):
    def get_attributes(self, record: LogRecord) -> Optional[dict[str, Any]]:  # noqa ARG002
        if not has_request_context():
            return None

        return {
            "resource": f"{request.method} {request.path}",
            "http.url": request.url,
            "http.method": request.method,
            "http.referrer": request.referrer,
            "http.useragent": request.user_agent.string,
            "http.remote_addr": request.remote_addr,
        }
