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
























    
