# 启用未来的注解支持，使得类型注解更加灵活。
from __future__ import annotations

# 用于类型注解。
import typing as t
# 用于管理上下文变量。
from contextvars import ContextVar

# 用于创建上下文代理对象。这些对象在 Flask 应用程序运行时自动绑定到当前的应用上下文或请求上下文。
from werkzeug.local import LocalProxy

# 仅在类型检查时执行，以避免在运行时引入不必要的依赖。
# 这有助于提高代码的可读性和维护性，同时不增加运行时开销。
if t.TYPE_CHECKING:  # pragma: no cover
    from .app import Flask
    from .ctx import _AppCtxGlobals
    from .ctx import AppContext
    from .ctx import RequestContext
    from .sessions import SessionMixin
    from .wrappers import Request


# 定义一个错误消息，当尝试在没有应用上下文的情况下使用应用功能时会显示该消息。
_no_app_msg = """\
Working outside of application context.

This typically means that you attempted to use functionality that needed
the current application. To solve this, set up an application context
with app.app_context(). See the documentation for more information.\
"""
# 用于存储当前的应用上下文。
_cv_app: ContextVar[AppContext] = ContextVar("flask.app_ctx")
# 创建一个 LocalProxy 对象 app_ctx，代理 _cv_app 上下文变量，
# 并在没有绑定上下文时显示错误消息 _no_app_msg。
app_ctx: AppContext = LocalProxy(  # type: ignore[assignment]
    _cv_app, unbound_message=_no_app_msg
)
# 创建一个 LocalProxy 对象 current_app，代理 _cv_app 上下文变量中的 app 属性，
# 并在没有绑定上下文时显示错误消息 _no_app_msg。
current_app: Flask = LocalProxy(  # type: ignore[assignment]
    _cv_app, "app", unbound_message=_no_app_msg
)
# 创建一个 LocalProxy 对象 g，代理 _cv_app 上下文变量中的 g 属性，
# 并在没有绑定上下文时显示错误消息 _no_app_msg。
g: _AppCtxGlobals = LocalProxy(  # type: ignore[assignment]
    _cv_app, "g", unbound_message=_no_app_msg
)

# 定义一个错误消息，当尝试在没有请求上下文的情况下使用请求功能时会显示该消息。
_no_req_msg = """\
Working outside of request context.

This typically means that you attempted to use functionality that needed
an active HTTP request. Consult the documentation on testing for
information about how to avoid this problem.\
"""
# 用于存储当前的请求上下文。
_cv_request: ContextVar[RequestContext] = ContextVar("flask.request_ctx")
# 创建一个 LocalProxy 对象 request_ctx，代理 _cv_request 上下文变量，
# 并在没有绑定上下文时显示错误消息 _no_req_msg。
request_ctx: RequestContext = LocalProxy(  # type: ignore[assignment]
    _cv_request, unbound_message=_no_req_msg
)
# 创建一个 LocalProxy 对象 request，代理 _cv_request 上下文变量中的 request 属性，
# 并在没有绑定上下文时显示错误消息 _no_req_msg。
request: Request = LocalProxy(  # type: ignore[assignment]
    _cv_request, "request", unbound_message=_no_req_msg
)
# 创建一个 LocalProxy 对象 session，代理 _cv_request 上下文变量中的 session 属性，
# 并在没有绑定上下文时显示错误消息 _no_req_msg。
session: SessionMixin = LocalProxy(  # type: ignore[assignment]
    _cv_request, "session", unbound_message=_no_req_msg
)

