from types import TracebackType
from typing import NamedTuple, Type

ExecInfo = tuple[Type[BaseException], BaseException, TracebackType]


class FormatterError(NamedTuple):
    message: str
    exc_info: ExecInfo | tuple[None, None, None] = (None, None, None)
