
# 启用未来的注解支持，使得类型注解更加灵活。
from __future__ import annotations

# importlib.util 和 os：用于动态加载配置文件或模块。
# datetime：用于处理时间戳或记录日志。
# lru_cache 和 update_wrapper：用于优化性能和装饰函数。
# werkzeug.utils 和 werkzeug.exceptions：用于处理 HTTP 重定向和错误响应。
# current_app 和 request：用于在视图函数中访问当前应用实例和请求对象。
# session：用于管理用户会话数据。
# message_flashed：用于发送和接收闪现消息信号。
# 用于导入和加载模块的工具。
import importlib.util
import os
import sys
# 用于类型注解。
import typing as t
from datetime import datetime
# 提供最近最少使用（LRU）缓存装饰器。
from functools import lru_cache
# 更新包装函数以更好地反映被包装的函数。
from functools import update_wrapper

# 导入 Werkzeug 实用工具模块。
import werkzeug.utils
# 用于终止请求并返回错误响应。
from werkzeug.exceptions import abort as _wz_abort
# 用于发起重定向响应。
from werkzeug.utils import redirect as _wz_redirect
# 用作基本响应类。
from werkzeug.wrappers import Response as BaseResponse

# 当前请求上下文变量。
from .globals import _cv_request
# 当前应用实例。
from .globals import current_app
# 当前请求对象。
from .globals import request
# 当前请求上下文。
from .globals import request_ctx
# 当前会话对象。
from .globals import session
# 消息闪现信号，用于在闪现消息时发出信号。
from .signals import message_flashed

# 仅在进行类型检查时执行此块中的导入，以避免在运行时引入不必要的依赖。
if t.TYPE_CHECKING:  # pragma: no cover
    from .wrappers import Response


# 用于获取应用是否应该启用调试模式。
# 获取是否应为应用启用调试模式，这由环境变量 FLASK_DEBUG 指定。默认值为 False。
def get_debug_flag() -> bool:
    """Get whether debug mode should be enabled for the app, indicated by the
    :envvar:`FLASK_DEBUG` environment variable. The default is ``False``.
    """
    # 从环境变量中获取 FLASK_DEBUG 的值。如果环境变量未设置，os.environ.get 会返回 None。
    val = os.environ.get("FLASK_DEBUG")
    # 如果 val 存在且不在 {"0", "false", "no"} 集合中，则返回 True，表示应启用调试模式。
    # 否则返回 False，表示不应启用调试模式。
    return bool(val and val.lower() not in {"0", "false", "no"})


# 用于确定是否加载默认的 .env 文件。
# 通过环境变量 FLASK_SKIP_DOTENV 来控制此行为，默认情况下是加载 .env 文件。
def get_load_dotenv(default: bool = True) -> bool:
    """Get whether the user has disabled loading default dotenv files by
    setting :envvar:`FLASK_SKIP_DOTENV`. The default is ``True``, load
    the files.

    :param default: What to return if the env var isn't set.
    """
    # 从环境变量中获取 FLASK_SKIP_DOTENV 的值。
    # 如果环境变量未设置，os.environ.get 会返回 None。
    val = os.environ.get("FLASK_SKIP_DOTENV")

    # 如果 val 为 None 或空字符串，返回 default 参数的值。
    if not val:
        return default

    # 如果环境变量 FLASK_SKIP_DOTENV 设置了值，将其转换为小写，
    # 并检查它是否在集合 ("0", "false", "no") 中。
    # 如果 val 在集合中，则返回 True，表示应加载 .env 文件。
    # 否则返回 False，表示不应加载 .env 文件。
    return val.lower() in ("0", "false", "no")


# 用于在 Flask 应用中保持请求上下文，即使在生成器函数生成响应流的过程中。
# 这个函数的主要目的是在使用流式响应时，使生成器能够访问请求上下文中的信息。 
def stream_with_context(
    # 可以是一个生成器对象或一个返回生成器的函数。
    generator_or_function: t.Iterator[t.AnyStr] | t.Callable[..., t.Iterator[t.AnyStr]],
) -> t.Iterator[t.AnyStr]:
    """Request contexts disappear when the response is started on the server.
    This is done for efficiency reasons and to make it less likely to encounter
    memory leaks with badly written WSGI middlewares.  The downside is that if
    you are using streamed responses, the generator cannot access request bound
    information any more.

    This function however can help you keep the context around for longer::

        from flask import stream_with_context, request, Response

        @app.route('/stream')
        def streamed_response():
            @stream_with_context
            def generate():
                yield 'Hello '
                yield request.args['name']
                yield '!'
            return Response(generate())

    Alternatively it can also be used around a specific generator::

        from flask import stream_with_context, request, Response

        @app.route('/stream')
        def streamed_response():
            def generate():
                yield 'Hello '
                yield request.args['name']
                yield '!'
            return Response(stream_with_context(generate()))

    .. versionadded:: 0.9
    """
    # 尝试将 generator_or_function 转换为迭代器。
    try:
        gen = iter(generator_or_function)  # type: ignore[arg-type]
    # 如果失败，则说明它是一个返回生成器的函数。
    except TypeError:
        # decorator 调用原始函数，获取生成器对象，并使用 stream_with_context 包装生成器对象。
        def decorator(*args: t.Any, **kwargs: t.Any) -> t.Any:
            gen = generator_or_function(*args, **kwargs)  # type: ignore[operator]
            return stream_with_context(gen)

        # 返回使用 update_wrapper 更新过的装饰器函数，以确保装饰器函数的属性与原始函数一致。
        return update_wrapper(decorator, generator_or_function)  # type: ignore[arg-type, return-value]

    # 定义内部生成器函数 generator，用于保持请求上下文。
    def generator() -> t.Iterator[t.AnyStr | None]:
        # 获取当前请求上下文 ctx。
        ctx = _cv_request.get(None)
        # 如果不存在，则抛出运行时错误。
        if ctx is None:
            raise RuntimeError(
                "'stream_with_context' can only be used when a request"
                " context is active, such as in a view function."
            )
        # 使用 with ctx: 语句块保持上下文，并在进入上下文后立即生成一个 None 以确保上下文已被推送。
        with ctx:
            # Dummy sentinel.  Has to be inside the context block or we're
            # not actually keeping the context around.
            yield None

            # The try/finally is here so that if someone passes a WSGI level
            # iterator in we're still running the cleanup logic.  Generators
            # don't need that because they are closed on their destruction
            # automatically.
            # 使用 try/finally 块确保即使在生成器完成或关闭时也能正确执行清理操作。
            try:
                # 将生成器的内容逐步返回给调用者。
                yield from gen
            finally:
                if hasattr(gen, "close"):
                    gen.close()

    # The trick is to start the generator.  Then the code execution runs until
    # the first dummy None is yielded at which point the context was already
    # pushed.  This item is discarded.  Then when the iteration continues the
    # real generator is executed.
    # 启动内部生成器 generator 并跳过第一个 None 值，以确保上下文已被推送。
    wrapped_g = generator()
    next(wrapped_g)
    # 返回包装后的生成器对象 wrapped_g。
    return wrapped_g  # type: ignore[return-value]


# 用于在 Flask 应用中创建一个响应对象。
# 允许开发者在视图函数中添加额外的响应头，或强制将视图函数的返回值转换为响应对象。
def make_response(*args: t.Any) -> Response:
    """Sometimes it is necessary to set additional headers in a view.  Because
    views do not have to return response objects but can return a value that
    is converted into a response object by Flask itself, it becomes tricky to
    add headers to it.  This function can be called instead of using a return
    and you will get a response object which you can use to attach headers.

    If view looked like this and you want to add a new header::

        def index():
            return render_template('index.html', foo=42)

    You can now do something like this::

        def index():
            response = make_response(render_template('index.html', foo=42))
            response.headers['X-Parachutes'] = 'parachutes are cool'
            return response

    This function accepts the very same arguments you can return from a
    view function.  This for example creates a response with a 404 error
    code::

        response = make_response(render_template('not_found.html'), 404)

    The other use case of this function is to force the return value of a
    view function into a response which is helpful with view
    decorators::

        response = make_response(view_function())
        response.headers['X-Parachutes'] = 'parachutes are cool'

    Internally this function does the following things:

    -   if no arguments are passed, it creates a new response argument
    -   if one argument is passed, :meth:`flask.Flask.make_response`
        is invoked with it.
    -   if more than one argument is passed, the arguments are passed
        to the :meth:`flask.Flask.make_response` function as tuple.

    .. versionadded:: 0.6
    """
    # 如果没有传入任何参数，创建一个新的空响应对象并返回。
    if not args:
        return current_app.response_class()
    # 如果只传入了一个参数，将 args 设置为该参数的值。
    if len(args) == 1:
        args = args[0]
    # 调用当前应用的 make_response 方法，将参数传递给它并返回创建的响应对象。
    return current_app.make_response(args)
































