from types import TracebackType
from typing import NamedTuple, Type


class FormatterError(NamedTuple):
    message: str
    exc_info: tuple[Type[BaseException], BaseException, TracebackType] | tuple[None, None, None] = (None, None, None)
