from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from dans_log_formatter.contrib.fastapi.provider import fastapi_request_context


class LogContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = fastapi_request_context.set(request)
        try:
            return await call_next(request)
        finally:
            fastapi_request_context.reset(token)
