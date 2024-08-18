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


# 获取当前安装的 Werkzeug 库的版本号，并将其缓存为全局变量。
# 通过使用全局变量缓存版本号，它避免了在多次调用时重复执行获取版本号的操作，从而提高了性能。
# Werkzeug 是 Flask 的底层 WSGI 工具包，Flask 使用它来处理 HTTP 请求和响应。
def _get_werkzeug_version() -> str:
    global _werkzeug_version

    if not _werkzeug_version:
        # importlib.metadata.version 是 Python 标准库中的一个方法，用于获取已安装的 Python 包的版本号。
        _werkzeug_version = importlib.metadata.version("werkzeug")

    return _werkzeug_version


# FlaskClient 类是 Flask 测试客户端的实现，它继承自 Werkzeug 的 Client 类，
# 并扩展了对 Flask 应用上下文的支持。这个类使得开发者可以在测试 Flask 应用时更方便
# 地管理应用上下文和请求上下文，并在测试期间模拟客户端的行为，如发送请求、管理会话等。
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

    # 声明了与 FlaskClient 关联的 Flask 应用实例。
    application: Flask

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        # 调用父类 Client 的构造函数，将所有传入参数传递给父类。
        super().__init__(*args, **kwargs)
        # 初始化 preserve_context 属性为 False，用于控制上下文是否在请求后保留。
        self.preserve_context = False
        # 初始化一个空列表，用于存储新创建的上下文管理器。
        self._new_contexts: list[t.ContextManager[t.Any]] = []
        # 创建一个 ExitStack 实例，用于管理多个上下文管理器。
        self._context_stack = ExitStack()
        # 字典，存储请求的默认环境变量。
        self.environ_base = {
            "REMOTE_ADDR": "127.0.0.1",
            "HTTP_USER_AGENT": f"Werkzeug/{_get_werkzeug_version()}",
        }

    # 装饰器：将方法定义为上下文管理器，允许与 with 语句一起使用。
    @contextmanager
    # 创建一个会话事务，使得在 with 语句块中可以修改客户端会话。
    def session_transaction(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Iterator[SessionMixin]:
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
        # 如果客户端禁用了 Cookies，则抛出 TypeError。
        if self._cookies is None:
            raise TypeError(
                "Cookies are disabled. Create a client with 'use_cookies=True'."
            )

        app = self.application
        # 通过 app.test_request_context 方法创建一个请求上下文 ctx，
        ctx = app.test_request_context(*args, **kwargs)
        # 并将当前会话的 Cookies 添加到 WSGI 环境中。
        self._add_cookies_to_wsgi(ctx.request.environ)

        # 在请求上下文中调用 open_session 方法打开一个会话对象 sess。
        with ctx:
            sess = app.session_interface.open_session(app, ctx.request)

        # 如果无法打开会话，则抛出 RuntimeError。
        if sess is None:
            raise RuntimeError("Session backend did not open a session.")

        # 使用 yield 关键字将会话对象 sess 传递给 with 语句块，
        # 并在退出 with 语句块时生成一个响应对象 resp。
        yield sess
        resp = app.response_class()

        # 检查会话是否为空：如果会话是空的（即 is_null_session 返回 True），则不保存会话，直接返回。
        if app.session_interface.is_null_session(sess):
            return

        # 在请求上下文中调用 save_session 方法保存会话。
        with ctx:
            app.session_interface.save_session(app, sess, resp)

        # 根据响应头中的 Set-Cookie 更新客户端的 Cookies。
        self._update_cookies_from_response(
            ctx.request.host.partition(":")[0],
            ctx.request.path,
            resp.headers.getlist("Set-Cookie"),
        )

    # 复制并合并环境变量字典 other 和 environ_base，并在需要时保留上下文。
    def _copy_environ(self, other: WSGIEnvironment) -> WSGIEnvironment:
        # 合并 self.environ_base 和 other，生成一个新的环境变量字典 out。
        out = {**self.environ_base, **other}

        # 如果 preserve_context 为 True，则在环境变量中添加 werkzeug.debug.preserve_context。
        if self.preserve_context:
            out["werkzeug.debug.preserve_context"] = self._new_contexts.append

        return out

    # 从构造器参数中生成一个请求对象 BaseRequest。
    def _request_from_builder_args(
        self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
    ) -> BaseRequest:
        # 将更新后的环境变量传递给 kwargs。
        kwargs["environ_base"] = self._copy_environ(kwargs.get("environ_base", {}))
        # 创建一个 EnvironBuilder 对象，用于生成请求。
        builder = EnvironBuilder(self.application, *args, **kwargs)

        # 通过 builder.get_request() 生成请求对象，并在最终关闭 builder。
        try:
            return builder.get_request()
        finally:
            builder.close()

    # 模拟客户端请求，返回 TestResponse 对象。
    def open(
        self,
        *args: t.Any,
        buffered: bool = False,
        follow_redirects: bool = False,
        **kwargs: t.Any,
    ) -> TestResponse:
        # 处理传入的参数：根据 args 的类型不同，处理请求对象的生成。
        if args and isinstance(
            args[0], (werkzeug.test.EnvironBuilder, dict, BaseRequest)
        ):
            if isinstance(args[0], werkzeug.test.EnvironBuilder):
                builder = copy(args[0])
                builder.environ_base = self._copy_environ(builder.environ_base or {})  # type: ignore[arg-type]
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

        # Pop any previously preserved contexts. This prevents contexts
        # from being preserved across redirects or multiple requests
        # within a single block.
        # 关闭上下文栈：清除任何之前保留的上下文，防止跨请求的上下文混淆。
        self._context_stack.close()

        # 调用父类 open 方法：发送请求并接收响应。将 Flask 应用的 JSON 模块分配给响应对象。
        response = super().open(
            request,
            buffered=buffered,
            follow_redirects=follow_redirects,
        )
        response.json_module = self.application.json  # type: ignore[assignment]

        # Re-push contexts that were preserved during the request.
        # 重新推送保留的上下文：将 _new_contexts 中的上下文重新推送到上下文栈中。
        while self._new_contexts:
            cm = self._new_contexts.pop()
            self._context_stack.enter_context(cm)

        return response

    # 当 FlaskClient 作为上下文管理器使用时调用，
    # 设置 preserve_context 为 True，并返回自身实例。
    def __enter__(self) -> FlaskClient:
        if self.preserve_context:
            raise RuntimeError("Cannot nest client invocations")
        self.preserve_context = True
        return self

    # 实现上下文管理协议的一部分，当 FlaskClient 对象退出 with 语句块时自动调用。
    # 它用于清理在 with 语句块期间创建的上下文并执行相应的资源释放操作。
    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.preserve_context = False
        self._context_stack.close()


# FlaskCliRunner 类通过继承 CliRunner 并添加与 Flask 应用集成的功能，
# 使得测试 Flask 应用的命令行接口变得更加方便。它自动管理 Flask 应用的上下文，
# 并允许开发者在测试时模拟 CLI 命令的执行。
class FlaskCliRunner(CliRunner):
    """A :class:`~click.testing.CliRunner` for testing a Flask app's
    CLI commands. Typically created using
    :meth:`~flask.Flask.test_cli_runner`. See :ref:`testing-cli`.
    """

    def __init__(self, app: Flask, **kwargs: t.Any) -> None:
        self.app = app
        # 调用父类 CliRunner 的构造函数，传递所有关键字参数 kwargs。
        # 这允许继承父类的功能，同时保留 Flask 应用的上下文。
        super().__init__(**kwargs)

    # 用于在一个隔离的环境中调用 CLI 命令。
    # 它扩展了 click.testing.CliRunner.invoke 方法，增加了对 Flask 应用的支持。
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
        # 如果 cli 为 None，则使用 Flask 应用实例的 cli 命令组 (self.app.cli) 作为默认值。
        if cli is None:
            cli = self.app.cli

        # 如果关键字参数 kwargs 中没有传递 obj，则默认设置一个 ScriptInfo 对象。
        # ScriptInfo 是一个存储脚本执行相关信息的对象，它通过 create_app 函数来提供 Flask 应用实例。
        if "obj" not in kwargs:
            kwargs["obj"] = ScriptInfo(create_app=lambda: self.app)

        return super().invoke(cli, args, **kwargs)




