from contextvars import ContextVar
from logging import LogRecord
from typing import Any, Optional

from django.http import HttpRequest
from django.urls import resolve, Resolver404

from dans_log_formatter.providers.abstract_context import AbstractContextProvider

django_request_context: ContextVar[Optional[HttpRequest]] = ContextVar("django_log_context", default=None)


class DjangoRequestProvider(AbstractContextProvider):
    def __init__(self):
        super().__init__(django_request_context)

    def get_context_attributes(self, record: LogRecord, request: HttpRequest) -> Optional[dict[str, Any]]:  # noqa ARG002
        result = {
            "resource": self.get_resource(request),
            "http.url": request.build_absolute_uri(),
            "http.method": request.method,
            "http.referrer": request.headers.get("referer"),
            "http.useragent": request.headers.get("user-agent"),
            "http.remote_addr": self.extract_remote_addr(request),
        }
        if user := getattr(request, "user", None):
            try:
                result["user.id"] = user.id if user.is_authenticated else 0
                result["user.name"] = str(user)
                result["user.email"] = getattr(user, "email", None)
            except Exception as e:  # noqa BLE001
                self.record_error(f"Failed to extract user attributes: {e}")

        return result

    def get_resource(self, request: HttpRequest) -> str:
        try:
            path = resolve(request.path_info).route
        except Resolver404:
            return f"{request.method} {request.path}"
        else:
            return f"{request.method} {path}"

    def extract_remote_addr(self, request: HttpRequest) -> str:
        if x_forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"):
            return str(x_forwarded_for)
        elif remote_addr := request.META.get("REMOTE_ADDR"):
            return str(remote_addr)
        else:
            return "unknown"
