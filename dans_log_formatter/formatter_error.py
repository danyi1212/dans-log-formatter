from types import TracebackType
from typing import NamedTuple, Type, Union

ExecInfo = tuple[Type[BaseException], BaseException, TracebackType]


class FormatterError(NamedTuple):
    message: str
    exc_info: Union[ExecInfo, tuple[None, None, None]] = (None, None, None)
