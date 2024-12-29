from typing import Any

from ..elements.base_object import BaseObject

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

class Code(BaseObject):
    def __init__(self, code: str):
        super().__init__()
        self.code = code
        self.DEFINE_LEVEL = 0
        self.BRACKET_LEVEL = 0
        self.lines: list[str] = []
        self.process_code()
        self.op: str = ""

    def process_code(self) -> None:
        for char in self.code:
            if char == "{":
                self.DEFINE_LEVEL += 1
            elif char == "}":
                self.DEFINE_LEVEL -= 1
            elif char == "(":
                self.BRACKET_LEVEL += 1
            elif char == ")":
                self.BRACKET_LEVEL -= 1
            elif char in OPS:
                self.op = char

        if self.DEFINE_LEVEL != 0 or self.BRACKET_LEVEL != 0:
            msg = "Mismatched parentheses."
            raise ValueError(msg)

        self.lines = [item.strip() for item in self.code.split("\n") if item.strip()]

    def get_lines(self) -> list[str]:
        return self.lines


class Frame(BaseObject):
    def __init__(self, code: Code):
        super().__init__()
        self.code = code
        self.local_vars: dict[str, Any] = {}
        self.return_value: Any = None

    def set_var(self, name: str, value: Any) -> None:
        self.local_vars[name] = value

    def get_var(self, name: str) -> Any:
        return self.local_vars.get(name)

    def set_return_value(self, value: Any) -> None:
        self.return_value = value

    def get_return_value(self) -> Any:
        return self.return_value


class Stack(BaseObject):
    def __init__(self):
        super().__init__()
        self.frames: list[Frame] = []

    def push_frame(self, frame: Frame) -> None:
        self.frames.append(frame)

    def pop_frame(self) -> Frame:
        if not self.frames:
            raise IndexError("pop from empty stack")
        return self.frames.pop()

    def current_frame(self) -> Frame:
        if not self.frames:
            raise IndexError("current frame from empty stack")
        return self.frames[-1]

    def is_empty(self) -> bool:
        return len(self.frames) == 0


if __name__ == "__main__":
    # 示例代码
    code_str = """*"""

    code_obj = Code(code_str)
    code_obj.process_code()

    stack = Stack()

    frame = Frame(code_obj)
    stack.push_frame(frame)

    frame.set_var("a", 114514)
    frame.set_var("b", 1919810)

    if code_obj.op in OPS:
        operation = OPS[code_obj.op]
        frame.set_return_value(operation(frame.get_var("a"), frame.get_var("b")))
    else:
        raise ValueError(f"Unsupported operation: {code_obj.op}")

    print(frame.get_return_value())

    # 弹出栈帧
    stack.pop_frame()
