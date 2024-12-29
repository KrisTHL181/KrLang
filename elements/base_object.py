"""对于KrLang的基本对象元素实现."""

from collections.abc import Callable
from typing import Any


class BaseObject:
    """对于KrLang的基本元素: 对象."""

    __slots__ = [
        "_interceptables",
        "_members",
        "_meta",
        "_weavings",
        "_wrappers",
    ]

    def __init__(self, *args: Any) -> None:
        """初始化对象, 并调用on_init包装器.

        Args:
            *args: 可变参数, 传递给on_init包装器.

        """
        self._members = {}
        self._wrappers = {}
        self._meta = {}
        self._interceptables = []
        self._weavings: dict[str, tuple[Callable, Callable]] = {}
        self._call_wrappers("on_init", *args)

    def __getitem__(self, key: str) -> Any:
        """通过键获取成员属性值.

        Args:
            key (str): 成员属性的键.

        Returns:
            Any: 成员属性的值.

        """
        return self._get_member(key)

    def __setitem__(self, key: str, value: Any) -> Any:
        """通过键设置成员属性值.

        Args:
            key (str): 成员属性的键.
            value (Any): 成员属性的新值.

        Returns:
            Any: 成员属性的新值.

        """
        return self._set_member(key, value)

    def __delitem__(self, key: str) -> None:
        """通过键删除成员属性.

        Args:
            key (str): 成员属性的键.

        """
        self._remove_member(key)

    def __delattr__(self, key: str) -> None:
        """通过属性名删除成员属性.

        Args:
            key (str): 成员属性的名字.

        """
        self._remove_member(key)

    def __setattr__(self, key: str, value: Any) -> None:
        """设置对象属性.

        如果属性名以'_'开头, 则使用基类的setattr方法.
        否则, 调用before_set_{key}和after_set_{key}包装器, 并设置成员属性.

        Args:
            key (str): 属性名.
            value (Any): 属性值.

        Raises:
            AttributeError: 如果尝试将属性设置为自身.

        """
        if value is self:
            msg = f"Cannot set attribute '{key}' to itself."
            raise AttributeError(msg)
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self._call_wrappers(f"before_set_{key}", key, value)
            self._set_member(key, value)
            self._call_wrappers(f"after_set_{key}", key, value)

    def __getattr__(self, key: str) -> Any:
        """获取对象属性.

        如果属性名在成员属性中, 则调用before_get和after_get包装器, 并返回成员属性值.
        否则, 使用基类的getattr方法.

        Args:
            key (str): 属性名.

        Returns:
            Any: 属性值.

        Raises:
            AttributeError: 如果属性不存在.

        """
        if key in super().__getattribute__("_members"):
            self._call_wrappers(f"before_get_{key}", key)
            value = self._get_member(key)
            self._call_wrappers(f"after_get_{key}", key, value)

            return value
        try:
            return super().__getattribute__(key)
        except AttributeError as err:
            msg = f"'{self.__class__.__name__}' object has no attribute '{key}'"
            raise AttributeError(msg) from err

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """调用成员属性内的call方法, 并转换为Python Callable对象.

        to_py_callable, 在CallableObject内实现或直接调用已实现的python函数.

        Args:
            *args: 可变参数, 传递给call方法.
            **kwargs: 可变关键字参数, 传递给call方法.

        Returns:
            Any: call方法的返回值.

        Raises:
            TypeError: 如果对象不可调用.

        """
        if self._has_member("call"):
            caller = self._get_member("call")
            if caller.has_meta("to_py_callable"):
                return caller._get_meta("to_py_callable")(
                    *args,
                    **kwargs,
                )
            if callable(caller):
                return caller(*args, **kwargs)
        elif hasattr(self, "call"):
            if callable(self.call):
                return self.call(*args, **kwargs)

        msg = f"'{self.__class__.__name__}' object is not callable"
        raise TypeError(msg)

    def __repr__(self) -> str:
        """返回该对象的成员属性映射(name=value).

        Returns:
            str: 对象的字符串表示.

        """
        return f"{self.__class__.__name__}\
({', '.join(f'{k}={v!r}' for k, v in self._members.items())})"

    def _call_wrappers(self, wrapper_type: str, *args: Any, **kwargs: Any) -> None:
        """调用指定类型的所有包装器.

        Args:
            wrapper_type (str): 包装器类型.
            *args: 传递给包装器的可变参数.
            **kwargs: 传递给包装器的可变关键字参数.

        """
        if wrapper_type in self._wrappers:
            for wrapper in self._wrappers[wrapper_type]:
                wrapper(*args, **kwargs)

    def _add_wrapper(self, wrapper_type: str, wrapper: Callable) -> None:
        """添加一个包装器到指定类型.

        Args:
            wrapper_type (str): 包装器类型.
            wrapper (Callable): 包装器函数.

        """
        if wrapper_type not in self._wrappers:
            self._wrappers[wrapper_type] = []
        self._wrappers[wrapper_type].append(wrapper)

    def _remove_wrapper(self, wrapper_type: str, wrapper: Callable) -> None:
        """从指定类型中移除一个包装器.

        Args:
            wrapper_type (str): 包装器类型.
            wrapper (Callable): 包装器函数.

        """
        if wrapper_type in self._wrappers:
            self._wrappers[wrapper_type].remove(wrapper)

    def _get_member(self, key: str) -> Any:
        """获取成员属性值.

        Args:
            key (str): 成员属性的键.

        Returns:
            Any: 成员属性的值.

        Raises:
            AttributeError: 如果成员属性不存在.

        """
        if key in self._members:
            self._call_wrappers(f"before_get_{key}", key)
            attr = self._members[key]
            self._call_wrappers(f"after_get_{key}", key, attr)
            if self._is_interceptable(key) and callable(attr):

                def wrapped(*args: Any, **kwargs: Any) -> Any:
                    self._call_weaving(self._get_weaving(key), *args, **kwargs)
                    result = attr(*args, **kwargs)
                    self._call_weaving(self._get_weaving(key), *args, **kwargs)
                    return result

                return wrapped
            return attr

        msg = f"'{self.__class__.__name__}' object has no member '{key}'"
        raise AttributeError(
            msg,
        )

    def _set_member(self, key: str, value: Any) -> None:
        """设置成员属性值.

        Args:
            key (str): 成员属性的键.
            value (Any): 成员属性的新值.

        """
        self._call_wrappers(f"before_set_{key}", key, value)
        self._members[key] = value
        self._call_wrappers(f"after_set_{key}", key, value)

    def _remove_member(self, key: str) -> None:
        """删除成员属性.

        Args:
            key (str): 成员属性的键.

        Raises:
            AttributeError: 如果成员属性不存在.

        """
        if key in self._members:
            self._call_wrappers(f"before_del_{key}", key)
            del self._members[key]
            self._call_wrappers(f"after_del_{key}", key)
            if key in self._interceptables:
                self._interceptables.remove(key)
        else:
            msg = f"'{self.__class__.__name__}' object has no member '{key}'"
            raise AttributeError(
                msg,
            )

    def _has_member(self, key: str) -> bool:
        """检查成员属性是否存在.

        Args:
            key (str): 成员属性的键.

        Returns:
            bool: 如果成员属性存在, 则返回True.

        """
        return key in self._members

    def _get_meta(self, key: str, default: Any = None) -> Any:
        """获取元属性值.

        Args:
            key (str): 元属性的键.
            default (Any, optional): 如果键不存在时返回的默认值.默认为None.

        Returns:
            Any: 元属性的值.

        Raises:
            AttributeError: 如果元属性不存在且未提供默认值.

        """
        if key in self._meta:
            return self._meta[key]
        if default is not None:
            return default
        msg = f"'{self.__class__.__name__}' object has no meta attribute '{key}'"
        raise AttributeError(
            msg,
        )

    def _set_meta(self, key: str, value: Any) -> None:
        """设置元属性值.

        Args:
            key (str): 元属性的键.
            value (Any): 元属性的新值.

        """
        self._meta[key] = value

    def _remove_meta(self, key: str) -> None:
        """删除元属性.

        Args:
            key (str): 元属性的键.

        Raises:
            AttributeError: 如果元属性不存在.

        """
        if key in self._meta:
            del self._meta[key]
        else:
            msg = f"'{self.__class__.__name__}' object has no meta attribute '{key}'"
            raise AttributeError(
                msg,
            )

    def _has_meta(self, key: str) -> bool:
        """检查元属性是否存在.

        Args:
            key (str): 元属性的键.

        Returns:
            bool: 如果元属性存在, 则返回True.

        """
        return key in self._meta

    def _reset(self) -> None:
        """重置对象状态, 清空成员属性、包装器和元属性, 并调用on_reset包装器."""
        self._call_wrappers("on_reset")
        self._members.clear()
        self._wrappers.clear()
        self._meta.clear()
        self._interceptables.clear()
        self._weavings.clear()

    def _is_interceptable(self, key: str) -> bool:
        """检查成员属性是否可拦截.

        Args:
            key (str): 成员属性的键.

        Returns:
            bool: 如果成员属性可拦截, 则返回True.

        """
        return (
            key in self._members
            and callable(self._members[key])
            and key in self._interceptables
        )

    def _set_interceptable(self, key: str) -> None:
        """设置成员属性为可拦截.

        Args:
            key (str): 成员属性的键.

        """
        if key in self._members and callable(self._members[key]):
            self._interceptables.append(key)

    def _unset_interceptable(self, key: str) -> None:
        """取消成员属性的可拦截状态.

        Args:
            key (str): 成员属性的键.

        """
        if key in self._interceptables:
            self._interceptables.remove(key)

    def _call_weaving(
        self,
        weaving: list[tuple[Callable, Callable]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """调用指定的编织函数.

        Args:
            weaving (List[Tuple[Callable, Callable]]): 织入的函数列表.
            *args: 传递给编织函数的可变参数.
            **kwargs: 传递给编织函数的可变关键字参数.

        """
        for before, after in weaving:
            before(*args, **kwargs)
            after(*args, **kwargs)

    def _get_weaving(self, key: str) -> list[tuple[Callable, Callable]]:
        """获取指定成员属性的编织函数.

        Args:
            key (str): 成员属性的键.

        Returns:
            List[Tuple[Callable, Callable]]: 织入的函数列表, 左边为执行前调用, 右边为执行后调用.

        """

    def _add_weaving(self, key: str, before: Callable, after: Callable) -> None:
        """为指定成员属性添加编织函数.

        Args:
            key (str): 成员属性的键.
            before (Callable): 调用成员属性之前执行的函数.
            after (Callable): 调用成员属性之后执行的函数.

        """
        if key not in self._weavings:
            self._weavings[key] = []

        self._weavings[key].append((before, after))

    def _remove_weaving(self, key: str, side: str) -> None:
        """从指定成员属性移除编织函数.

        Args:
            key (str): 成员属性的键.
            before (Callable): 调用成员属性之前执行的函数.
            after (Callable): 调用成员属性之后执行的函数.

        """
        if side == "all":
            del self._weavings[key]
            return
        if side in {"left", "right"}:
            if key in self._weavings:
                del self._weavings[key][0 if side == "left" else 1]
                return
            msg = f"Key '{key}' not found in _weavings."
            raise KeyError(msg)
        msg = f"Invalid side '{side}'. Expected 'left', 'right', or 'all'."
        raise ValueError(msg)

    def _reload_weaving(self, key: str, side: str, method: Callable) -> None:
        if side in {"left", "right"}:
            if key in self._weavings:
                self._weavings[key][0 if side == "left" else 1] = method
                return
            msg = f"Key '{key}' not found in _weavings."
            raise KeyError(msg)
        msg = f"Invalid side '{side}'. Expected 'left' or 'right'."
        raise ValueError(msg)
