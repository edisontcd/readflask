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


# 用于在应用上下文中作为一个命名空间存储数据。
# 当创建一个应用上下文时，这个对象会被自动创建，并通过 g 代理对象使其可用。
class _AppCtxGlobals:
    """A plain object. Used as a namespace for storing data during an
    application context.

    Creating an app context automatically creates this object, which is
    made available as the :data:`g` proxy.

    .. describe:: 'key' in g

        Check whether an attribute is present.

        .. versionadded:: 0.10

    .. describe:: iter(g)

        Return an iterator over the attribute names.

        .. versionadded:: 0.10
    """

    # Define attr methods to let mypy know this is a namespace object
    # that has arbitrary attributes.

    # 用来获取属性的特殊方法。
    # 如果这个属性在实例的字典 __dict__ 中不存在，则会抛出一个 AttributeError 异常。
    # 这允许 _AppCtxGlobals 对象动态地处理属性访问，即使这些属性在创建对象时并未定义。
    def __getattr__(self, name: str) -> t.Any:
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(name) from None

    # 重写了设置属性的行为。
    # 通过直接修改实例的字典 __dict__，这个方法允许动态地为对象添加新属性
    # 或修改现有属性的值，从而提供了极高的灵活性。
    def __setattr__(self, name: str, value: t.Any) -> None:
        self.__dict__[name] = value

    # 用于删除属性。
    # 如果尝试删除的属性在 __dict__ 中不存在，则会抛出 AttributeError 异常。
    # 这样，可以确保只有实际存在的属性可以被删除，避免了可能的错误。
    def __delattr__(self, name: str) -> None:
        try:
            del self.__dict__[name]
        except KeyError:
            raise AttributeError(name) from None

    # 用于从 _AppCtxGlobals 对象中获取属性值。如果属性不存在，则返回一个默认值。
    def get(self, name: str, default: t.Any | None = None) -> t.Any:
        """Get an attribute by name, or a default value. Like
        :meth:`dict.get`.

        :param name: Name of attribute to get.
        :param default: Value to return if the attribute is not present.

        .. versionadded:: 0.10
        """
        return self.__dict__.get(name, default)

    # 用于获取并移除 _AppCtxGlobals 对象中的属性。
    # 如果属性不存在，可以选择返回一个默认值，而不是抛出 KeyError 异常。
    def pop(self, name: str, default: t.Any = _sentinel) -> t.Any:
        """Get and remove an attribute by name. Like :meth:`dict.pop`.

        :param name: Name of attribute to pop.
        :param default: Value to return if the attribute is not present,
            instead of raising a ``KeyError``.

        .. versionadded:: 0.11
        """
        if default is _sentinel:
            return self.__dict__.pop(name)
        else:
            return self.__dict__.pop(name, default)

    # 用于获取属性的值，如果属性不存在，则设置属性为默认值并返回该默认值。
    def setdefault(self, name: str, default: t.Any = None) -> t.Any:
        """Get the value of an attribute if it is present, otherwise
        set and return a default value. Like :meth:`dict.setdefault`.

        :param name: Name of attribute to get.
        :param default: Value to set and return if the attribute is not
            present.

        .. versionadded:: 0.11
        """
        return self.__dict__.setdefault(name, default) 

    # 这个方法实现了 in 运算符，使我们可以使用 item in obj 的语法来
    # 检查 item 是否存在于 self.__dict__ 中。
    # item：要检查的属性名，类型为字符串。
    # 返回值类型为布尔值，如果 item 是 self.__dict__ 的一个键，
    # 则返回 True，否则返回 False。
    def __contains__(self, item: str) -> bool:
        return item in self.__dict__

    # 这个方法使对象可迭代，返回一个迭代器，可以遍历 self.__dict__ 的键。
    # 返回值类型为字符串迭代器。
    def __iter__(self) -> t.Iterator[str]:
        return iter(self.__dict__)

    # 这个方法提供了对象的字符串表示，主要用于调试和日志记录。
    # 尝试从 _cv_app 中获取当前的应用上下文 ctx。
    # 如果 ctx 不为 None，则返回一个格式化字符串，表示当前的 Flask 应用名称（例如 <flask.g of 'myapp'>）。
    # 如果 ctx 为 None，则调用 object.__repr__(self) 返回默认的对象表示。
    def __repr__(self) -> str:
        ctx = _cv_app.get(None)
        if ctx is not None:
            return f"<flask.g of '{ctx.app.name}'>"
        return object.__repr__(self)


# 用于在请求处理完毕后执行一个函数。
# 这个函数通常用于修改响应对象，例如添加额外的头部信息。
def after_this_request(
    # f: 一个可调用对象，用于在请求处理完毕后执行的操作。
    # 它接受一个响应对象作为参数，并返回同一个或新的响应对象。
    f: ft.AfterRequestCallable[t.Any],
) -> ft.AfterRequestCallable[t.Any]:
    """Executes a function after this request.  This is useful to modify
    response objects.  The function is passed the response object and has
    to return the same or a new one.

    Example::

        @app.route('/')
        def index():
            @after_this_request
            def add_header(response):
                response.headers['X-Foo'] = 'Parachute'
                return response
            return 'Hello World!'

    This is more useful if a function other than the view function wants to
    modify a response.  For instance think of a decorator that wants to add
    some headers without converting the return value into a response object.

    .. versionadded:: 0.9
    """
    ctx = _cv_request.get(None)

    # 如果没有请求上下文处于活动状态（例如在视图函数之外调用），则会引发 RuntimeError 异常。
    if ctx is None:
        raise RuntimeError(
            "'after_this_request' can only be used when a request"
            " context is active, such as in a view function."
        )

    ctx._after_request_functions.append(f)
    return f

# 变量 F 用于声明一个泛型类型，表示任意的可调用对象。
F = t.TypeVar("F", bound=t.Callable[..., t.Any])


# 一个装饰器，用于在异步工作环境中（例如使用 greenlets）保留当前的请求上下文。
# 当异步函数被调用时，它仍然能够访问 Flask 的请求上下文和会话。
# f：被装饰的函数。类型为 F，这是一个泛型类型，表示任何可调用对象。
def copy_current_request_context(f: F) -> F:
    """A helper function that decorates a function to retain the current
    request context.  This is useful when working with greenlets.  The moment
    the function is decorated a copy of the request context is created and
    then pushed when the function is called.  The current session is also
    included in the copied request context.

    Example::

        import gevent
        from flask import copy_current_request_context

        @app.route('/')
        def index():
            @copy_current_request_context
            def do_some_work():
                # do some work here, it can access flask.request or
                # flask.session like you would otherwise in the view function.
                ...
            gevent.spawn(do_some_work)
            return 'Regular response'

    .. versionadded:: 0.10
    """
    # 通过 _cv_request.get(None) 获取当前请求上下文。
    ctx = _cv_request.get(None)

    # 如果当前没有活动的请求上下文，则抛出 RuntimeError 异常，
    # 提示该装饰器只能在有活动请求上下文时使用，例如在视图函数中。
    if ctx is None:
        raise RuntimeError(
            "'copy_current_request_context' can only be used when a"
            " request context is active, such as in a view function."
        )

    # 复制当前的请求上下文 ctx，以便在异步工作时能够使用这个上下文。
    ctx = ctx.copy()

    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        # 使用 with ctx: 语句推送复制的上下文 ctx。
        with ctx:  # type: ignore[union-attr]
            # 执行被装饰的函数 f，确保函数在正确的上下文中执行。
            return ctx.app.ensure_sync(f)(*args, **kwargs)  # type: ignore[union-attr]

    return update_wrapper(wrapper, f)  # type: ignore[return-value]













