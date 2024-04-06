# 这行代码是 Python 3.7+ 的特性，允许开发者在类型注解中使用尚未定义的类名。
# 从 Python 3.10 开始，这成为了默认行为。
# 这对于解决循环导入问题或在同一个文件中定义互相引用的类非常有用。
from __future__ import annotations

# 导入 Python 的 errno 模块，用于处理操作系统相关的错误码。
import errno
# 导入 Python 的 json 模块，用于处理 JSON 数据的编码和解码。
import json
# 导入 Python 的 os 模块，用于与操作系统交互，例如文件操作、环境变量等。
import os
# 导入 Python 的 types 模块，用于操作 Python 中的类型和类。
import types
# 导入 Python 的 typing 模块，并将其重命名为 t，以便在代码中使用类型提示。
import typing as t

# 从 Werkzeug 工具包中导入 import_string 函数，该函数用于根据字符串导入模块或对象。
from werkzeug.utils import import_string

# 用于检查是否在类型检查模式下执行代码，并在类型检查模式下导入模块。
if t.TYPE_CHECKING:
    import typing_extensions as te

    from .sansio.app import App

# 使用 TypeVar 类创建一个类型变量，名称为 "T"。
# 类型变量通常用于泛型编程中，表示可以是任何类型的占位符。
T = t.TypeVar("T")


# 一个泛型类，用于将属性委托给配置对象。
# 泛型类是一种具有泛型参数的类，其中泛型参数可以用来定义类中的属性、方法或方法参数的类型。
# 泛型类允许在类定义中使用未知类型，以便在实际使用时进行具体化。
# 在 Python 中，泛型类通常使用 typing 模块中的 TypeVar 和 Generic 类进行定义。
# TypeVar 用于声明类型变量，表示任意类型的占位符，而 Generic 类则表示泛型类的基类。
class ConfigAttribute(t.Generic[T]):
    """Makes an attribute forward to the config"""

    def __init__(
        # name 表示属性的名称，get_converter 是一个可选的回调函数，用于将配置值转换为指定类型。
        self, name: str, get_converter: t.Callable[[t.Any], T] | None = None
    ) -> None:
        # 将属性名称存储在 __name__ 属性中。
        self.__name__ = name
        # 将传入的转换器函数存储在 get_converter 属性中。
        self.get_converter = get_converter

    # @t.overload：使用 typing 模块中的 overload 装饰器进行函数重载。
    @t.overload
    def __get__(self, obj: None, owner: None) -> te.Self:
        ...

    @t.overload
    def __get__(self, obj: App, owner: type[App]) -> T:
        ...

    # 定义 __get__ 方法，用于获取属性值。它接受两个参数，obj 表示属性所属的对象
    #（例如 App 对象），owner 表示拥有属性的类。方法返回类型可以是 T 或 te.Self。
    def __get__(self, obj: App | None, owner: type[App] | None = None) -> T | te.Self:
        # 如果 obj 为 None，则返回 self，即返回 ConfigAttribute 实例本身。
        if obj is None:
            return self

        # 否则，从对象的配置中获取属性值 rv = obj.config[self.__name__]。
        rv = obj.config[self.__name__]

        # 如果存在转换器函数，则将属性值传递给转换器进行转换。
        if self.get_converter is not None:
            rv = self.get_converter(rv)

        return rv  # type: ignore[no-any-return]

    # 定义 __set__ 方法，用于设置属性值。它接受两个参数，obj 表示属性所属的对象，
    # value 表示要设置的值。该方法没有返回值，只是将值存储到对象的配置中。
    def __set__(self, obj: App, value: t.Any) -> None:
        obj.config[self.__name__] = value



















