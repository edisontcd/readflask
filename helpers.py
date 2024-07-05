
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


# 用于生成指向应用中各个端点的URL。
# 它可以处理内部和外部URL，并允许添加查询参数和锚点。
def url_for(
    # 要生成URL的端点名称。如果以.开头，则使用当前蓝图名称（如果有）。
    endpoint: str,
    *,
    # 如果提供，则将其作为 #anchor 添加到URL。
    _anchor: str | None = None,
    # 如果提供，则生成与此方法关联的端点的URL。
    _method: str | None = None,
    # 如果提供，则生成与此方法关联的端点的URL。
    _scheme: str | None = None,
    # 如果提供，指定URL是内部的（False）还是外部的（True）。外部URL包括方案和域名。
    # 在非活动请求中，URL默认是外部的。
    _external: bool | None = None,
    # 用于URL规则变量部分的值。未知的键将作为查询字符串参数附加，例如 ?a=b&c=d。
    **values: t.Any,
) -> str:
    """Generate a URL to the given endpoint with the given values.

    This requires an active request or application context, and calls
    :meth:`current_app.url_for() <flask.Flask.url_for>`. See that method
    for full documentation.

    :param endpoint: The endpoint name associated with the URL to
        generate. If this starts with a ``.``, the current blueprint
        name (if any) will be used.
    :param _anchor: If given, append this as ``#anchor`` to the URL.
    :param _method: If given, generate the URL associated with this
        method for the endpoint.
    :param _scheme: If given, the URL will have this scheme if it is
        external.
    :param _external: If given, prefer the URL to be internal (False) or
        require it to be external (True). External URLs include the
        scheme and domain. When not in an active request, URLs are
        external by default.
    :param values: Values to use for the variable parts of the URL rule.
        Unknown keys are appended as query string arguments, like
        ``?a=b&c=d``.

    .. versionchanged:: 2.2
        Calls ``current_app.url_for``, allowing an app to override the
        behavior.

    .. versionchanged:: 0.10
       The ``_scheme`` parameter was added.

    .. versionchanged:: 0.9
       The ``_anchor`` and ``_method`` parameters were added.

    .. versionchanged:: 0.9
       Calls ``app.handle_url_build_error`` on build errors.
    """
    return current_app.url_for(
        endpoint,
        _anchor=_anchor,
        _method=_method,
        _scheme=_scheme,
        _external=_external,
        **values,
    )


# 用于创建重定向响应对象。
# 它根据当前应用的可用性，灵活地选择使用 Flask 的 redirect 方法或 Werkzeug 的默认重定向方法，
def redirect(
    location: str, code: int = 302, Response: type[BaseResponse] | None = None
) -> BaseResponse:
    """Create a redirect response object.

    If :data:`~flask.current_app` is available, it will use its
    :meth:`~flask.Flask.redirect` method, otherwise it will use
    :func:`werkzeug.utils.redirect`.

    :param location: The URL to redirect to.
    :param code: The status code for the redirect.
    :param Response: The response class to use. Not used when
        ``current_app`` is active, which uses ``app.response_class``.

    .. versionadded:: 2.2
        Calls ``current_app.redirect`` if available instead of always
        using Werkzeug's default ``redirect``.
    """
    # 如果 current_app 可用，调用其 redirect 方法，否则使用 Werkzeug 的默认重定向。
    if current_app:
        return current_app.redirect(location, code=code)

    return _wz_redirect(location, code=code, Response=Response)


# 用于引发特定状态码的 HTTP 异常。
def abort(code: int | BaseResponse, *args: t.Any, **kwargs: t.Any) -> t.NoReturn:
    # t.NoReturn，表示此函数不会正常返回，因为它总是引发异常。
    """Raise an :exc:`~werkzeug.exceptions.HTTPException` for the given
    status code.

    If :data:`~flask.current_app` is available, it will call its
    :attr:`~flask.Flask.aborter` object, otherwise it will use
    :func:`werkzeug.exceptions.abort`.

    :param code: The status code for the exception, which must be
        registered in ``app.aborter``.
    :param args: Passed to the exception.
    :param kwargs: Passed to the exception.

    .. versionadded:: 2.2
        Calls ``current_app.aborter`` if available instead of always
        using Werkzeug's default ``abort``.
    """
    # 如果 current_app 可用，调用其 abort 方法，否则使用 Werkzeug 的默认 abort 函数。
    if current_app:
        current_app.aborter(code, *args, **kwargs)

    _wz_abort(code, *args, **kwargs)


# 从 Jinja2 模板中动态加载和调用宏或变量的方法，以便在 Python 代码中调用该宏。
def get_template_attribute(template_name: str, attribute: str) -> t.Any:
    """Loads a macro (or variable) a template exports.  This can be used to
    invoke a macro from within Python code.  If you for example have a
    template named :file:`_cider.html` with the following contents:

    .. sourcecode:: html+jinja

       {% macro hello(name) %}Hello {{ name }}!{% endmacro %}

    You can access this from Python code like this::

        hello = get_template_attribute('_cider.html', 'hello')
        return hello('World')

    .. versionadded:: 0.2

    :param template_name: the name of the template
    :param attribute: the name of the variable of macro to access
    """
    # current_app.jinja_env.get_template 从当前应用的 Jinja2 环境中获取指定的模板。
    # 使用 getattr 函数从模板模块中获取指定的属性（变量或宏）。
    return getattr(current_app.jinja_env.get_template(template_name).module, attribute)


# 用于向用户显示临时消息。
# 这些消息会在下一次请求时显示，常用于通知用户某些操作的结果（例如表单提交成功、错误提示等）。
def flash(message: str, category: str = "message") -> None:
    """Flashes a message to the next request.  In order to remove the
    flashed message from the session and to display it to the user,
    the template has to call :func:`get_flashed_messages`.

    .. versionchanged:: 0.3
       `category` parameter added.

    :param message: the message to be flashed.
    :param category: the category for the message.  The following values
                     are recommended: ``'message'`` for any kind of message,
                     ``'error'`` for errors, ``'info'`` for information
                     messages and ``'warning'`` for warnings.  However any
                     kind of string can be used as category.
    """
    # Original implementation:
    #
    #     session.setdefault('_flashes', []).append((category, message))
    #
    # This assumed that changes made to mutable structures in the session are
    # always in sync with the session object, which is not true for session
    # implementations that use external storage for keeping their keys/values.
    # 从会话中获取现有的闪现消息。如果不存在，则返回一个空列表。
    flashes = session.get("_flashes", [])
    # 将新的消息（包括类别和内容）添加到消息列表中。
    flashes.append((category, message))
    # 将更新后的消息列表存回会话中。
    session["_flashes"] = flashes
    # 获取当前应用实例。
    app = current_app._get_current_object()  # type: ignore
    # 发送 message_flashed 信号，通知系统有新的消息被闪现。信号包含了应用实例、消息内容和类别。
    message_flashed.send(
        app,
        _async_wrapper=app.ensure_sync,
        message=message,
        category=category,
    )


# 用于从会话中提取所有闪现消息，并根据需要返回带或不带类别的消息列表。
def get_flashed_messages(
    # with_categories：一个布尔值，指示是否返回类别，默认为 False。
    # category_filter：一个可迭代对象，用于过滤要返回的消息类别，默认为空元组 ()。
    with_categories: bool = False, category_filter: t.Iterable[str] = ()
) -> list[str] | list[tuple[str, str]]:
    """Pulls all flashed messages from the session and returns them.
    Further calls in the same request to the function will return
    the same messages.  By default just the messages are returned,
    but when `with_categories` is set to ``True``, the return value will
    be a list of tuples in the form ``(category, message)`` instead.

    Filter the flashed messages to one or more categories by providing those
    categories in `category_filter`.  This allows rendering categories in
    separate html blocks.  The `with_categories` and `category_filter`
    arguments are distinct:

    * `with_categories` controls whether categories are returned with message
      text (``True`` gives a tuple, where ``False`` gives just the message text).
    * `category_filter` filters the messages down to only those matching the
      provided categories.

    See :doc:`/patterns/flashing` for examples.

    .. versionchanged:: 0.3
       `with_categories` parameter added.

    .. versionchanged:: 0.9
        `category_filter` parameter added.

    :param with_categories: set to ``True`` to also receive categories.
    :param category_filter: filter of categories to limit return values.  Only
                            categories in the list will be returned.
    """
    # 从请求上下文中获取已缓存的闪现消息。
    flashes = request_ctx.flashes
    # 如果 flashes 为 None，表示尚未从会话中提取消息。
    if flashes is None:
        # 从会话中弹出 _flashes 键（即获取并删除该键），如果 _flashes 存在，返回其值；否则返回一个空列表。
        flashes = session.pop("_flashes") if "_flashes" in session else []
        # 将提取到的消息缓存到请求上下文中，以便在同一请求中多次调用时不重复提取。
        request_ctx.flashes = flashes
    # 使用 filter 函数过滤消息，只保留类别在 category_filter 中的消息。
    if category_filter:
        flashes = list(filter(lambda f: f[0] in category_filter, flashes))
    # 如果 with_categories 为 False，只返回消息的文本部分。
    if not with_categories:
        # 返回消息的文本部分列表。
        return [x[1] for x in flashes]
    # 返回包含类别和消息文本的元组列表。
    return flashes


# 一个内部辅助函数，用于准备发送文件时所需的参数。
# **kwargs 接受任意数量的关键字参数，这些参数会被传递给 Flask 的 send_file 函数。
# 返回一个字典，其中包含了用于发送文件的参数。
def _prepare_send_file_kwargs(**kwargs: t.Any) -> dict[str, t.Any]:
    # 如果没有设置 max_age 参数，使用当前应用的 get_send_file_max_age 方法来设置默认值。
    if kwargs.get("max_age") is None:
        kwargs["max_age"] = current_app.get_send_file_max_age

    # 更新关键字参数字典，添加以下参数。
    kwargs.update(
        # 设置为当前请求的环境变量 request.environ。
        environ=request.environ,
        # 从当前应用的配置中获取 USE_X_SENDFILE 参数。
        use_x_sendfile=current_app.config["USE_X_SENDFILE"],
        # 使用当前应用的响应类 current_app.response_class。
        response_class=current_app.response_class,
        # 设置为当前应用的根路径 current_app.root_path。
        _root_path=current_app.root_path,  # type: ignore
    )
    # 返回更新后的关键字参数字典。
    return kwargs












