# 允许在类型注释中使用从属于本模块或将要在后面定义的类名。
from __future__ import annotations

# 用于管理和隔离上下文本地状态的标准库，非常适合在异步编程中维护状态。
import contextvars
# 访问与Python解释器紧密相关的变量和函数的标准库模块。
import sys
# 以别名t导入typing模块，该模块用于支持类型提示，有助于静态类型检查和文档化代码。
import typing as t
# 用于在使用装饰器时，更新装饰器内函数的一些属性，如__name__、__doc__等，
# 以反映被装饰的原始函数的属性。
from functools import update_wrapper
# 用于类型注释，指明变量应该存储异常的回溯数据。
from types import TracebackType

# 用于处理在HTTP请求过程中可能抛出的各种HTTP异常。
from werkzeug.exceptions import HTTPException


from . import typing as ft
# _cv_app 和 _cv_request，这些是上下文变量，用于全局存取当前 Flask 应用实例和当前请求。
from .globals import _cv_app
from .globals import _cv_request
# appcontext_popped 和 appcontext_pushed 信号，
# 这些信号用于在 Flask 应用上下文被推入和弹出时进行通知。
from .signals import appcontext_popped
from .signals import appcontext_pushed

if t.TYPE_CHECKING:  # pragma: no cover
    # 用于类型注释 WSGI 环境对象。
    from _typeshed.wsgi import WSGIEnvironment

    # 这些导入是类型提示用的，指明 Flask 应用主类、会话管理的 Mixin 类和请求封装类。
    from .app import Flask
    from .sessions import SessionMixin
    from .wrappers import Request


# a singleton sentinel value for parameter defaults
_sentinel = object()