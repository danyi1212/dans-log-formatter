from logging import LogRecord
from typing import Any

from flask import has_request_context, request

from providers.abstract import AbstractProvider


class FlaskRequestProvider(AbstractProvider):
    def get_attributes(self, record: LogRecord) -> None | dict[str, Any]:  # noqa ARG002
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
