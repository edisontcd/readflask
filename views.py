# 这行代码是 Python 3.7+ 的特性，允许开发者在类型注解中使用尚未定义的类名。
# 从 Python 3.10 开始，这成为了默认行为。
# 这对于解决循环导入问题或在同一个文件中定义互相引用的类非常有用。
from __future__ import annotations

# 提供了一套用于支持类型提示（Type Hints）的工具，这在 Python 3.5+ 中被引入。
import typing as t

from . import typing as ft
from .globals import current_app
from .globals import request

# t.TypeVar 创建一个类型变量，这在泛型编程中是常见的做法，允许你指定一个函数或类可以接受多种类型的参数。
# "F" 是类型变量的名称。
# bound=t.Callable[..., t.Any] 指定了类型变量 F 的上界，意味着 F 可以是任何类型的
# 调用对象（如函数、方法等），其参数和返回类型是任意的。
# 这里，... 表示函数可以接受任意数量和类型的参数，t.Any 表示函数可以返回任意类型的值。
F = t.TypeVar("F", bound=t.Callable[..., t.Any])

# 使用 frozenset 而不是普通的 set 是因为 frozenset 是不可变的，确保了集合在创建后不能被修改。
# 这在定义全局常量或确保某些数据结构在整个程序生命周期内保持不变时非常有用。
http_method_funcs = frozenset(
    ["get", "post", "head", "options", "delete", "put", "trace", "patch"]
)