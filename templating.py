from __future__ import annotations

import typing as t

# 这些类和函数用于模板渲染。
from jinja2 import BaseLoader
from jinja2 import Environment as BaseEnvironment
from jinja2 import Template
from jinja2 import TemplateNotFound

# 用于管理应用和请求上下文的全局变量。
from .globals import _cv_app
from .globals import _cv_request
from .globals import current_app
from .globals import request

#用于处理流式响应的帮助函数。
from .helpers import stream_with_context

# 用于在模板渲染前后触发事件。
from .signals import before_render_template
from .signals import template_rendered

# 这部分代码仅在类型检查时执行，不会在运行时执行。
if t.TYPE_CHECKING:  # pragma: no cover
    from .app import Flask
    from .sansio.app import App
    from .sansio.scaffold import Scaffold


# 默认的模板上下文处理器。
# 它将 request、session 和 g 注入到模板上下文中。
# 通过这种方式，可以在模板中方便地访问和使用请求、会话和全局数据。
def _default_template_ctx_processor() -> dict[str, t.Any]:
    """Default template context processor.  Injects `request`,
    `session` and `g`.
    """
    # 获取当前的应用上下文。如果没有活动的应用上下文，则返回 None。
    appctx = _cv_app.get(None)
    # 获取当前的请求上下文。如果没有活动的请求上下文，则返回 None。
    reqctx = _cv_request.get(None)
    # 初始化一个空字典，用于存储将要注入到模板上下文中的变量。
    rv: dict[str, t.Any] = {}
    # 如果存在活动的应用上下文，则将 g 注入到返回值字典中。
    # g 是一个特殊对象，用于在请求过程中存储和共享数据。
    if appctx is not None:
        rv["g"] = appctx.g
    # 如果存在活动的请求上下文，则将 request 和 session 注入到返回值字典中。
    # request 是当前的请求对象，包含有关当前 HTTP 请求的信息。
    # session 是当前会话对象，允许在多个请求之间存储用户数据。
    if reqctx is not None:
        rv["request"] = reqctx.request
        rv["session"] = reqctx.session
    # 返回包含 g、request 和 session 的字典。
    return rv


















