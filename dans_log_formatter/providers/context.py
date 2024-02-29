from contextlib import contextmanager
from contextvars import ContextVar
from logging import LogRecord
from typing import Any, ContextManager

from providers.abstract_context import AbstractContextProvider

_context: ContextVar[dict[str, Any] | None] = ContextVar("custom_log_context", default=None)


class ContextProvider(AbstractContextProvider):
    def __init__(self):
        super().__init__(_context)

    def format_context_fields(self, record: LogRecord, context_value: dict[str, Any]):  # noqa ARG002
        return context_value


@contextmanager
def with_log_context(**kwargs) -> ContextManager[None]:
    original_context = _context.get()
    if original_context is None:
        context = kwargs
    else:
        context = original_context.copy()
        context.update(kwargs)

    token = _context.set(context)
    try:
        yield None
    finally:
        _context.reset(token)
