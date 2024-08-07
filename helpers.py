
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


# 用于在应用中将文件发送到客户端。
# 它封装了 Werkzeug 的 send_file 函数，并添加了一些 Flask 特有的参数处理，
# 使得开发者可以更加灵活和方便地管理文件传输。
# 通过使用 _prepare_send_file_kwargs 辅助函数，这个函数可以从当前请求和应用中获取必要的信息，
# 并设置一些默认值，从而简化了文件发送的过程。
def send_file(
    # 文件路径（可以是 os.PathLike 或 str 类型）或文件对象（必须是以二进制模式打开的）。
    path_or_file: os.PathLike[t.AnyStr] | str | t.BinaryIO,
    # 文件的 MIME 类型，如果未提供，将尝试从文件名中检测。
    mimetype: str | None = None,
    # 指示浏览器是否应将文件保存为附件而不是直接显示。
    as_attachment: bool = False,
    # 浏览器保存文件时的默认名称，默认为传递的文件名。
    download_name: str | None = None,
    # 启用基于请求头的条件和范围响应，默认为 True。
    conditional: bool = True,
    # 计算文件的 ETag，可以是布尔值或字符串。
    etag: bool | str = True,
    # 文件的最后修改时间，可以是 datetime 对象、时间戳（整数或浮点数）或 None。
    last_modified: datetime | int | float | None = None,
    # 客户端应缓存文件的时间，以秒为单位。
    max_age: None | (int | t.Callable[[str | None], int | None]) = None,
) -> Response:
    """Send the contents of a file to the client.

    The first argument can be a file path or a file-like object. Paths
    are preferred in most cases because Werkzeug can manage the file and
    get extra information from the path. Passing a file-like object
    requires that the file is opened in binary mode, and is mostly
    useful when building a file in memory with :class:`io.BytesIO`.

    Never pass file paths provided by a user. The path is assumed to be
    trusted, so a user could craft a path to access a file you didn't
    intend. Use :func:`send_from_directory` to safely serve
    user-requested paths from within a directory.

    If the WSGI server sets a ``file_wrapper`` in ``environ``, it is
    used, otherwise Werkzeug's built-in wrapper is used. Alternatively,
    if the HTTP server supports ``X-Sendfile``, configuring Flask with
    ``USE_X_SENDFILE = True`` will tell the server to send the given
    path, which is much more efficient than reading it in Python.

    :param path_or_file: The path to the file to send, relative to the
        current working directory if a relative path is given.
        Alternatively, a file-like object opened in binary mode. Make
        sure the file pointer is seeked to the start of the data.
    :param mimetype: The MIME type to send for the file. If not
        provided, it will try to detect it from the file name.
    :param as_attachment: Indicate to a browser that it should offer to
        save the file instead of displaying it.
    :param download_name: The default name browsers will use when saving
        the file. Defaults to the passed file name.
    :param conditional: Enable conditional and range responses based on
        request headers. Requires passing a file path and ``environ``.
    :param etag: Calculate an ETag for the file, which requires passing
        a file path. Can also be a string to use instead.
    :param last_modified: The last modified time to send for the file,
        in seconds. If not provided, it will try to detect it from the
        file path.
    :param max_age: How long the client should cache the file, in
        seconds. If set, ``Cache-Control`` will be ``public``, otherwise
        it will be ``no-cache`` to prefer conditional caching.

    .. versionchanged:: 2.0
        ``download_name`` replaces the ``attachment_filename``
        parameter. If ``as_attachment=False``, it is passed with
        ``Content-Disposition: inline`` instead.

    .. versionchanged:: 2.0
        ``max_age`` replaces the ``cache_timeout`` parameter.
        ``conditional`` is enabled and ``max_age`` is not set by
        default.

    .. versionchanged:: 2.0
        ``etag`` replaces the ``add_etags`` parameter. It can be a
        string to use instead of generating one.

    .. versionchanged:: 2.0
        Passing a file-like object that inherits from
        :class:`~io.TextIOBase` will raise a :exc:`ValueError` rather
        than sending an empty file.

    .. versionadded:: 2.0
        Moved the implementation to Werkzeug. This is now a wrapper to
        pass some Flask-specific arguments.

    .. versionchanged:: 1.1
        ``filename`` may be a :class:`~os.PathLike` object.

    .. versionchanged:: 1.1
        Passing a :class:`~io.BytesIO` object supports range requests.

    .. versionchanged:: 1.0.3
        Filenames are encoded with ASCII instead of Latin-1 for broader
        compatibility with WSGI servers.

    .. versionchanged:: 1.0
        UTF-8 filenames as specified in :rfc:`2231` are supported.

    .. versionchanged:: 0.12
        The filename is no longer automatically inferred from file
        objects. If you want to use automatic MIME and etag support,
        pass a filename via ``filename_or_fp`` or
        ``attachment_filename``.

    .. versionchanged:: 0.12
        ``attachment_filename`` is preferred over ``filename`` for MIME
        detection.

    .. versionchanged:: 0.9
        ``cache_timeout`` defaults to
        :meth:`Flask.get_send_file_max_age`.

    .. versionchanged:: 0.7
        MIME guessing and etag support for file-like objects was
        removed because it was unreliable. Pass a filename if you are
        able to, otherwise attach an etag yourself.

    .. versionchanged:: 0.5
        The ``add_etags``, ``cache_timeout`` and ``conditional``
        parameters were added. The default behavior is to add etags.

    .. versionadded:: 0.2
    """
    # werkzeug.utils.send_file 是 Werkzeug 提供的用于发送文件的实用函数。
    # 它处理文件传输的实际细节，如设置响应头、处理文件对象等。
    # 通过 ** 解包运算符将准备好的关键字参数传递给 send_file 函数。
    return werkzeug.utils.send_file(  # type: ignore[return-value]
        # _prepare_send_file_kwargs 是一个辅助函数，用于准备发送文件时所需的关键字参数。
        # 它从当前请求和应用中获取必要的信息，并设置一些默认值。
        # 调用 _prepare_send_file_kwargs 函数，传递发送文件所需的参数，
        # 并将其结果作为关键字参数传递给 werkzeug.utils.send_file。
        **_prepare_send_file_kwargs(
            path_or_file=path_or_file,
            environ=request.environ,
            mimetype=mimetype,
            as_attachment=as_attachment,
            download_name=download_name,
            conditional=conditional,
            etag=etag,
            last_modified=last_modified,
            max_age=max_age,
        )
    )


# 用于从指定目录中安全地发送文件。
# 它封装了 Werkzeug 的 send_from_directory 函数，并添加了一些 Flask 特有的参数处理，
# 使得开发者可以更加灵活和方便地管理文件传输。通过使用 _prepare_send_file_kwargs 辅助函数，
# 这个函数可以从当前请求和应用中获取必要的信息，并设置一些默认值，从而简化了文件发送的过程。
def send_from_directory(
    # 指定文件所在的目录，相对于当前应用的根路径。
    directory: os.PathLike[str] | str,
    # 要发送的文件的路径，相对于 directory。
    path: os.PathLike[str] | str,
    # 传递给 send_file 函数的其他参数。
    **kwargs: t.Any,
) -> Response:
    """Send a file from within a directory using :func:`send_file`.

    .. code-block:: python

        @app.route("/uploads/<path:name>")
        def download_file(name):
            return send_from_directory(
                app.config['UPLOAD_FOLDER'], name, as_attachment=True
            )

    # 使用 werkzeug.security.safe_join 来确保路径的安全性。
    # 如果最终路径不是一个存在的常规文件，会引发 404 错误。

    This is a secure way to serve files from a folder, such as static
    files or uploads. Uses :func:`~werkzeug.security.safe_join` to
    ensure the path coming from the client is not maliciously crafted to
    point outside the specified directory.

    If the final path does not point to an existing regular file,
    raises a 404 :exc:`~werkzeug.exceptions.NotFound` error.

    :param directory: The directory that ``path`` must be located under,
        relative to the current application's root path.
    :param path: The path to the file to send, relative to
        ``directory``.
    :param kwargs: Arguments to pass to :func:`send_file`.

    .. versionchanged:: 2.0
        ``path`` replaces the ``filename`` parameter.

    .. versionadded:: 2.0
        Moved the implementation to Werkzeug. This is now a wrapper to
        pass some Flask-specific arguments.

    .. versionadded:: 0.5
    """
    # werkzeug.utils.send_from_directory 是 Werkzeug 提供的用于从目录中
    # 安全发送文件的实用函数。它确保路径安全，避免路径遍历攻击，并处理文件传输的实际细节。
    # 通过 ** 解包运算符将准备好的关键字参数传递给 send_from_directory 函数。
    return werkzeug.utils.send_from_directory(  # type: ignore[return-value]
        # _prepare_send_file_kwargs 是一个辅助函数，用于准备发送文件时所需的关键字参数。
        # 它从当前请求和应用中获取必要的信息，并设置一些默认值。
        directory, path, **_prepare_send_file_kwargs(**kwargs)
    )


# 用于找到包的根路径或包含模块的路径。如果找不到路径，则返回当前工作目录。
# 这在应用程序需要知道特定模块或包的文件系统位置时非常有用。
# 参数：import_name，类型为 str，表示要查找的包或模块的导入名称。
def get_root_path(import_name: str) -> str:
    """Find the root path of a package, or the path that contains a
    module. If it cannot be found, returns the current working
    directory.

    Not to be confused with the value returned by :func:`find_package`.

    :meta private:
    """
    # Module already imported and has a file attribute. Use that first.
    # 从 sys.modules 中获取模块对象。
    mod = sys.modules.get(import_name)

    # 如果模块已导入且有 __file__ 属性，则返回该文件的目录。
    if mod is not None and hasattr(mod, "__file__") and mod.__file__ is not None:
        return os.path.dirname(os.path.abspath(mod.__file__))

    # Next attempt: check the loader.
    try:
        # 尝试使用 importlib.util.find_spec 查找模块的规范（spec）。
        spec = importlib.util.find_spec(import_name)

        if spec is None:
            raise ValueError
    except (ImportError, ValueError):
        loader = None
    else:
        loader = spec.loader

    # Loader does not exist or we're referring to an unloaded main
    # module or a main module without path (interactive sessions), go
    # with the current working directory.
    # 如果加载器不存在或是主模块（如交互式会话中的主模块），则返回当前工作目录。
    if loader is None:
        return os.getcwd()

    # 如果加载器有 get_filename 方法，使用该方法获取文件路径。
    if hasattr(loader, "get_filename"):
        filepath = loader.get_filename(import_name)
    else:
        # 否则，使用 __import__ 导入模块并从 sys.modules 中获取模块对象，
        # 然后获取其 __file__ 属性。
        # Fall back to imports.
        __import__(import_name)
        mod = sys.modules[import_name]
        filepath = getattr(mod, "__file__", None)

        # If we don't have a file path it might be because it is a
        # namespace package. In this case pick the root path from the
        # first module that is contained in the package.
        # 如果文件路径为空，抛出运行时错误，提示无法找到根路径。
        if filepath is None:
            raise RuntimeError(
                "No root path can be found for the provided module"
                f" {import_name!r}. This can happen because the module"
                " came from an import hook that does not provide file"
                " name information or because it's a namespace package."
                " In this case the root path needs to be explicitly"
                " provided."
            )

    # 返回文件路径的目录。
    # filepath is import_name.py for a module, or __init__.py for a package.
    return os.path.dirname(os.path.abspath(filepath))  # type: ignore[no-any-return]


# 通过递归方式将包含点号的蓝图路径进行拆分，返回一个按层级排列的路径列表。
# 装饰器用于缓存函数的结果，以提高性能。maxsize=None 表示缓存大小不限制，即缓存所有调用结果。
@lru_cache(maxsize=None)
# 参数：name，类型为 str，表示要拆分的蓝图路径。
# 返回值类型：list[str]，返回一个字符串列表，包含拆分后的路径。
def _split_blueprint_path(name: str) -> list[str]:
    # 初始化一个名为 out 的列表，其中包含传入的 name 字符串。
    out: list[str] = [name]

    if "." in name:
        # 使用 name.rpartition(".")[0] 获取最后一个点号之前的部分，
        # 并递归调用 _split_blueprint_path，将结果扩展到 out 列表中。
        # rpartition 方法会将字符串分成三部分：最后一个点号之前的部分、点号本身、
        # 点号之后的部分。[0] 表示获取点号之前的部分。
        out.extend(_split_blueprint_path(name.rpartition(".")[0]))

    return out






