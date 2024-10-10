from __future__ import annotations

# 用于动态加载模块。
import importlib.util
# 提供与操作系统交互的函数，如文件路径操作。
import os
# 提供面向对象的文件系统路径操作方式，常用于代替 os.path。
import pathlib
# 与 Python 解释器进行交互，比如访问命令行参数、模块、路径等。
import sys
# 引入 typing 模块，用于类型注解，重命名为 t 方便简写。
import typing as t
# 来自 collections 模块，是一种字典类型，支持为每个键提供默认值。
from collections import defaultdict
# 用于更新一个函数的包装器（如装饰器），使其保留原函数的元数据（如名称和文档字符串）。
from functools import update_wrapper

# jinja2 模板引擎的基类，用于加载模板。
from jinja2 import BaseLoader
# 从文件系统中加载模板的加载器。
from jinja2 import FileSystemLoader
# Werkzeug 提供的一组默认 HTTP 异常，如 404、500 等。
from werkzeug.exceptions import default_exceptions
# Werkzeug 提供的基础 HTTP 异常类，所有 HTTP 异常都继承自它。
from werkzeug.exceptions import HTTPException
# Werkzeug 提供的装饰器，将一个方法的结果缓存为属性，只计算一次，之后多次调用时使用缓存结果。
from werkzeug.utils import cached_property

# 表示从当前模块的上一级导入模块或函数。
from .. import typing as ft
# 获取 Flask 应用的根目录路径。
from ..helpers import get_root_path
# templating 模块中的默认模板上下文处理器，它提供给 Jinja2 模板引擎的默认上下文变量
#（如 request, session, g 等）。
from ..templating import _default_template_ctx_processor

# 此代码块仅在类型检查工具（如 MyPy）运行时执行，不会在实际运行时执行。
if t.TYPE_CHECKING:  # pragma: no cover
    # 从 click 模块导入 Group 类，click 是一个用于创建命令行接口的 Python 包，Group 表示命令组。
    from click import Group

# a singleton sentinel value for parameter defaults
# 创建了一个单例哨兵对象，用于表示某种特殊状态或默认值。
_sentinel = object()

# F 是一个类型变量，表示函数类型，约束为任何可调用对象。
# TypeVar 用于泛型编程，这里用于函数装饰器中，表示该装饰器可以接受并返回任意可调用对象。
F = t.TypeVar("F", bound=t.Callable[..., t.Any])
# 定义了若干类型变量 T_after_request, T_before_request, T_error_handler, T_teardown，
# 分别约束为不同的回调函数类型。这些类型通常用于 Flask 应用中的请求处理流程，
# 包括请求前后处理、错误处理和上下文清理。
T_after_request = t.TypeVar("T_after_request", bound=ft.AfterRequestCallable[t.Any])
T_before_request = t.TypeVar("T_before_request", bound=ft.BeforeRequestCallable)
T_error_handler = t.TypeVar("T_error_handler", bound=ft.ErrorHandlerCallable)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
# 表示模板上下文处理器的回调函数类型。
T_template_context_processor = t.TypeVar(
    "T_template_context_processor", bound=ft.TemplateContextProcessorCallable
)
# URL 默认值处理器。
T_url_defaults = t.TypeVar("T_url_defaults", bound=ft.URLDefaultCallable)
# URL 值预处理器的回调函数类型。
T_url_value_preprocessor = t.TypeVar(
    "T_url_value_preprocessor", bound=ft.URLValuePreprocessorCallable
)
# 表示路由处理函数的类型。
T_route = t.TypeVar("T_route", bound=ft.RouteCallable)


# 饰器函数 setupmethod，它用于包装类方法，并在调用该方法之前检查类是否已经完成了某些 "设置" 工作。
# F 是一个泛型，表示任何类型的函数。
def setupmethod(f: F) -> F:
    # 通过 f.__name__，获取被装饰函数的名称 f_name。这通常用于后续调试或错误提示。
    f_name = f.__name__

    def wrapper_func(self: Scaffold, *args: t.Any, **kwargs: t.Any) -> t.Any:
        # 检查当前类实例的设置是否已经完成。
        self._check_setup_finished(f_name)
        # 如果设置完成，调用原始函数 f 并返回其结果。
        return f(self, *args, **kwargs)

    # 将原始函数 f 的元数据（如函数名称、文档字符串等）复制到包装函数 wrapper_func 上。
    # 这样即使函数被装饰，它的名称和文档字符串仍然保持原样。
    return t.cast(F, update_wrapper(wrapper_func, f))







