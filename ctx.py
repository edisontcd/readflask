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


# 用于检查当前是否存在请求上下文。
# 这在编写需要根据请求上下文条件执行不同操作的代码时非常有用。
# 该函数没有参数，返回一个布尔值，指示当前是否存在请求上下文。
def has_request_context() -> bool:
    """If you have code that wants to test if a request context is there or
    not this function can be used.  For instance, you may want to take advantage
    of request information if the request object is available, but fail
    silently if it is unavailable.

    ::

        class User(db.Model):

            def __init__(self, username, remote_addr=None):
                self.username = username
                if remote_addr is None and has_request_context():
                    remote_addr = request.remote_addr
                self.remote_addr = remote_addr

    Alternatively you can also just test any of the context bound objects
    (such as :class:`request` or :class:`g`) for truthness::

        class User(db.Model):

            def __init__(self, username, remote_addr=None):
                self.username = username
                if remote_addr is None and request:
                    remote_addr = request.remote_addr
                self.remote_addr = remote_addr

    .. versionadded:: 0.7
    """
    # _cv_request.get(None)尝试获取当前请求上下文对象。如果不存在请求上下文，则返回 None。
    # is not None 判断当前请求上下文对象是否存在。如果存在，返回 True；否则返回 False。
    return _cv_request.get(None) is not None


# 用于检查当前是否存在应用上下文。
# 这个函数没有参数，返回一个布尔值，指示当前是否存在应用上下文。
# 也可以直接对 current_app 对象进行布尔检查来达到相同的效果。
def has_app_context() -> bool:
    """Works like :func:`has_request_context` but for the application
    context.  You can also just do a boolean check on the
    :data:`current_app` object instead.

    .. versionadded:: 0.9
    """
    return _cv_app.get(None) is not None


# 管理 Flask 应用的上下文信息，确保在请求和 CLI 命令执行期间正确地设置和清理上下文。
# 通过实现上下文管理协议，AppContext 可以方便地使用 with 语句来自动管理上下文的推送和弹出。
class AppContext:
    """The app context contains application-specific information. An app
    context is created and pushed at the beginning of each request if
    one is not already active. An app context is also pushed when
    running CLI commands.
    """

    # 构造方法
    def __init__(self, app: Flask) -> None:
        # 保存应用实例。
        self.app = app
        # 创建 URL 适配器，用于 URL 映射。
        self.url_adapter = app.create_url_adapter(None)
        # 创建一个全局命名空间对象，用于存储临时数据。
        self.g: _AppCtxGlobals = app.app_ctx_globals_class()
        # 初始化一个列表，用于存储上下文变量的令牌。
        self._cv_tokens: list[contextvars.Token[AppContext]] = []

    # 推送上下文
    # push 方法将应用上下文绑定到当前上下文。
    # 将当前上下文设置为 self 并存储上下文变量的令牌。
    # 发送 appcontext_pushed 信号，通知应用上下文已被推送。
    def push(self) -> None:
        """Binds the app context to the current context."""
        self._cv_tokens.append(_cv_app.set(self))
        appcontext_pushed.send(self.app, _async_wrapper=self.app.ensure_sync)

    # 弹出上下文
    def pop(self, exc: BaseException | None = _sentinel) -> None:  # type: ignore
        """Pops the app context."""
        # 如果当前上下文令牌列表中只有一个令牌，则调用 do_teardown_appcontext 方法进行上下文清理。
        try:
            if len(self._cv_tokens) == 1:
                if exc is _sentinel:
                    exc = sys.exc_info()[1]
                self.app.do_teardown_appcontext(exc)
        # 重置上下文变量，将其从 _cv_tokens 中移除。
        finally:
            ctx = _cv_app.get()
            _cv_app.reset(self._cv_tokens.pop())

        # 如果弹出的上下文不是当前上下文，抛出 AssertionError 异常。
        if ctx is not self:
            raise AssertionError(
                f"Popped wrong app context. ({ctx!r} instead of {self!r})"
            )

        # 发送 appcontext_popped 信号，通知应用上下文已被弹出。
        appcontext_popped.send(self.app, _async_wrapper=self.app.ensure_sync)

    # 上下文管理协议
    # 实现上下文管理协议，使 AppContext 可以使用 with 语句。
    # 在进入 with 语句时推送上下文，并返回自身。
    def __enter__(self) -> AppContext:
        self.push()
        return self

    # 在退出 with 语句时弹出上下文。接收异常类型、异常值和回溯对象作为参数。
    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.pop(exc_value)


# 管理每个请求的上下文信息，包括请求对象、URL 适配器和会话。
# 它在每个请求开始时创建并推送，在请求结束时弹出。通过上下文管理协议，
# 可以方便地使用 with 语句来自动管理请求上下文的推送和弹出。
# 不应直接使用这个类，而是通过 flask.Flask.test_request_context 和 
# flask.Flask.request_context 来创建这个对象。
# 请求上下文弹出时，会执行所有注册的清理函数。
class RequestContext:
    """The request context contains per-request information. The Flask
    app creates and pushes it at the beginning of the request, then pops
    it at the end of the request. It will create the URL adapter and
    request object for the WSGI environment provided.

    Do not attempt to use this class directly, instead use
    :meth:`~flask.Flask.test_request_context` and
    :meth:`~flask.Flask.request_context` to create this object.

    When the request context is popped, it will evaluate all the
    functions registered on the application for teardown execution
    (:meth:`~flask.Flask.teardown_request`).

    The request context is automatically popped at the end of the
    request. When using the interactive debugger, the context will be
    restored so ``request`` is still accessible. Similarly, the test
    client can preserve the context after the request ends. However,
    teardown functions may already have closed some resources such as
    database connections.
    """

    # 初始化方法。
    def __init__(
        self,
        app: Flask,
        environ: WSGIEnvironment,
        request: Request | None = None,
        session: SessionMixin | None = None,
    ) -> None:
        self.app = app
        # 如果未提供 request 参数，使用 app.request_class 创建一个新的请求对象，
        # 并设置其 json_module 属性。
        if request is None:
            request = app.request_class(environ)
            request.json_module = app.json
        # 将 request 保存到实例变量 self.request 中。
        self.request: Request = request
        # 初始化 self.url_adapter 为 None。
        self.url_adapter = None
        # 尝试创建 URL 适配器并赋值给 self.url_adapter。如果出现 HTTPException 异常，
        # 将异常保存到 self.request.routing_exception 中。
        try:
            self.url_adapter = app.create_url_adapter(self.request)
        except HTTPException as e:
            self.request.routing_exception = e
        # 初始化 self.flashes 为 None，用于存储闪现消息。
        self.flashes: list[tuple[str, str]] | None = None
        # 将 session 参数保存到实例变量 self.session 中。
        self.session: SessionMixin | None = session
        # Functions that should be executed after the request on the response
        # object.  These will be called before the regular "after_request"
        # functions.
        # 在响应对象上执行的函数列表。初始化 self._after_request_functions 为一个空列表，
        # 用于存储请求后的回调函数。
        self._after_request_functions: list[ft.AfterRequestCallable[t.Any]] = []

        # 上下文变量令牌列表。初始化 self._cv_tokens 为一个空列表，用于存储上下文变量的令牌。
        self._cv_tokens: list[
            tuple[contextvars.Token[RequestContext], AppContext | None]
        ] = []

    # 创建一个当前请求上下文的副本，使用相同的请求对象。
    # 返回新的 RequestContext 实例。
    def copy(self) -> RequestContext:
        """Creates a copy of this request context with the same request object.
        This can be used to move a request context to a different greenlet.
        Because the actual request object is the same this cannot be used to
        move a request context to a different thread unless access to the
        request object is locked.

        .. versionadded:: 0.10

        .. versionchanged:: 1.1
           The current session object is used instead of reloading the original
           data. This prevents `flask.session` pointing to an out-of-date object.
        """
        return self.__class__(
            self.app,
            environ=self.request.environ,
            request=self.request,
            session=self.session,
        )

    # 匹配请求的 URL，并设置请求的 url_rule 和 view_args。
    # 可以被子类重写以钩入请求匹配过程。
    def match_request(self) -> None:
        """Can be overridden by a subclass to hook into the matching
        of the request.
        """
        try:
            result = self.url_adapter.match(return_rule=True)  # type: ignore
            self.request.url_rule, self.request.view_args = result  # type: ignore
        except HTTPException as e:
            self.request.routing_exception = e

    # 推送请求上下文。
    def push(self) -> None:
        # Before we push the request context we have to ensure that there
        # is an application context.
        # 在推送请求上下文之前，确保存在应用上下文。
        app_ctx = _cv_app.get(None)

        # 如果没有应用上下文或应用上下文不是当前应用的，创建并推送一个新的应用上下文。
        if app_ctx is None or app_ctx.app is not self.app:
            app_ctx = self.app.app_context()
            app_ctx.push()
        else:
            app_ctx = None

        # 将请求上下文设置为当前上下文，并保存上下文变量令牌。
        self._cv_tokens.append((_cv_request.set(self), app_ctx))

        # Open the session at the moment that the request context is available.
        # This allows a custom open_session method to use the request context.
        # Only open a new session if this is the first time the request was
        # pushed, otherwise stream_with_context loses the session.
        # 在请求上下文可用时打开会话。
        if self.session is None:
            session_interface = self.app.session_interface
            self.session = session_interface.open_session(self.app, self.request)

            if self.session is None:
                self.session = session_interface.make_null_session(self.app)

        # Match the request URL after loading the session, so that the
        # session is available in custom URL converters.
        # 加载会话后匹配请求的 URL，使会话在自定义 URL 转换器中可用。
        if self.url_adapter is not None:
            self.match_request()

    # 弹出请求上下文并解除绑定。
    def pop(self, exc: BaseException | None = _sentinel) -> None:  # type: ignore
        """Pops the request context and unbinds it by doing that.  This will
        also trigger the execution of functions registered by the
        :meth:`~flask.Flask.teardown_request` decorator.

        .. versionchanged:: 0.9
           Added the `exc` argument.
        """
        clear_request = len(self._cv_tokens) == 1

        # 如果这是最后一个上下文令牌，执行请求的清理操作。
        try:
            if clear_request:
                if exc is _sentinel:
                    exc = sys.exc_info()[1]
                self.app.do_teardown_request(exc)

                request_close = getattr(self.request, "close", None)
                if request_close is not None:
                    request_close()
        # 重置上下文变量，并在请求结束时清除循环依赖。
        finally:
            ctx = _cv_request.get()
            token, app_ctx = self._cv_tokens.pop()
            _cv_request.reset(token)

            # get rid of circular dependencies at the end of the request
            # so that we don't require the GC to be active.
            if clear_request:
                ctx.request.environ["werkzeug.request"] = None

            if app_ctx is not None:
                app_ctx.pop(exc)

            # 确保弹出的上下文是当前的上下文，否则抛出 AssertionError。
            if ctx is not self:
                raise AssertionError(
                    f"Popped wrong request context. ({ctx!r} instead of {self!r})"
                )

    # 实现上下文管理协议，使 RequestContext 可以使用 with 语句。
    # 进入 with 语句时推送上下文，退出时弹出上下文。
    def __enter__(self) -> RequestContext:
        self.push()
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.pop(exc_value)

    # 返回请求上下文的字符串表示形式，包含请求的 URL 和方法，以及应用的名称。
    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} {self.request.url!r}"
            f" [{self.request.method}] of {self.app.name}>"
        )




