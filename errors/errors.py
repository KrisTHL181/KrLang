from __future__ import annotations

from .base_exception import BaseException, Exception


def _new_error(name: str) -> type:
    return type(name, (Exception,), {})


def _new_base_error(name: str, with_msg: bool = False) -> type:
    return type(
        name,
        (BaseException,),
        (
            {
                "__init__": lambda self, msg=None: BaseException.__init__(
                    self,
                    err_string=msg if with_msg else None,
                ),
            }
        ),
    )


SyntaxError = _new_base_error("SyntaxError")
