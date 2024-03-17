from contextvars import ContextVar
from logging import LogRecord
from typing import Optional

from fastapi.routing import APIRoute
from starlette.requests import Request

from dans_log_formatter.providers.abstract_context import AbstractContextProvider

fastapi_request_context: ContextVar[Optional[Request]] = ContextVar("fastapi_log_context", default=None)


class FastAPIRequestProvider(AbstractContextProvider):
    def __init__(self):
        super().__init__(fastapi_request_context)

    def get_context_attributes(self, record: LogRecord, request: Request):  # noqa ARG002
        return {
            "resource": self.get_resource(request),
            "http.url": str(request.url),
            "http.method": request.method,
            "http.referrer": request.headers.get("referer"),
            "http.useragent": request.headers.get("user-agent"),
            "http.remote_addr": self.extract_remote_addr(request),
        }

    def get_resource(self, request: Request) -> str:
        route = request.scope.get("route")
        path = route.path_format if isinstance(route, APIRoute) else request.url.path
        return f"{request.method} {path}"

    def extract_remote_addr(self, request: Request) -> str:
        if forwarded := request.headers.get("x-forwarded-for"):
            return str(forwarded)
        elif request.client is not None:
            return str(request.client.host)
        else:
            return "unknown"
