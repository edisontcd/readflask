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