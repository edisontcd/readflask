from __future__ import annotations

import os
import typing as t
# 一个字典子类，提供默认值功能。
from collections import defaultdict
# 用于更新装饰器的元数据，使其与被装饰的函数一致。
from functools import update_wrapper

from .. import typing as ft
from .scaffold import _endpoint_from_view_func
from .scaffold import _sentinel
from .scaffold import Scaffold
from .scaffold import setupmethod

# 这个块中的代码只在类型检查时有效，通常用于避免运行时导入。
if t.TYPE_CHECKING:  # pragma: no cover
    from .app import App

# 示一个接受 BlueprintSetupState 类型参数并返回 None 的可调用对象。
DeferredSetupFunction = t.Callable[["BlueprintSetupState"], None]
# 绑定到 ft.AfterRequestCallable 类型，表示可以接受任何类型的请求处理函数。
T_after_request = t.TypeVar("T_after_request", bound=ft.AfterRequestCallable[t.Any])
# 表示一个在请求之前调用的函数类型。
T_before_request = t.TypeVar("T_before_request", bound=ft.BeforeRequestCallable)
# 表示一个处理错误的函数类型。
T_error_handler = t.TypeVar("T_error_handler", bound=ft.ErrorHandlerCallable)
# 表示一个在请求结束时调用的函数类型。
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
# 表示一个用于处理模板上下文的函数类型。
T_template_context_processor = t.TypeVar(
    "T_template_context_processor", bound=ft.TemplateContextProcessorCallable
)
# 表示一个模板过滤器的函数类型。
T_template_filter = t.TypeVar("T_template_filter", bound=ft.TemplateFilterCallable)
# 表示一个全局模板变量的函数类型。
T_template_global = t.TypeVar("T_template_global", bound=ft.TemplateGlobalCallable)
# 表示一个用于模板测试的函数类型。
T_template_test = t.TypeVar("T_template_test", bound=ft.TemplateTestCallable)
# 表示一个用于 URL 默认值的函数类型。
T_url_defaults = t.TypeVar("T_url_defaults", bound=ft.URLDefaultCallable)
# 表示一个用于 URL 值预处理的函数类型。
T_url_value_preprocessor = t.TypeVar(
    "T_url_value_preprocessor", bound=ft.URLValuePreprocessorCallable
)























