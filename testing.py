# 它从 Python 3.7 开始引入，用于提供更好的类型提示功能。
from __future__ import annotations

# Python 标准库中的一个模块，用于访问有关安装的包和模块元数据的信息。
import importlib.metadata

# typing 模块是 Python 3.5 及更高版本引入的一个标准库模块，
# 用于支持类型提示和类型注解，以提高代码的可读性和可维护性。
import typing as t

# contextlib 模块是 Python 标准库中的一个模块，用于支持上下文管理器的创建和使用。
# contextmanager 类是一个装饰器，用于定义一个生成器函数，该生成器函数可以生成上下文管理器。
from contextlib import contextmanager
# ExitStack 类是一个上下文管理器，它用于管理多个上下文管理器。
from contextlib import ExitStack

# copy 函数用于创建对象的浅拷贝。当修改原始列表的嵌套列表时，浅拷贝后的列表也会受到影响。
from copy import copy

# types定义了一些工具函数，用于协助动态创建新的类型。
# TracebackType 是 Python 的内置类型之一，用于表示异常的回溯信息（traceback）。
from types import TracebackType

# urlsplit 函数用于解析 URL（Uniform Resource Locator）字符串，
# 并将其拆分为不同的组成部分，如协议、域名、路径、查询参数和片段等。
from urllib.parse import urlsplit

# 用于测试和模拟 HTTP 请求和响应，以便测试 Web 应用程序的行为和功能。
import werkzeug.test

# CliRunner 类的主要作用是模拟命令行应用程序的运行，并允许你以编程方式发送命令、
# 模拟用户输入以及捕获应用程序的输出，从而进行单元测试和集成测试。
from click.testing import CliRunner

# Client 类的主要作用是允许你以编程方式构建 HTTP 请求，发送它们到你的 Web 应用程序，
# 然后检查和处理应用程序的响应。
from werkzeug.test import Client

# Request允许你轻松地访问请求的各个部分，并从中提取数据以处理和响应客户端请求。
from werkzeug.wrappers import Request as BaseRequest

from .cli import ScriptInfo
from .sessions import SessionMixin

if t.TYPE_CHECKING:  # pragma: no cover
    from werkzeug.test import TestResponse

    from .app import Flask

# 继承了 werkzeug.test.EnvironBuilder 类的所有属性和方法
class EnvironBuilder(werkzeug.test.EnvironBuilder):

    """An :class:`~werkzeug.test.EnvironBuilder`, that takes defaults from the
    application.

    :param app: The Flask application to configure the environment from.
    :param path: URL path being requested.
    :param base_url: Base URL where the app is being served, which
        ``path`` is relative to. If not given, built from
        :data:`PREFERRED_URL_SCHEME`, ``subdomain``,
        :data:`SERVER_NAME`, and :data:`APPLICATION_ROOT`.
    :param subdomain: Subdomain name to append to :data:`SERVER_NAME`.
    :param url_scheme: Scheme to use instead of
        :data:`PREFERRED_URL_SCHEME`.
    :param json: If given, this is serialized as JSON and passed as
        ``data``. Also defaults ``content_type`` to
        ``application/json``.
    :param args: other positional arguments passed to
        :class:`~werkzeug.test.EnvironBuilder`.
    :param kwargs: other keyword arguments passed to
        :class:`~werkzeug.test.EnvironBuilder`.
    """

    # 用于在创建类的实例（对象）时进行初始化操作。这个方法是类的构造函数。
    def __init__(
        self,
        app: Flask,
        path: str = "/",
        # str | None：这是类型提示，表示 base_url 参数的类型可以是字符串（str）
        # 或者 None，= None：这是默认值，表示如果调用函数时没有提供 base_url 
        # 参数的值，将默认为 None。
        base_url: str | None = None,
        subdomain: str | None = None,
        url_scheme: str | None = None,
        # 表示函数可以接受任意数量的位置参数，并且这些参数的类型可以是任意类型。
        # t.Any 是 Python 中的类型标注，表示类型可以是任何有效的类型。
        *args: t.Any,
        # 表示函数可以接受任意数量的关键字参数，并且这些参数的类型可以是任意类型。
        **kwargs: t.Any,
      # 函数或方法的返回类型注释，None：这表示函数或方法的返回值类型是 None，
      # 也就是没有返回值。  
    ) -> None:
        # assert（断言）用于判断一个表达式，在表达式条件为 false 的时候触发异常。
        # assert expression = if not expression: raise AssertionError
        assert not (base_url or subdomain or url_scheme) or (
            base_url is not None
        ) != bool(
            subdomain or url_scheme
            # 断言的错误消息
        ), 'Cannot pass "subdomain" or "url_scheme" with "base_url".'

        if base_url is None:
            http_host = app.config.get("SERVER_NAME") or "localhost"
            app_root = app.config["APPLICATION_ROOT"]

            if subdomain:
                #  f-string（格式化字符串）语法，构建了一个字符串。
                http_host = f"{subdomain}.{http_host}"

            if url_scheme is None:
                url_scheme = app.config["PREFERRED_URL_SCHEME"]

            url = urlsplit(path)
            base_url = (
                f"{url.scheme or url_scheme}://{url.netloc or http_host}"
                f"/{app_root.lstrip('/')}"
            )
            # 将 path 更新为解析后的 URL 中的路径部分。
            path = url.path

            # 处理 URL 查询参数的逻辑。
            if url.query:
                sep = b"?" if isinstance(url.query, bytes) else "?"
                path += sep + url.query

        self.app = app
        # 内置函数，用于获取父类（超类）的对象。
        super().__init__(path, base_url, *args, **kwargs)

    # 将对象 obj 序列化为一个 JSON 格式的字符串。
    def json_dumps(self, obj: t.Any, **kwargs: t.Any) -> str:  # type: ignore
        """Serialize ``obj`` to a JSON-formatted string.

        The serialization will be configured according to the config associated
        with this EnvironBuilder's ``app``.
        """

        # self.app：这是类的实例属性，它表示与该 EnvironBuilder 实例相关联的 Flask 应用对象。
        # self.app.json：这是应用对象的一个属性，它表示与 JSON 相关的配置和功能。
        # self.app.json.dumps(obj, **kwargs)：这一行代码调用应用对象的 json.dumps 
        # 方法来序列化输入的对象 obj。任何额外的关键字参数也会被传递给该方法。
        return self.app.json.dumps(obj, **kwargs)

_werkzeug_version = ""


def _get_werkzeug_version() -> str:
    global _werkzeug_version

    if not _werkzeug_version:
        _werkzeug_version = importlib.metadata.version("werkzeug")

    return _werkzeug_version

class FlaskClient(Client):
    """Works like a regular Werkzeug test client but has knowledge about
    Flask's contexts to defer the cleanup of the request context until
    the end of a ``with`` block. For general information about how to
    use this class refer to :class:`werkzeug.test.Client`.

    .. versionchanged:: 0.12
       `app.test_client()` includes preset default environment, which can be
       set after instantiation of the `app.test_client()` object in
       `client.environ_base`.

    Basic usage is outlined in the :doc:`/testing` chapter.
    """

    application: Flask

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        # 这一行代码为类的实例属性 preserve_context 赋了一个初始值 False。
        # 这个属性用于标志是否要保留上下文。
        self.preserve_context = False
        # 为类的实例属性 _new_contexts 赋了一个空列表作为初始值。
        # 这个属性用于存储新的上下文管理器（context manager）。
        self._new_contexts: list[t.ContextManager[t.Any]] = []
        # ExitStack 是 Python 的上下文管理器，用于管理一组上下文管理器，
        # 可以在退出上下文时自动清理资源。
        self._context_stack = ExitStack()
        # 环境变量用于模拟请求的环境。
        self.environ_base = {
            "REMOTE_ADDR": "127.0.0.1",
            "HTTP_USER_AGENT": f"Werkzeug/{_get_werkzeug_version()}",
        }

    # Python 装饰器，用于定义上下文管理器。它将函数装饰成一个生成器函数，
    # 使其可以与 with 语句一起使用。
    @contextmanager
    def session_transaction(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Generator[SessionMixin, None, None]:
        """When used in combination with a ``with`` statement this opens a
        session transaction.  This can be used to modify the session that
        the test client uses.  Once the ``with`` block is left the session is
        stored back.

        ::

            with client.session_transaction() as session:
                session['value'] = 42

        Internally this is implemented by going through a temporary test
        request context and since session handling could depend on
        request variables this function accepts the same arguments as
        :meth:`~flask.Flask.test_request_context` which are directly
        passed through.
        """

        # self._cookies 是一个对象属性，它可能用于存储客户端的 cookies。
        if self._cookies is None:
            raise TypeError(
                "Cookies are disabled. Create a client with 'use_cookies=True'."
            )

        app = self.application
        ctx = app.test_request_context(*args, **kwargs)
        self._add_cookies_to_wsgi(ctx.request.environ)

        # 这是一个上下文管理器的开始，它将进入 Flask 请求上下文（ctx）。
        with ctx:
            # 通过应用程序的会话接口 (app.session_interface) 来打开会话。
            # 返回一个会话对象 (sess)。
            sess = app.session_interface.open_session(app, ctx.request)

        if sess is None:
            raise RuntimeError("Session backend did not open a session.")

        # yield 语句将会话对象 (sess) 作为生成器的值返回。这允许在 with 
        # 语句块中的代码中使用会话对象，例如在测试中对会话进行操作。
        yield sess
        # 创建一个应用程序响应对象 (resp)，通常用于在上下文结束后保存会话状态。
        resp = app.response_class()

        if app.session_interface.is_null_session(sess):
            return

        # 再次进入 Flask 请求上下文，这次是为了保存会话到响应中。
        with ctx:
            app.session_interface.save_session(app, sess, resp)

        # 从响应中更新 cookies。它传递了主机名、请求路径和
        # 响应头中的 Set-Cookie 部分作为参数。
        self._update_cookies_from_response(
            ctx.request.host.partition(":")[0],
            ctx.request.path,
            resp.headers.getlist("Set-Cookie"),
        )

    # 将两个环境对象合并成一个新的环境字典，并在需要时添加额外的调试上下文信息。
    def _copy_environ(self, other):
        out = {**self.environ_base, **other}

        if self.preserve_context:
            out["werkzeug.debug.preserve_context"] = self._new_contexts.append

        return out

    # 创建一个请求对象，它使用 EnvironBuilder 来构建请求的环境，
    # 并通过合并和复制环境参数来创建请求对象。
    def _request_from_builder_args(self, args, kwargs):
        kwargs["environ_base"] = self._copy_environ(kwargs.get("environ_base", {}))
        builder = EnvironBuilder(self.application, *args, **kwargs)

        try:
            return builder.get_request()
        finally:
            builder.close()

    # 发送测试请求，并根据请求的不同方式创建请求对象。它还负责处理上下文的保留和恢复，
    # 以确保测试请求的环境隔离。最终，它返回测试响应对象，以供测试用例进一步分析和断言。
    def open(
        self,
        *args: t.Any,
        buffered: bool = False,
        follow_redirects: bool = False,
        **kwargs: t.Any,
    ) -> TestResponse:
        if args and isinstance(
            args[0], (werkzeug.test.EnvironBuilder, dict, BaseRequest)
        ):
            if isinstance(args[0], werkzeug.test.EnvironBuilder):
                builder = copy(args[0])
                builder.environ_base = self._copy_environ(builder.environ_base or {})
                request = builder.get_request()
            elif isinstance(args[0], dict):
                request = EnvironBuilder.from_environ(
                    args[0], app=self.application, environ_base=self._copy_environ({})
                ).get_request()
            else:
                # isinstance(args[0], BaseRequest)
                request = copy(args[0])
                request.environ = self._copy_environ(request.environ)
        else:
            # request is None
            request = self._request_from_builder_args(args, kwargs)

        # 清除之前保留的上下文，以防止它们在重定向或多个请求中的同一块中保留。
        self._context_stack.close()

        response = super().open(
            request,
            buffered=buffered,
            follow_redirects=follow_redirects,
        )
        response.json_module = self.application.json  # type: ignore[assignment]

        # 通过循环重新推送之前保留的上下文，以确保它们在请求期间保持不变。
        while self._new_contexts:
            cm = self._new_contexts.pop()
            self._context_stack.enter_context(cm)

        return response

    # 用于进入 Flask 客户端的上下文，当进入 with 语句块时，会设置 preserve_context 属性为 True，
    # 表示当前处于一个客户端上下文中。如果已经在客户端上下文中，则会引发异常以防止嵌套使用客户端。
    def __enter__(self) -> FlaskClient:
        if self.preserve_context:
            raise RuntimeError("Cannot nest client invocations")
        self.preserve_context = True
        return self

    # 在退出 Flask 客户端的上下文时，将 preserve_context 属性设置为 False，
    # 表示客户端上下文已经结束，并且关闭之前保留的上下文，以确保上下文资源得到释放。
    # 这是一种用于管理上下文的良好做法，以确保资源的正确释放和环境的清理。
    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.preserve_context = False
        self._context_stack.close()

# 用于测试 Flask 应用程序的命令行界面（CLI）命令的测试运行器。
class FlaskCliRunner(CliRunner):
    """A :class:`~click.testing.CliRunner` for testing a Flask app's
    CLI commands. Typically created using
    :meth:`~flask.Flask.test_cli_runner`. See :ref:`testing-cli`.
    """

    def __init__(self, app: Flask, **kwargs: t.Any) -> None:
        self.app = app
        super().__init__(**kwargs)

    def invoke(  # type: ignore
        self, cli: t.Any = None, args: t.Any = None, **kwargs: t.Any
    ) -> t.Any:
        """Invokes a CLI command in an isolated environment. See
        :meth:`CliRunner.invoke <click.testing.CliRunner.invoke>` for
        full method documentation. See :ref:`testing-cli` for examples.

        If the ``obj`` argument is not given, passes an instance of
        :class:`~flask.cli.ScriptInfo` that knows how to load the Flask
        app being tested.

        :param cli: Command object to invoke. Default is the app's
            :attr:`~flask.app.Flask.cli` group.
        :param args: List of strings to invoke the command with.

        :return: a :class:`~click.testing.Result` object.
        """
        if cli is None:
            cli = self.app.cli  # type: ignore

        if "obj" not in kwargs:
            kwargs["obj"] = ScriptInfo(create_app=lambda: self.app)

        return super().invoke(cli, args, **kwargs)

