from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.http import HttpRequest

from dans_log_formatter.contrib.django.provider import django_request_context


class LogContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        token = django_request_context.set(request)
        try:
            return self.get_response(request)
        finally:
            django_request_context.reset(token)


class AsyncLogContextMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request):
        token = django_request_context.set(request)
        try:
            return await self.get_response(request)
        finally:
            django_request_context.reset(token)
