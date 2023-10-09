# 它从 Python 3.7 开始引入，用于提供更好的类型提示功能。
from __future__ import annotations

# os模块负责程序与操作系统的交互，提供了访问操作系统底层的接口。
import os

# sys模块负责程序与python解释器的交互，提供了一系列的函数和变量，
# 用于操控python的运行时环境。
import sys

# typing 模块是 Python 3.5 及更高版本引入的一个标准库模块，
# 用于支持类型提示和类型注解，以提高代码的可读性和可维护性。
import typing as t

# 弱引用的主要用途是实现保存大对象的高速缓存或映射，
# 但又不希望大对象仅仅因为它出现在高速缓存或映射中而保持存活。
import weakref

# 容器的抽象基类
from collections.abc import Iterator as _abc_Iterator

# datetime基本日期和时间类型
# timedelta表示两个 date 对象或 time 对象，或者 datetime 对象之间的时间间隔，精确到微秒。
from datetime import timedelta

# inspect4种主要的功能: 类型检查、获取源代码、检查类与函数、检查解释器的调用堆栈。
# iscoroutinefunction: 如果对象是协程函数（使用 async def 语法定义的函数），则返回 True。
from inspect import iscoroutinefunction

# 创建一个迭代器，它首先返回第一个可迭代对象中所有元素，接着返回下一个可迭代对象中所有元素，
# 直到耗尽所有可迭代对象中的元素。可将多个序列处理为单个序列。
from itertools import chain

# types定义了一些工具函数，用于协助动态创建新的类型。
# TracebackType 是 Python 的内置类型之一，用于表示异常的回溯信息（traceback）。
from types import TracebackType

# urllib.parse用于将统一资源定位符（URL）字符串拆分为不同部分（协议、网络位置、路径等），
# 或将各个部分组合回 URL 字符串。quote使用 %xx 转义符替换 string 中的特殊字符。
from urllib.parse import quote as _url_quote

# 创建命令行界面 (CLI) 应用程序的 Python 库
import click

# Python的WSGI规范的实用函数库
# 创建、修改和处理 HTTP 请求或响应的头部信息。
from werkzeug.datastructures import Headers
# 表示一个不可变的字典，即一旦创建，就无法更改其内容。
from werkzeug.datastructures import ImmutableDict
# 通常用于表示客户端请求中的键错误或缺失。
from werkzeug.exceptions import BadRequestKeyError
# 用于表示 HTTP 协议相关的异常情况，例如客户端错误（4xx 错误）
# 和服务器错误（5xx 错误）等。
from werkzeug.exceptions import HTTPException
# 用于表示服务器内部错误的情况。
from werkzeug.exceptions import InternalServerError
# 用于处理 URL 构建错误的情况。
from werkzeug.routing import BuildError
# 用于执行 URL 到视图函数的映射，以及从视图函数生成 URL。
# 它允许你动态地构建 URL 和路由请求，以便与 Web 应用程序的路由系统进行交互。
from werkzeug.routing import MapAdapter
# 用于表示请求需要重定向到另一个 URL 的情况。
from werkzeug.routing import RequestRedirect
# 用于表示与 URL 路由相关的异常情况。
from werkzeug.routing import RoutingException
# 定义 URL 路由规则。
from werkzeug.routing import Rule
# 监视脚本文件的更改，并在文件更改时自动重新启动应用程序，
# 以便开发人员可以在不停止服务器的情况下进行代码修改和调试。
from werkzeug.serving import is_running_from_reloader
# 允许你构建和设置 HTTP 响应的各个部分，以便向客户端发送响应数据。
from werkzeug.wrappers import Response as BaseResponse

# 命令行应用
from . import cli

# 为框架的 API 提供类型提示，以提高代码的可读性、可维护性，并支持类型检查工具的使用。
from . import typing as ft

# 实现保存上下文所需的对象
# AppContext 类用于管理应用程序上下文，它包含应用程序的状态信息，
# 允许你在整个应用程序中共享数据。
from .ctx import AppContext
# RequestContext 类用于管理请求上下文，它包含有关当前请求的信息，
# 如请求对象、响应对象和请求特定的状态。
from .ctx import RequestContext

# globals 文件通常包含了一些全局变量和对象，
# 这些全局变量和对象用于在整个应用程序中存储和访问共享的数据。
from .globals import _cv_app
from .globals import _cv_request
from .globals import current_app
from .globals import g
from .globals import request
from .globals import request_ctx
from .globals import session

# helpers 文件通常包含了一些辅助函数和工具，用于执行各种任务，
# 例如处理请求、处理 URL、发送响应、管理会话等。
from .helpers import get_debug_flag
from .helpers import get_flashed_messages
from .helpers import get_load_dotenv
from .helpers import send_from_directory

# sansio 模块是 Flask 框架的核心部分，它提供了处理 HTTP 请求和响应、
# 路由分发、视图函数调用以及上下文管理等基本功能的实现。
from .sansio.app import App
from .sansio.scaffold import _sentinel

# 用于处理会话（Session）的相关代码。
from .sessions import SecureCookieSessionInterface
from .sessions import SessionInterface

# signals 文件通常包含用于处理信号和事件的相关代码。
# 信号和事件是一种机制，用于在特定的代码执行时触发自定义操作。
from .signals import appcontext_tearing_down
from .signals import got_request_exception
from .signals import request_finished
from .signals import request_started
from .signals import request_tearing_down

# templating 文件通常包含用于处理模板引擎的相关代码。
from .templating import Environment

# Request 和 Response 类以及其他相关功能通常用于实现 WSGI 规范。
# 这些类和功能允许 Flask 应用程序处理 HTTP 请求和生成 HTTP 响应，
# 从而与任何符合 WSGI 标准的 Web 服务器兼容。
from .wrappers import Request
from .wrappers import Response

# "pragma: no cover" 是一种代码注释，通常用于测试代码中，
# 以告诉测试工具不要计算或报告注释标记的代码段的测试覆盖率。
if t.TYPE_CHECKING:  # pragma: no cover
    from .testing import FlaskClient
    from .testing import FlaskCliRunner

# 主要作用是在类型提示中提供更具体的信息，以确保只有符合特定类型约束的函数才能
# 被传递给相应的上下文处理器、清理函数、模板过滤器、模板全局变量或模板测试函数。
# 这有助于提高代码的类型安全性和可读性。。
T_shell_context_processor = t.TypeVar(
    "T_shell_context_processor", bound=ft.ShellContextProcessorCallable
)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
T_template_filter = t.TypeVar("T_template_filter", bound=ft.TemplateFilterCallable)
T_template_global = t.TypeVar("T_template_global", bound=ft.TemplateGlobalCallable)
T_template_test = t.TypeVar("T_template_test", bound=ft.TemplateTestCallable)


# timedelta用于执行时间相关的计算
def _make_timedelta(value: timedelta | int | None) -> timedelta | None:
    if value is None or isinstance(value, timedelta):
        return value

    return timedelta(seconds=value)

class Flask(App):
    """The flask object implements a WSGI application and acts as the central
    object.  It is passed the name of the module or package of the
    application.  Once it is created it will act as a central registry for
    the view functions, the URL rules, template configuration and much more.

    The name of the package is used to resolve resources from inside the
    package or the folder the module is contained in depending on if the
    package parameter resolves to an actual python package (a folder with
    an :file:`__init__.py` file inside) or a standard module (just a ``.py`` file).

    For more information about resource loading, see :func:`open_resource`.

    Usually you create a :class:`Flask` instance in your main module or
    in the :file:`__init__.py` file of your package like this::

        from flask import Flask
        app = Flask(__name__)

    .. admonition:: About the First Parameter

        The idea of the first parameter is to give Flask an idea of what
        belongs to your application.  This name is used to find resources
        on the filesystem, can be used by extensions to improve debugging
        information and a lot more.

        So it's important what you provide there.  If you are using a single
        module, `__name__` is always the correct value.  If you however are
        using a package, it's usually recommended to hardcode the name of
        your package there.

        For example if your application is defined in :file:`yourapplication/app.py`
        you should create it with one of the two versions below::

            app = Flask('yourapplication')
            app = Flask(__name__.split('.')[0])

        Why is that?  The application will work even with `__name__`, thanks
        to how resources are looked up.  However it will make debugging more
        painful.  Certain extensions can make assumptions based on the
        import name of your application.  For example the Flask-SQLAlchemy
        extension will look for the code in your application that triggered
        an SQL query in debug mode.  If the import name is not properly set
        up, that debugging information is lost.  (For example it would only
        pick up SQL queries in `yourapplication.app` and not
        `yourapplication.views.frontend`)

    .. versionadded:: 0.7
       The `static_url_path`, `static_folder`, and `template_folder`
       parameters were added.

    .. versionadded:: 0.8
       The `instance_path` and `instance_relative_config` parameters were
       added.

    .. versionadded:: 0.11
       The `root_path` parameter was added.

    .. versionadded:: 1.0
       The ``host_matching`` and ``static_host`` parameters were added.

    .. versionadded:: 1.0
       The ``subdomain_matching`` parameter was added. Subdomain
       matching needs to be enabled manually now. Setting
       :data:`SERVER_NAME` does not implicitly enable it.

    :param import_name: the name of the application package
    :param static_url_path: can be used to specify a different path for the
                            static files on the web.  Defaults to the name
                            of the `static_folder` folder.
    :param static_folder: The folder with static files that is served at
        ``static_url_path``. Relative to the application ``root_path``
        or an absolute path. Defaults to ``'static'``.
    :param static_host: the host to use when adding the static route.
        Defaults to None. Required when using ``host_matching=True``
        with a ``static_folder`` configured.
    :param host_matching: set ``url_map.host_matching`` attribute.
        Defaults to False.
    :param subdomain_matching: consider the subdomain relative to
        :data:`SERVER_NAME` when matching routes. Defaults to False.
    :param template_folder: the folder that contains the templates that should
                            be used by the application.  Defaults to
                            ``'templates'`` folder in the root path of the
                            application.
    :param instance_path: An alternative instance path for the application.
                          By default the folder ``'instance'`` next to the
                          package or module is assumed to be the instance
                          path.
    :param instance_relative_config: if set to ``True`` relative filenames
                                     for loading the config are assumed to
                                     be relative to the instance path instead
                                     of the application root.
    :param root_path: The path to the root of the application files.
        This should only be set manually when it can't be detected
        automatically, such as for namespace packages.
    """

    default_config = ImmutableDict(
        {
            "DEBUG": None,
            "TESTING": False,
            "PROPAGATE_EXCEPTIONS": None,
            "SECRET_KEY": None,
            "PERMANENT_SESSION_LIFETIME": timedelta(days=31),
            "USE_X_SENDFILE": False,
            "SERVER_NAME": None,
            "APPLICATION_ROOT": "/",
            "SESSION_COOKIE_NAME": "session",
            "SESSION_COOKIE_DOMAIN": None,
            "SESSION_COOKIE_PATH": None,
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SECURE": False,
            "SESSION_COOKIE_SAMESITE": None,
            "SESSION_REFRESH_EACH_REQUEST": True,
            "MAX_CONTENT_LENGTH": None,
            "SEND_FILE_MAX_AGE_DEFAULT": None,
            "TRAP_BAD_REQUEST_ERRORS": None,
            "TRAP_HTTP_EXCEPTIONS": False,
            "EXPLAIN_TEMPLATE_LOADING": False,
            "PREFERRED_URL_SCHEME": "http",
            "TEMPLATES_AUTO_RELOAD": None,
            "MAX_COOKIE_SIZE": 4093,
        }
    )


    #: The class that is used for request objects.  See :class:`~flask.Request`
    #: for more information.
    request_class = Request

    #: The class that is used for response objects.  See
    #: :class:`~flask.Response` for more information.
    response_class = Response

    #: the session interface to use.  By default an instance of
    #: :class:`~flask.sessions.SecureCookieSessionInterface` is used here.
    #:
    #: .. versionadded:: 0.8
    # session_interface 是一个变量名，: 后面的 SessionInterface 是这个变量的类型注释，
    # 表示 session_interface 的类型应该是 SessionInterface。
    session_interface: SessionInterface = SecureCookieSessionInterface()


    def __init__(
        # 构造函数参数列表
        self,
        import_name: str,
        static_url_path: str | None = None,
        static_folder: str | os.PathLike | None = "static",
        static_host: str | None = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: str | os.PathLike | None = "templates",
        instance_path: str | None = None,
        instance_relative_config: bool = False,
        root_path: str | None = None,
    ):
        super().__init__(
            import_name=import_name,
            static_url_path=static_url_path,
            static_folder=static_folder,
            static_host=static_host,
            host_matching=host_matching,
            subdomain_matching=subdomain_matching,
            template_folder=template_folder,
            instance_path=instance_path,
            instance_relative_config=instance_relative_config,
            root_path=root_path,
        )

        # Add a static route using the provided static_url_path, static_host,
        # and static_folder if there is a configured static_folder.
        # Note we do this without checking if static_folder exists.
        # For one, it might be created while the server is running (e.g. during
        # development). Also, Google App Engine stores static files somewhere
        # 在 Flask 应用程序中添加一个静态路由，以便处理静态文件的请求。
        # has_static_folder位于sansio/scaffold.py中。
        if self.has_static_folder:
            assert (
                bool(static_host) == host_matching
            ), "Invalid static_host/host_matching combination"
            # Use a weakref to avoid creating a reference cycle between the app
            # and the view function (see #3761).
            self_ref = weakref.ref(self)
            # add_url_rule位于sansio/scaffold.py和sansio/blueprints.py中。
            self.add_url_rule(
                f"{self.static_url_path}/<path:filename>",
                endpoint="static",
                host=static_host,
                # 关键字lambda表示匿名函数，冒号前面的x表示函数参数。
                view_func=lambda **kw: self_ref().send_static_file(**kw),  # type: ignore # noqa: B950
            )

    # 在发送文件时设置缓存的最大寿命（max_age）。缓存控制是通过 HTTP 头来实现的，
    # 它告诉浏览器在多长时间内可以使用缓存的文件，而不需要重新请求服务器。
    # 这可以提高 Web 应用程序的性能和加载速度。
    def get_send_file_max_age(self, filename: str | None) -> int | None:
        """Used by :func:`send_file` to determine the ``max_age`` cache
        value for a given file path if it wasn't passed.

        By default, this returns :data:`SEND_FILE_MAX_AGE_DEFAULT` from
        the configuration of :data:`~flask.current_app`. This defaults
        to ``None``, which tells the browser to use conditional requests
        instead of a timed cache, which is usually preferable.

        Note this is a duplicate of the same method in the Flask
        class.

        .. versionchanged:: 2.0
            The default configuration is ``None`` instead of 12 hours.

        .. versionadded:: 0.9
        """
        value = current_app.config["SEND_FILE_MAX_AGE_DEFAULT"]

        if value is None:
            return None

        # 如果 SEND_FILE_MAX_AGE_DEFAULT 的配置值是一个 timedelta 对象（时间间隔），
        # 则将其转换为秒数并返回。
        if isinstance(value, timedelta):
            # total_seconds() 是 Python 中 timedelta 对象的方法，
            # 用于获取时间间隔（timedelta）的总秒数。
            return int(value.total_seconds())

        # 如果 SEND_FILE_MAX_AGE_DEFAULT 的配置值是一个整数，则直接返回该整数。
        return value

    # 用于从 static_folder 目录中提供静态文件的视图函数。
    def send_static_file(self, filename: str) -> Response:
        """The view function used to serve files from
        :attr:`static_folder`. A route is automatically registered for
        this view at :attr:`static_url_path` if :attr:`static_folder` is
        set.

        Note this is a duplicate of the same method in the Flask
        class.

        .. versionadded:: 0.5

        """
        if not self.has_static_folder:
            raise RuntimeError("'static_folder' must be set to serve static_files.")

        # send_file only knows to call get_send_file_max_age on the app,
        # call it here so it works for blueprints too.
        max_age = self.get_send_file_max_age(filename)
        # get_send_file_max_age位于helpers.py，
        return send_from_directory(
            # cast() 是 Python 中的一个函数，通常用于执行类型转换或强制类型断言。
            t.cast(str, self.static_folder), filename, max_age=max_age
        )














