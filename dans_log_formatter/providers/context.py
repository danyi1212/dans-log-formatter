from contextlib import contextmanager
from contextvars import ContextVar
from logging import LogRecord
from typing import Any, Optional

from dans_log_formatter.providers.abstract_context import AbstractContextProvider

_context: ContextVar[Optional[dict[str, Any]]] = ContextVar("custom_log_context", default=None)


class ContextProvider(AbstractContextProvider):
    """
    Inject custom context into the log record using with_log_context() decorator.
    Context example:
        with with_log_context(attribute="value"):
            logger.info("message")

    Decorator example:
        @with_log_context(attribute="value")
        def function():
            logger.info("message")
    """

    def __init__(self):
        super().__init__(_context)

    def get_context_attributes(self, record: LogRecord, context_value: dict[str, Any]):  # noqa ARG002
        return context_value


@contextmanager
def inject_log_context(attributes: dict[str, Any], /, *, override: bool = False):
    original_context = _context.get()
    if original_context is None:
        context = attributes
    else:
        context = original_context.copy()
        if not override and (existing_attributes := set(original_context).intersection(set(attributes))):
            raise AttributeError(f"Attributes {existing_attributes} already exist in the context")

        context.update(attributes)

    token = _context.set(context)
    try:
        yield None
    finally:
        _context.reset(token)
