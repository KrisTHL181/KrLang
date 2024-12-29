from __future__ import annotations

from ..elements.base_object import BaseObject


class Number(BaseObject):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value
        self._init_meta()

    def _init_meta(self) -> None:
        self._set_meta("add", self.__add__)
        self._set_meta("subtract", self.__sub__)
        self._set_meta("multiply", self.__mul__)
        self._set_meta("divide", self.__truediv__)

    def __add__(self, other: Number) -> Number:
        return Number(self.value + other.value)

    def __sub__(self, other: Number) -> Number:
        return Number(self.value - other.value)

    def __mul__(self, other: Number) -> Number:
        return Number(self.value * other.value)

    def __truediv__(self, other: Number) -> Number:
        if other.value == 0:
            msg = "Cannot divide by zero."
            raise ValueError(msg)
        return Number(self.value / other.value)
