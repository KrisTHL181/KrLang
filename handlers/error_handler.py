"""KrLang的异常处理机制."""

import os
import sys

from ..errors.base_exception import BaseException as KrLangBaseException
from ..errors.errors import TypeError as KrLangTypeError
from ..interpreter.interpreter import interpreter


def throw(error: KrLangBaseException) -> None:
    """抛出一个异常."""
    if not isinstance(error, KrLangBaseException):
        _error(KrLangTypeError("Exceptions must derive from BaseException"))
    _error(error)


def _error(error: KrLangBaseException) -> None:
    sys.stderr.write(
        f"ERROR! ({interpreter.file}[{interpreter.line}<{interpreter.calling_name}>]){error.err_type}: {error.err_string}",
    )
    if not error.recoverable:
        os._exit(1)
