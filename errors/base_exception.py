from ..elements import BaseObject
from ..interpreter import interpreter


class BaseException(BaseObject):
    def __init__(
        self,
        err_type: str | None = None,
        err_string: str | None = None,
    ) -> None:
        """所有异常的基础类型. 对于用户自定义的非致命异常, 应该使用Exception.

        参数:
            args (tuple): 包括err_type(str)和err_string(str)的元组.
        """
        super().__init__()
        if err_type is None:
            err_type = self.__class__.__name__
        self.content = interpreter.get_content(interpreter.get_current_frame(), 3)
        self.err_type, self.err_string = err_type, err_string
        self.recoverable = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.err_type}: {self.err_string})"


class Exception(BaseException):
    def __init__(self, err_string: str | None = None) -> None:
        """非致命性异常的基础类型.

        参数:
            err_string (str): 打印异常栈时输出的文本.
        """
        super().__init__(self.__class__.__name__, err_string)
        self.recoverable = True
