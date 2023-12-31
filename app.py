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

    # 打开相对于类的root_path的资源文件以进行读取，root_path包含了应用程序的核心代码和静态资源，
    # 在应用程序的开发和部署过程中不会频繁变动。
    # t.IO[t.AnyStr]表示一个可以进行输入/输出操作的对象，可以是字符串或字节串，具体取决于上下文。
    def open_resource(self, resource: str, mode: str = "rb") -> t.IO[t.AnyStr]:
        """Open a resource file relative to :attr:`root_path` for
        reading.

        For example, if the file ``schema.sql`` is next to the file
        ``app.py`` where the ``Flask`` app is defined, it can be opened
        with:

        .. code-block:: python

            with app.open_resource("schema.sql") as f:
                conn.executescript(f.read())

        :param resource: Path to the resource relative to
            :attr:`root_path`.
        :param mode: Open the file in this mode. Only reading is
            supported, valid values are "r" (or "rt") and "rb".

        Note this is a duplicate of the same method in the Flask
        class.

        """
        if mode not in {"r", "rt", "rb"}:
            raise ValueError("Resources can only be opened for reading.")

        # 
        return open(os.path.join(self.root_path, resource), mode)

    # 用于打开应用程序实例文件夹（instance_path）中的资源文件。
    # 应用程序实例文件夹，通常用于存储应用程序实例特定的数据和配置文件。
    # 在一个博客应用中，instance_path 可能用于存储用户上传的文章图片、
    # 用户配置文件、应用程序日志等。这些文件是在运行时动态创建和修改的。
    def open_instance_resource(self, resource: str, mode: str = "rb") -> t.IO[t.AnyStr]:
        """Opens a resource from the application's instance folder
        (:attr:`instance_path`).  Otherwise works like
        :meth:`open_resource`.  Instance resources can also be opened for
        writing.

        :param resource: the name of the resource.  To access resources within
                         subfolders use forward slashes as separator.
        :param mode: resource file opening mode, default is 'rb'.
        """
        return open(os.path.join(self.instance_path, resource), mode)

    # 设置了一个Jinja2环境，并添加了各种选项，同时将Flask特定的函数和对象
    # 添加到环境的全局上下文中，以便在模板中使用。
    # 返回一个 Environment 类的实例，Environment类位于templating.py。
    def create_jinja_environment(self) -> Environment:
        """Create the Jinja environment based on :attr:`jinja_options`
        and the various Jinja-related methods of the app. Changing
        :attr:`jinja_options` after this will have no effect. Also adds
        Flask-related globals and filters to the environment.

        .. versionchanged:: 0.11
           ``Environment.auto_reload`` set in accordance with
           ``TEMPLATES_AUTO_RELOAD`` configuration option.

        .. versionadded:: 0.5
        """
        # 创建一个名为 options 的字典，初始值为 Flask 应用程序对象
        #（self）的 jinja_options 属性。
        options = dict(self.jinja_options)

        if "autoescape" not in options:
            options["autoescape"] = self.select_jinja_autoescape

        if "auto_reload" not in options:
            auto_reload = self.config["TEMPLATES_AUTO_RELOAD"]

            if auto_reload is None:
                auto_reload = self.debug

            options["auto_reload"] = auto_reload

        rv = self.jinja_environment(self, **options)
        # 用于将各种与Flask相关的函数和对象添加到Jinja2环境的全局上下文中，
        # 从而使它们可以在模板中访问。
        rv.globals.update(
            url_for=self.url_for,
            get_flashed_messages=get_flashed_messages,
            config=self.config,
            # request, session and g are normally added with the
            # context processor for efficiency reasons but for imported
            # templates we also want the proxies in there.
            request=request,
            session=session,
            g=g,
        )
        rv.policies["json.dumps_function"] = self.json.dumps
        return rv

    # 用于为给定的请求创建URL适配器。URL适配器用于处理URL路由和生成，
    # 它允许应用程序将URL映射到视图函数并根据应用程序中定义的路由生成URL。
    def create_url_adapter(self, request: Request | None) -> MapAdapter | None:
        """Creates a URL adapter for the given request. The URL adapter
        is created at a point where the request context is not yet set
        up so the request is passed explicitly.

        .. versionadded:: 0.6

        .. versionchanged:: 0.9
           This can now also be called without a request object when the
           URL adapter is created for the application context.

        .. versionchanged:: 1.0
            :data:`SERVER_NAME` no longer implicitly enables subdomain
            matching. Use :attr:`subdomain_matching` instead.
        """
        if request is not None:
            # If subdomain matching is disabled (the default), use the
            # default subdomain in all cases. This should be the default
            # in Werkzeug but it currently does not have that feature.
            # url_map是一个werkzeug.routing.Map对象，位于sansio/app.py
            if not self.subdomain_matching:
                subdomain = self.url_map.default_subdomain or None
            else:
                subdomain = None

            return self.url_map.bind_to_environ(
                request.environ,
                server_name=self.config["SERVER_NAME"],
                subdomain=subdomain,
            )
        # We need at the very least the server name to be set for this
        # to work.
        if self.config["SERVER_NAME"] is not None:
            return self.url_map.bind(
                self.config["SERVER_NAME"],
                script_name=self.config["APPLICATION_ROOT"],
                url_scheme=self.config["PREFERRED_URL_SCHEME"],
            )

        return None

    # 引发路由异常。
    # 确保在Flask应用程序的调试模式下，当路由引发重定向并且请求的HTTP方法适用时，
    # 不会丢弃请求的主体内容。
    def raise_routing_exception(self, request: Request) -> t.NoReturn:
        """Intercept routing exceptions and possibly do something else.

        In debug mode, intercept a routing redirect and replace it with
        an error if the body will be discarded.

        With modern Werkzeug this shouldn't occur, since it now uses a
        308 status which tells the browser to resend the method and
        body.

        .. versionchanged:: 2.1
            Don't intercept 307 and 308 redirects.

        :meta private:
        :internal:
        """
        if (
            not self.debug
            or not isinstance(request.routing_exception, RequestRedirect)
            or request.routing_exception.code in {307, 308}
            or request.method in {"GET", "HEAD", "OPTIONS"}
        ):
            raise request.routing_exception  # type: ignore

        from .debughelpers import FormDataRoutingRedirect

        raise FormDataRoutingRedirect(request)

    # 更新模板上下文，向模板上下文中添加一些常用的变量。
    # 有助于模板引擎在生成HTML页面时使用这些数据。
    # request：当前请求对象，包含有关客户端请求的信息。
    # session：会话对象，用于在多个请求之间存储数据。
    # config：应用程序的配置信息。
    # g：全局变量，通常用于在请求生命周期内存储临时数据。
    def update_template_context(self, context: dict) -> None:
        """Update the template context with some commonly used variables.
        This injects request, session, config and g into the template
        context as well as everything template context processors want
        to inject.  Note that the as of Flask 0.6, the original values
        in the context will not be overridden if a context processor
        decides to return a value with the same key.

        :param context: the context as a dictionary that is updated in place
                        to add extra variables.
        """
        # 类型提示，names 的预期类型是一个可迭代对象，
        # 该对象包含字符串 (str) 或 None 值。
        names: t.Iterable[str | None] = (None,)

        # A template may be rendered outside a request context.
        # reversed()函数是内置函数，用于反转一个序列的元素。
        # chain()将多个可迭代对象合并成一个单一的迭代器，顺序地迭代它们的元素。
        if request:
            names = chain(names, reversed(request.blueprints))

        # The values passed to render_template take precedence. Keep a
        # copy to re-apply after all context functions.
        # 保存模板上下文的原始值
        orig_ctx = context.copy()

        for name in names:
            # 位于scaffold.py
            if name in self.template_context_processors:
                for func in self.template_context_processors[name]:
                    context.update(self.ensure_sync(func)())

        context.update(orig_ctx)

    # 用于创建一个包含了应用程序和其他相关变量的上下文字典，
    # 以便在交互式Shell中可以轻松地访问这些变量。
    def make_shell_context(self) -> dict:
        """Returns the shell context for an interactive shell for this
        application.  This runs all the registered shell context
        processors.

        .. versionadded:: 0.11
        """
        rv = {"app": self, "g": g}
        # shell_context_processors 位于sansio/app.py
        # self.shell_context_processors: 
        #    list[ft.ShellContextProcessorCallable] = []
        # 定义了一个属性，用于存储 shell 上下文处理器函数的列表。
        for processor in self.shell_context_processors:
            rv.update(processor())
        return rv

    # 在本地服务器上运行应用程序。
    def run(
        self,
        host: str | None = None,
        port: int | None = None,
        debug: bool | None = None,
        load_dotenv: bool = True,
        **options: t.Any,
    ) -> None:
        """Runs the application on a local development server.

        Do not use ``run()`` in a production setting. It is not intended to
        meet security and performance requirements for a production server.
        Instead, see :doc:`/deploying/index` for WSGI server recommendations.

        If the :attr:`debug` flag is set the server will automatically reload
        for code changes and show a debugger in case an exception happened.

        If you want to run the application in debug mode, but disable the
        code execution on the interactive debugger, you can pass
        ``use_evalex=False`` as parameter.  This will keep the debugger's
        traceback screen active, but disable code execution.

        It is not recommended to use this function for development with
        automatic reloading as this is badly supported.  Instead you should
        be using the :command:`flask` command line script's ``run`` support.

        .. admonition:: Keep in Mind

           Flask will suppress any server error with a generic error page
           unless it is in debug mode.  As such to enable just the
           interactive debugger without the code reloading, you have to
           invoke :meth:`run` with ``debug=True`` and ``use_reloader=False``.
           Setting ``use_debugger`` to ``True`` without being in debug mode
           won't catch any exceptions because there won't be any to
           catch.

        :param host: the hostname to listen on. Set this to ``'0.0.0.0'`` to
            have the server available externally as well. Defaults to
            ``'127.0.0.1'`` or the host in the ``SERVER_NAME`` config variable
            if present.
        :param port: the port of the webserver. Defaults to ``5000`` or the
            port defined in the ``SERVER_NAME`` config variable if present.
        :param debug: if given, enable or disable debug mode. See
            :attr:`debug`.
        :param load_dotenv: Load the nearest :file:`.env` and :file:`.flaskenv`
            files to set environment variables. Will also change the working
            directory to the directory containing the first file found.
        :param options: the options to be forwarded to the underlying Werkzeug
            server. See :func:`werkzeug.serving.run_simple` for more
            information.

        .. versionchanged:: 1.0
            If installed, python-dotenv will be used to load environment
            variables from :file:`.env` and :file:`.flaskenv` files.

            The :envvar:`FLASK_DEBUG` environment variable will override :attr:`debug`.

            Threaded mode is enabled by default.

        .. versionchanged:: 0.10
            The default port is now picked from the ``SERVER_NAME``
            variable.
        """
        # Ignore this call so that it doesn't start another server if
        # the 'flask run' command is used.
        if os.environ.get("FLASK_RUN_FROM_CLI") == "true":
            # 检查应用程序是否是通过重新加载（reloader）启动的。
            if not is_running_from_reloader():
                # click.secho() 函数用于在命令行中输出文本。
                click.secho(
                    " * Ignoring a call to 'app.run()' that would block"
                    " the current 'flask' CLI command.\n"
                    "   Only call 'app.run()' in an 'if __name__ =="
                    ' "__main__"\' guard.',
                    # fg="red" 是用于控制命令行文本颜色的参数。
                    fg="red",
                )

            return

        # 确定是否应该加载环境变量文件（.env 和 .flaskenv）。
        if get_load_dotenv(load_dotenv):
            # 加载最近的 .env 和 .flaskenv 文件以设置环境变量。
            cli.load_dotenv()

            # if set, env var overrides existing value
            if "FLASK_DEBUG" in os.environ:
                self.debug = get_debug_flag()

        # debug passed to method overrides all other sources
        if debug is not None:
            self.debug = bool(debug)

        # 用于确定应用程序在开发服务器上监听的主机和端口。
        server_name = self.config.get("SERVER_NAME")
        sn_host = sn_port = None

        if server_name:
            # str.partition(":") 方法，将 server_name 按照 ":" 分割为三部分，
            # 即主机名、冒号、端口号。
            sn_host, _, sn_port = server_name.partition(":")

        if not host:
            if sn_host:
                host = sn_host
            else:
                host = "127.0.0.1"

        if port or port == 0:
            port = int(port)
        elif sn_port:
            port = int(sn_port)
        else:
            port = 5000

        options.setdefault("use_reloader", self.debug)
        options.setdefault("use_debugger", self.debug)
        options.setdefault("threaded", True)

        # 在命令行中显示服务器的启动横幅（banner）。
        # 这个横幅通常包含应用程序的名称和调试模式的信息。它用于提醒开发者服务器正在运行。
        cli.show_server_banner(self.debug, self.name)

        # run_simple 是 Werkzeug 库中用于启动服务器的函数。
        from werkzeug.serving import run_simple

        try:
            # 启动服务器，并开始监听指定的主机和端口，处理应用程序的请求。
            # t.cast(str, host) 是将主机名强制转换为字符串类型。
            run_simple(t.cast(str, host), port, self, **options)
        finally:
            # reset the first request information if the development server
            # reset normally.  This makes it possible to restart the server
            # without reloader and that stuff from an interactive shell.
            self._got_first_request = False

    # 创建一个用于测试的客户端对象。
    def test_client(self, use_cookies: bool = True, **kwargs: t.Any) -> FlaskClient:
        """Creates a test client for this application.  For information
        about unit testing head over to :doc:`/testing`.

        Note that if you are testing for assertions or exceptions in your
        application code, you must set ``app.testing = True`` in order for the
        exceptions to propagate to the test client.  Otherwise, the exception
        will be handled by the application (not visible to the test client) and
        the only indication of an AssertionError or other exception will be a
        500 status code response to the test client.  See the :attr:`testing`
        attribute.  For example::

            app.testing = True
            client = app.test_client()

        The test client can be used in a ``with`` block to defer the closing down
        of the context until the end of the ``with`` block.  This is useful if
        you want to access the context locals for testing::

            with app.test_client() as c:
                rv = c.get('/?vodka=42')
                assert request.args['vodka'] == '42'

        Additionally, you may pass optional keyword arguments that will then
        be passed to the application's :attr:`test_client_class` constructor.
        For example::

            from flask.testing import FlaskClient

            class CustomClient(FlaskClient):
                def __init__(self, *args, **kwargs):
                    self._authentication = kwargs.pop("authentication")
                    super(CustomClient,self).__init__( *args, **kwargs)

            app.test_client_class = CustomClient
            client = app.test_client(authentication='Basic ....')

        See :class:`~flask.testing.FlaskClient` for more information.

        .. versionchanged:: 0.4
           added support for ``with`` block usage for the client.

        .. versionadded:: 0.7
           The `use_cookies` parameter was added as well as the ability
           to override the client to be used by setting the
           :attr:`test_client_class` attribute.

        .. versionchanged:: 0.11
           Added `**kwargs` to support passing additional keyword arguments to
           the constructor of :attr:`test_client_class`.
        """
        cls = self.test_client_class
        if cls is None:
            from .testing import FlaskClient as cls
        return cls(  # type: ignore
            self, self.response_class, use_cookies=use_cookies, **kwargs
        )

    # 创建用于测试命令行界面 (CLI) 命令的 CLI 运行器。
    def test_cli_runner(self, **kwargs: t.Any) -> FlaskCliRunner:
        """Create a CLI runner for testing CLI commands.
        See :ref:`testing-cli`.

        Returns an instance of :attr:`test_cli_runner_class`, by default
        :class:`~flask.testing.FlaskCliRunner`. The Flask app object is
        passed as the first argument.

        .. versionadded:: 1.0
        """
        cls = self.test_cli_runner_class

        if cls is None:
            from .testing import FlaskCliRunner as cls

        return cls(self, **kwargs)  # type: ignore


    # 处理 HTTP 异常的核心方法，它通过查找适当的错误处理程序，调用它，
    # 并返回处理程序的结果或原始异常，以实现对异常的处理。
    def handle_http_exception(
        self, e: HTTPException
    ) -> HTTPException | ft.ResponseReturnValue:
        """Handles an HTTP exception.  By default this will invoke the
        registered error handlers and fall back to returning the
        exception as response.

        .. versionchanged:: 1.0.3
            ``RoutingException``, used internally for actions such as
             slash redirects during routing, is not passed to error
             handlers.

        .. versionchanged:: 1.0
            Exceptions are looked up by code *and* by MRO, so
            ``HTTPException`` subclasses can be handled with a catch-all
            handler for the base ``HTTPException``.

        .. versionadded:: 0.3
        """
        # Proxy exceptions don't have error codes.  We want to always return
        # those unchanged as errors
        # 如果传入的 HTTP 异常 e 是代理异常（Proxy exceptions），
        # 即没有错误代码（code 属性为 None），则直接返回异常 e。
        if e.code is None:
            return e

        # 如果 e 是 RoutingException 的实例，它表示在路由过程中触发的操作，
        # 例如斜杠重定向。在这种情况下，直接返回异常 e，不调用错误处理程序。
        # RoutingExceptions are used internally to trigger routing
        # actions, such as slash redirects raising RequestRedirect. They
        # are not raised or handled in user code.
        if isinstance(e, RoutingException):
            return e

        # 通过调用 _find_error_handler 方法查找适当的错误处理程序。
        # 该方法考虑了异常的错误代码以及请求上下文中的蓝图（blueprints）信息。
        handler = self._find_error_handler(e, request.blueprints)
        # 如果没有找到适当的错误处理程序，则直接返回异常 e。
        if handler is None:
            return e
        # 如果找到错误处理程序，则调用 ensure_sync 方法同步执行该处理程序，
        # 并传递异常 e 作为参数。然后，返回处理程序的返回值。
        # 确保错误处理程序是同步执行的。这对于与异步代码进行交互或在同步代码中
        # 使用异步错误处理程序时非常重要。
        return self.ensure_sync(handler)(e)


    # 用于处理用户自定义异常的核心方法。
    def handle_user_exception(
        self, e: Exception
    ) -> HTTPException | ft.ResponseReturnValue:
        """This method is called whenever an exception occurs that
        should be handled. A special case is :class:`~werkzeug
        .exceptions.HTTPException` which is forwarded to the
        :meth:`handle_http_exception` method. This function will either
        return a response value or reraise the exception with the same
        traceback.

        .. versionchanged:: 1.0
            Key errors raised from request data like ``form`` show the
            bad key in debug mode rather than a generic bad request
            message.

        .. versionadded:: 0.7
        """
        if isinstance(e, BadRequestKeyError) and (
            self.debug or self.config["TRAP_BAD_REQUEST_ERRORS"]
        ):
            e.show_exception = True

        if isinstance(e, HTTPException) and not self.trap_http_exception(e):
            return self.handle_http_exception(e)

        handler = self._find_error_handler(e, request.blueprints)

        if handler is None:
            raise

        return self.ensure_sync(handler)(e)


    # 用于处理未关联错误处理程序的异常，或者从错误处理程序中引发的异常。
    def handle_exception(self, e: Exception) -> Response:
        """Handle an exception that did not have an error handler
        associated with it, or that was raised from an error handler.
        This always causes a 500 ``InternalServerError``.

        Always sends the :data:`got_request_exception` signal.

        If :data:`PROPAGATE_EXCEPTIONS` is ``True``, such as in debug
        mode, the error will be re-raised so that the debugger can
        display it. Otherwise, the original exception is logged, and
        an :exc:`~werkzeug.exceptions.InternalServerError` is returned.

        If an error handler is registered for ``InternalServerError`` or
        ``500``, it will be used. For consistency, the handler will
        always receive the ``InternalServerError``. The original
        unhandled exception is available as ``e.original_exception``.

        .. versionchanged:: 1.1.0
            Always passes the ``InternalServerError`` instance to the
            handler, setting ``original_exception`` to the unhandled
            error.

        .. versionchanged:: 1.1.0
            ``after_request`` functions and other finalization is done
            even for the default 500 response when there is no handler.

        .. versionadded:: 0.3
        """
        # sys.exc_info() 是 Python 标准库中 sys 模块提供的方法，
        # 用于获取当前线程的异常信息，返回一个包含三个值的元组 (type, value, traceback)
        exc_info = sys.exc_info()
        # 在发生请求异常时触发 got_request_exception 信号，
        # 并将异常对象传递给与该信号关联的所有处理函数。
        # got_request_exception.send 将触发与该信号关联的所有处理函数。
        # self是信号发送者，即发送信号的对象。在这里，是 Flask 应用程序对象。
        # _async_wrapper=self.ensure_sync用于指定信号的异步包装器。
        # 将异常对象 e 传递给 got_request_exception 信号的处理函数。
        got_request_exception.send(self, _async_wrapper=self.ensure_sync, exception=e)
        # "PROPAGATE_EXCEPTIONS": 这是配置项的名称，表示是否要传播异常。
        propagate = self.config["PROPAGATE_EXCEPTIONS"]

        # 如果其值为 None，则根据应用程序的测试模式和调试模式来确定是否传播异常。
        if propagate is None:
            propagate = self.testing or self.debug

        if propagate:
            # Re-raise if called with an active exception, otherwise
            # raise the passed in exception.
            if exc_info[1] is e:
                raise
            # 如果在处理当前异常时没有其他异常活动，那么就会重新引发当前异常 e
            raise e

        self.log_exception(exc_info)
        # InternalServerError: 这是 Flask 框架中定义的异常类，表示服务器内部错误。
        # ResponseReturnValue 是一个类型别名，表示视图函数可以返回的值的范围。
        server_error: InternalServerError | ft.ResponseReturnValue
        # 创建一个 InternalServerError 实例，并将原始的异常对象 e 作为参数传递给构造函数。
        server_error = InternalServerError(original_exception=e)
        # sansio/app.py line826
        # 查找适用于给定异常的错误处理器。
        # request.blueprints: 这是当前请求所属的蓝图列表。
        handler = self._find_error_handler(server_error, request.blueprints)

        if handler is not None:
            # self.ensure_sync(handler): 这是应用程序对象的方法，
            # 用于确保错误处理器是同步的（即不是异步的）。
            server_error = self.ensure_sync(handler)(server_error)

        return self.finalize_request(server_error, from_error_handler=True)

    # 记录异常的详细信息，以便在日志中进行调试和错误分析。
    def log_exception(
        self,
        exc_info: (tuple[type, BaseException, TracebackType] | tuple[None, None, None]),
    ) -> None:
        """Logs an exception.  This is called by :meth:`handle_exception`
        if debugging is disabled and right before the handler is called.
        The default implementation logs the exception as error on the
        :attr:`logger`.

        .. versionadded:: 0.8
        """

        # 格式化字符串，用于生成日志消息。它包含请求的路径和方法信息，
        # 以便在日志中标识发生异常的请求。
        self.logger.error(
            f"Exception on {request.path} [{request.method}]", exc_info=exc_info
        )


    # 通过执行这个方法，Flask 应用程序会根据请求的 URL 匹配相应的视图函数或错误处理器，
    # 并返回相应的响应。这是 Flask 中处理请求的核心方法之一。
    def dispatch_request(self) -> ft.ResponseReturnValue:
        """Does the request dispatching.  Matches the URL and returns the
        return value of the view or error handler.  This does not have to
        be a response object.  In order to convert the return value to a
        proper response object, call :func:`make_response`.

        .. versionchanged:: 0.7
           This no longer does the exception handling, this code was
           moved to the new :meth:`full_dispatch_request`.
        """
        # 获取当前请求对象，request_ctx 是请求上下文对象，request 是当前请求的实例。
        req = request_ctx.request
        # 是否存在路由异常
        if req.routing_exception is not None:
            self.raise_routing_exception(req)
        # rule: Rule = ...类型注解，用于指定变量 rule 的类型为 Rule。
        # req.url_rule: 获取当前请求对象的 URL 规则。
        rule: Rule = req.url_rule  # type: ignore[assignment]
        # if we provide automatic options for this URL and the
        # request came with the OPTIONS method, reply automatically
        if (
            getattr(rule, "provide_automatic_options", False)
            and req.method == "OPTIONS"
        ):
            return self.make_default_options_response()
        # otherwise dispatch to the handler for that endpoint
        view_args: dict[str, t.Any] = req.view_args  # type: ignore[assignment]
        return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)


    # 完成了请求的整个处理过程，包括预处理、派发、异常处理和最终处理。
    def full_dispatch_request(self) -> Response:
        """Dispatches the request and on top of that performs request
        pre and postprocessing as well as HTTP exception catching and
        error handling.

        .. versionadded:: 0.7
        """
        # 表示已经收到了第一个请求。
        self._got_first_request = True

        try:
            # request_started 信号，表示请求已经开始。
            # _async_wrapper 参数用于指定信号处理程序的异步包装器。
            request_started.send(self, _async_wrapper=self.ensure_sync)
            # 执行一些预处理操作，例如设置请求上下文或验证请求。
            rv = self.preprocess_request()
            if rv is None:
                rv = self.dispatch_request()
        except Exception as e:
            rv = self.handle_user_exception(e)
        return self.finalize_request(rv)


    # 在请求处理的最后阶段完成了对响应对象的最终处理，包括转换、后处理和信号发送。
    def finalize_request(
        self,
        rv: ft.ResponseReturnValue | HTTPException,
        from_error_handler: bool = False,
    ) -> Response:
        """Given the return value from a view function this finalizes
        the request by converting it into a response and invoking the
        postprocessing functions.  This is invoked for both normal
        request dispatching as well as error handlers.

        Because this means that it might be called as a result of a
        failure a special safe mode is available which can be enabled
        with the `from_error_handler` flag.  If enabled, failures in
        response processing will be logged and otherwise ignored.

        :internal:
        """
        response = self.make_response(rv)
        try:
            # 对响应对象进行进一步的处理，可能包括执行注册的响应后处理函数。
            response = self.process_response(response)
            request_finished.send(
                self, _async_wrapper=self.ensure_sync, response=response
            )
        except Exception:
            if not from_error_handler:
                raise
            self.logger.exception(
                "Request finalizing failed with an error while handling an error"
            )
        return response


    # 允许在子类中进行重写，以改变默认的 OPTIONS 请求响应的行为。
    def make_default_options_response(self) -> Response:
        """This method is called to create the default ``OPTIONS`` response.
        This can be changed through subclassing to change the default
        behavior of ``OPTIONS`` responses.

        .. versionadded:: 0.7
        """
        # 获取当前请求上下文中的 URL 适配器，用于处理当前请求的 URL。
        adapter = request_ctx.url_adapter
        # 获取当前请求的 URL 对应的资源允许的 HTTP 方法，例如 GET、POST、PUT 等。
        methods = adapter.allowed_methods()  # type: ignore[union-attr]
        # 创建一个空的响应对象，使用 self.response_class 来获取应用程序配置中定义
        # 的响应类（默认为 werkzeug.wrappers.Response）。
        rv = self.response_class()
        # 更新响应对象的允许方法集合，即设置 Allow 头部，告诉客户端服务器支持的 HTTP 方法。
        rv.allow.update(methods)
        return rv


    # 该方法用于确保函数是同步的，适用于在 WSGI 工作进程中运行的情况。
    # Flask 2.0 引入了 ensure_sync 方法，这个方法的目的是将异步函数转换为同步函数，
    # 以便在 WSGI 环境中正常运行。在 WSGI 中，同步函数是直接执行的，
    # 而异步函数需要使用特定的机制来确保其能够被正确执行和等待。
    def ensure_sync(self, func: t.Callable) -> t.Callable:
        """Ensure that the function is synchronous for WSGI workers.
        Plain ``def`` functions are returned as-is. ``async def``
        functions are wrapped to run and wait for the response.

        Override this method to change how the app runs async views.

        .. versionadded:: 2.0
        """
        if iscoroutinefunction(func):
            # 如果是协程函数，则调用 self.async_to_sync 方法将协程函数包装为同步函数，
            # 并返回包装后的函数。
            return self.async_to_sync(func)

        return func


    # 用于将异步协程函数（async def）转换为同步函数。
    def async_to_sync(
        self, func: t.Callable[..., t.Coroutine]
    ) -> t.Callable[..., t.Any]:
        """Return a sync function that will run the coroutine function.

        .. code-block:: python

            result = app.async_to_sync(func)(*args, **kwargs)

        Override this method to change how the app converts async code
        to be synchronously callable.

        .. versionadded:: 2.0
        """
        # 尝试从 asgiref 模块中导入 async_to_sync 函数，
        # 该函数用于将异步协程函数转换为同步函数。
        try:
            from asgiref.sync import async_to_sync as asgiref_async_to_sync
        except ImportError:
            raise RuntimeError(
                "Install Flask with the 'async' extra in order to use async views."
            ) from None

        # 返回一个新的同步函数，该函数会运行给定的异步协程函数。
        # 这样通过调用 app.async_to_sync(func)(*args, **kwargs)，
        # 可以以同步的方式运行原本是异步的协程函数。
        return asgiref_async_to_sync(func)


    # 用于生成与给定端点（endpoint）和值（values）对应的 URL。
    def url_for(
        self,
        /,
        endpoint: str,
        *,
        _anchor: str | None = None,
        _method: str | None = None,
        _scheme: str | None = None,
        _external: bool | None = None, # 控制生成的 URL 是相对路径还是绝对路径（包含域名和方案）。
        **values: t.Any,
    ) -> str:
        """Generate a URL to the given endpoint with the given values.

        This is called by :func:`flask.url_for`, and can be called
        directly as well.

        An *endpoint* is the name of a URL rule, usually added with
        :meth:`@app.route() <route>`, and usually the same name as the
        view function. A route defined in a :class:`~flask.Blueprint`
        will prepend the blueprint's name separated by a ``.`` to the
        endpoint.

        In some cases, such as email messages, you want URLs to include
        the scheme and domain, like ``https://example.com/hello``. When
        not in an active request, URLs will be external by default, but
        this requires setting :data:`SERVER_NAME` so Flask knows what
        domain to use. :data:`APPLICATION_ROOT` and
        :data:`PREFERRED_URL_SCHEME` should also be configured as
        needed. This config is only used when not in an active request.

        Functions can be decorated with :meth:`url_defaults` to modify
        keyword arguments before the URL is built.

        If building fails for some reason, such as an unknown endpoint
        or incorrect values, the app's :meth:`handle_url_build_error`
        method is called. If that returns a string, that is returned,
        otherwise a :exc:`~werkzeug.routing.BuildError` is raised.

        :param endpoint: The endpoint name associated with the URL to
            generate. If this starts with a ``.``, the current blueprint
            name (if any) will be used.
        :param _anchor: If given, append this as ``#anchor`` to the URL.
        :param _method: If given, generate the URL associated with this
            method for the endpoint.
        :param _scheme: If given, the URL will have this scheme if it
            is external.
        :param _external: If given, prefer the URL to be internal
            (False) or require it to be external (True). External URLs
            include the scheme and domain. When not in an active
            request, URLs are external by default.
        :param values: Values to use for the variable parts of the URL
            rule. Unknown keys are appended as query string arguments,
            like ``?a=b&c=d``.

        .. versionadded:: 2.2
            Moved from ``flask.url_for``, which calls this method.
        """
        # 获取当前线程的请求上下文，将其赋值给 req_ctx。如果当前线程没有请求上下文
        #（例如，在没有请求的情况下调用了 url_for 方法），req_ctx 的值将为 None。
        # req_ctx = _cv_request.get("some_key", default_value)
        req_ctx = _cv_request.get(None)

        # 首先检查是否存在请求上下文（req_ctx）。如果存在请求上下文，表示当前正在处理一个请求，
        # 那么就使用请求上下文的 url_adapter 属性和请求的蓝图（blueprint）信息来生成 URL。
        if req_ctx is not None:
            url_adapter = req_ctx.url_adapter
            blueprint_name = req_ctx.request.blueprint

            # If the endpoint starts with "." and the request matches a
            # blueprint, the endpoint is relative to the blueprint.
            if endpoint[:1] == ".":
                if blueprint_name is not None:
                    endpoint = f"{blueprint_name}{endpoint}"
                else:
                    endpoint = endpoint[1:]

            # When in a request, generate a URL without scheme and
            # domain by default, unless a scheme is given.
            if _external is None:
                _external = _scheme is not None
        # 如果没有请求上下文，则表示当前不在处理请求，可能是在应用初始化阶段或者在测试环境中。
        # 在这种情况下，代码会检查是否存在应用上下文（app_ctx）。如果存在应用上下文，
        # 就使用其 url_adapter 属性；否则，会创建一个新的 URL 适配器。
        else:
            app_ctx = _cv_app.get(None)

            # If called by helpers.url_for, an app context is active,
            # use its url_adapter. Otherwise, app.url_for was called
            # directly, build an adapter.
            if app_ctx is not None:
                url_adapter = app_ctx.url_adapter
            else:
                url_adapter = self.create_url_adapter(None)

            if url_adapter is None:
                raise RuntimeError(
                    "Unable to build URLs outside an active request"
                    " without 'SERVER_NAME' configured. Also configure"
                    " 'APPLICATION_ROOT' and 'PREFERRED_URL_SCHEME' as"
                    " needed."
                )

            # When outside a request, generate a URL with scheme and
            # domain by default.
            if _external is None:
                _external = True

        # It is an error to set _scheme when _external=False, in order
        # to avoid accidental insecure URLs.
        # 如果要指定 _scheme，通常应该将 _external 设置为 True，以确保生成的 URL 包含方案和域。
        # 如果设置了 _scheme 但将 _external 设置为 False，则会引发 ValueError，以避免生成不安全的 URL。
        if _scheme is not None and not _external:
            raise ValueError("When specifying '_scheme', '_external' must be True.")

        # 用于处理 URL 默认值的方法。在生成 URL 时，有时需要将一些默认值添加到 URL 中。
        # 这个方法的作用就是将这些默认值注入到 URL 的参数中。
        self.inject_url_defaults(endpoint, values)

        # 处理 URL 构建的核心逻辑。主要涉及使用 URL 适配器 (url_adapter) 构建 URL，
        # 处理构建错误，并在有锚点 (_anchor) 的情况下追加锚点。
        try:
            # 使用 URL 适配器的 build 方法构建 URL。
            rv = url_adapter.build(  # type: ignore[union-attr]
                endpoint,
                values,
                method=_method,
                url_scheme=_scheme,
                force_external=_external,
            )
        # 捕获可能的构建错误，即如果构建失败，抛出 BuildError 异常。
        except BuildError as error:
            # 在构建错误的情况下，将其他参数（如锚点、HTTP 方法、URL 方案、
            # 是否强制生成外部 URL）添加到参数字典 values 中，以便在后续的错误处理中使用。
            values.update(
                _anchor=_anchor, _method=_method, _scheme=_scheme, _external=_external
            )
            # 调用 handle_url_build_error 方法来处理构建错误。
            # 这个方法可以由应用程序进行重写以提供自定义的错误处理逻辑。
            return self.handle_url_build_error(error, endpoint, values)

        if _anchor is not None:
            _anchor = _url_quote(_anchor, safe="%!#$&'()*+,/:;=?@")
            rv = f"{rv}#{_anchor}"

        return rv


    # 将视图函数的返回值转换为 Response 对象。
    # 接收视图函数的返回值 rv，并将其转换为 Response 对象，最后返回这个 Response 对象。
    def make_response(self, rv: ft.ResponseReturnValue) -> Response:
        """Convert the return value from a view function to an instance of
        :attr:`response_class`.

        :param rv: the return value from the view function. The view function
            must return a response. Returning ``None``, or the view ending
            without returning, is not allowed. The following types are allowed
            for ``view_rv``:

            ``str``
                A response object is created with the string encoded to UTF-8
                as the body.

            ``bytes``
                A response object is created with the bytes as the body.

            ``dict``
                A dictionary that will be jsonify'd before being returned.

            ``list``
                A list that will be jsonify'd before being returned.

            ``generator`` or ``iterator``
                A generator that returns ``str`` or ``bytes`` to be
                streamed as the response.

            ``tuple``
                Either ``(body, status, headers)``, ``(body, status)``, or
                ``(body, headers)``, where ``body`` is any of the other types
                allowed here, ``status`` is a string or an integer, and
                ``headers`` is a dictionary or a list of ``(key, value)``
                tuples. If ``body`` is a :attr:`response_class` instance,
                ``status`` overwrites the exiting value and ``headers`` are
                extended.

            :attr:`response_class`
                The object is returned unchanged.

            other :class:`~werkzeug.wrappers.Response` class
                The object is coerced to :attr:`response_class`.

            :func:`callable`
                The function is called as a WSGI application. The result is
                used to create a response object.

        .. versionchanged:: 2.2
            A generator will be converted to a streaming response.
            A list will be converted to a JSON response.

        .. versionchanged:: 1.1
            A dict will be converted to a JSON response.

        .. versionchanged:: 0.9
           Previously a tuple was interpreted as the arguments for the
           response object.
        """

        # 初始化了两个变量 status 和 headers，将它们都设为 None。
        status = headers = None

        # unpack tuple returns
        # 用于处理视图函数的返回值 rv，如果 rv 是一个元组，它会进行解包操作。
        if isinstance(rv, tuple):
            len_rv = len(rv)

            # a 3-tuple is unpacked directly
            if len_rv == 3:
                rv, status, headers = rv  # type: ignore[misc]
            # decide if a 2-tuple has status or headers
            elif len_rv == 2:
                # 检查元组 rv 的第二个元素是否属于 (Headers, dict, tuple, list) 中的一种。
                if isinstance(rv[1], (Headers, dict, tuple, list)):
                    # 等效于rv = rv[0] headers = rv[1]
                    rv, headers = rv
                else:
                    rv, status = rv  # type: ignore[assignment,misc]
            # other sized tuples are not allowed
            else:
                raise TypeError(
                    "The view function did not return a valid response tuple."
                    " The tuple must have the form (body, status, headers),"
                    " (body, status), or (body, headers)."
                )

        # the body must not be None
        if rv is None:
            raise TypeError(
                f"The view function for {request.endpoint!r} did not"
                " return a valid response. The function either returned"
                " None or ended without a return statement."
            )

        # make sure the body is an instance of the response class
        # 确保 rv（即视图函数的返回值）是 self.response_class 类型的实例。
        # 在 Flask 中，self.response_class 默认是 werkzeug.wrappers.Response 类。
        # 这样可以确保返回的对象是符合预期的响应对象类型。
        if not isinstance(rv, self.response_class):
            if isinstance(rv, (str, bytes, bytearray)) or isinstance(rv, _abc_Iterator):
                # let the response class set the status and headers instead of
                # waiting to do it manually, so that the class can handle any
                # special logic
                rv = self.response_class(
                    rv,
                    status=status,
                    headers=headers,  # type: ignore[arg-type]
                )
                status = headers = None
            elif isinstance(rv, (dict, list)):
                rv = self.json.response(rv)
            elif isinstance(rv, BaseResponse) or callable(rv):
                # evaluate a WSGI callable, or coerce a different response
                # class to the correct type
                try:
                    rv = self.response_class.force_type(
                        rv,  # type: ignore[arg-type]
                        request.environ,
                    )
                except TypeError as e:
                    raise TypeError(
                        f"{e}\nThe view function did not return a valid"
                        " response. The return type must be a string,"
                        " dict, list, tuple with headers or status,"
                        " Response instance, or WSGI callable, but it"
                        f" was a {type(rv).__name__}."
                    ).with_traceback(sys.exc_info()[2]) from None
            else:
                raise TypeError(
                    "The view function did not return a valid"
                    " response. The return type must be a string,"
                    " dict, list, tuple with headers or status,"
                    " Response instance, or WSGI callable, but it was a"
                    f" {type(rv).__name__}."
                )

        # t.cast 不会执行实际的运行时类型检查或转换。它仅仅是为了在类型检查时提供额外的信息。
        # 在运行时，Python 仍然会以正常的方式处理 rv。
        rv = t.cast(Response, rv)
        # prefer the status if it was provided
        # 设置响应对象 (rv) 的状态码 (status)，确保响应对象的状态码正确设置。。
        # 如果 status 不是 None，则表示视图函数返回的响应中包含了自定义的状态码。
        if status is not None:
            if isinstance(status, (str, bytes, bytearray)):
                rv.status = status
            else:
                rv.status_code = status

        # extend existing headers with provided headers
        # 将视图函数返回的响应中包含的自定义头部信息 (headers) 添加到响应对象 (rv) 的头部。
        if headers:
            rv.headers.update(headers)  # type: ignore[arg-type]

        return rv


    # 用于处理请求的一部分，它在请求被分派到视图函数之前调用。
    def preprocess_request(self) -> ft.ResponseReturnValue | None:
        """Called before the request is dispatched. Calls
        :attr:`url_value_preprocessors` registered with the app and the
        current blueprint (if any). Then calls :attr:`before_request_funcs`
        registered with the app and the blueprint.

        If any :meth:`before_request` handler returns a non-None value, the
        value is handled as if it was the return value from the view, and
        further request handling is stopped.
        """
        # 将当前请求中涉及的蓝图的名称以相反的顺序添加到元组中。
        # request.blueprints 包含了当前请求所涉及的所有蓝图的名称。
        # None表示应用程序本身。
        names = (None, *reversed(request.blueprints))

        for name in names:
            # 检查当前名称是否有关联的 URL 参数预处理器。
            if name in self.url_value_preprocessors:
                # 如果存在与当前名称关联的预处理器函数，就遍历这些函数。
                for url_func in self.url_value_preprocessors[name]:
                    # 调用预处理器函数，将当前请求的终点（request.endpoint）和
                    # 视图参数（request.view_args）作为参数传递给这些函数。
                    url_func(request.endpoint, request.view_args)

        for name in names:
            # self.before_request_funcs 是 Flask 应用程序对象中存储
            # before_request 钩子函数的字典。
            if name in self.before_request_funcs:
                # before_func 是一个特定蓝图或应用程序关联的 before_request 钩子函数。
                for before_func in self.before_request_funcs[name]:
                    # 用于确保钩子函数是同步执行的，即使它是异步函数。
                    rv = self.ensure_sync(before_func)()

                    if rv is not None:
                        return rv

        return None


    # 用于在将响应发送到 WSGI 服务器之前对响应对象进行修改。
    def process_response(self, response: Response) -> Response:
        """Can be overridden in order to modify the response object
        before it's sent to the WSGI server.  By default this will
        call all the :meth:`after_request` decorated functions.

        .. versionchanged:: 0.5
           As of Flask 0.5 the functions registered for after request
           execution are called in reverse order of registration.

        :param response: a :attr:`response_class` object.
        :return: a new response object or the same, has to be an
                 instance of :attr:`response_class`.
        """
        # 获取当前请求上下文对象。
        # _get_current_object() 是该代理对象的方法，用于获取实际的请求上下文对象。
        ctx = request_ctx._get_current_object()  # type: ignore[attr-defined]

        # 在请求处理完成后，依次执行注册的after_request函数，
        # 并将响应对象作为参数传递给这些函数。
        for func in ctx._after_request_functions:
            # 使用同步版本的 func 处理 response。表示 ensure_sync(func) 返回的
            # 是另一个可调用对象，然后使用第二组括号 (response) 对其进行调用。
            response = self.ensure_sync(func)(response)

        # 用于处理请求后的钩子函数（after request hooks）的部分。
        # chain 函数用于将多个可迭代对象连接在一起，这里用于遍历蓝图和 None。
        for name in chain(request.blueprints, (None,)):
            # 检查当前循环中的 name 是否在应用的 after_request_funcs 中注册了钩子函数。
            if name in self.after_request_funcs:
                # 如果有注册的钩子函数，将它们按照注册的相反顺序进行遍历。
                # reversed 函数用于反转可迭代对象。
                for func in reversed(self.after_request_funcs[name]):
                    response = self.ensure_sync(func)(response)

        # 用于处理会话（session）的部分。在请求结束时检查会话是否为 null 会话，
        # 如果不是，则保存会话状态。这通常发生在用户进行身份验证或会话数据发生变化的情况下。
        # 通过应用的会话接口检查当前请求的会话对象是否为 null 会话。
        # Null 会话通常表示用户没有进行身份验证或没有启用会话功能。
        if not self.session_interface.is_null_session(ctx.session):
            self.session_interface.save_session(self, ctx.session, response)

        return response


    # 用于在请求处理结束后执行一些清理操作。
    def do_teardown_request(
        self,
        # exc：未处理的异常（可选），默认为 _sentinel。
        exc: BaseException | None = _sentinel,  # type: ignore[assignment]
    ) -> None:
        """Called after the request is dispatched and the response is
        returned, right before the request context is popped.

        This calls all functions decorated with
        :meth:`teardown_request`, and :meth:`Blueprint.teardown_request`
        if a blueprint handled the request. Finally, the
        :data:`request_tearing_down` signal is sent.

        This is called by
        :meth:`RequestContext.pop() <flask.ctx.RequestContext.pop>`,
        which may be delayed during testing to maintain access to
        resources.

        :param exc: An unhandled exception raised while dispatching the
            request. Detected from the current exception information if
            not passed. Passed to each teardown function.

        .. versionchanged:: 0.9
            Added the ``exc`` argument.
        """
        # 确保在调用 teardown_request 函数时，exc 参数始终包含有意义的异常信息。
        # 如果在调用时传递了异常，就使用传递的异常；否则，尝试从 sys.exc_info() 
        # 中获取当前异常。这样做的原因是在没有传递异常的情况下，
        # sys.exc_info() 提供了当前线程的异常信息。
        if exc is _sentinel:
            exc = sys.exc_info()[1]

        # 遍历所有的蓝图（包括主应用），以及一个额外的 None，
        # 这样可以确保注册在主应用上的 teardown 函数也会被执行。
        for name in chain(request.blueprints, (None,)):
            # 检查当前蓝图（或主应用）是否有注册 teardown 函数。
            if name in self.teardown_request_funcs:
                # 遍历已注册的 teardown 函数列表，注意这里使用 reversed 函数，
                # 表示按照注册的相反顺序执行 teardown 函数。
                for func in reversed(self.teardown_request_funcs[name]):
                    # 调用 ensure_sync 方法确保 teardown 函数是同步的，
                    # 然后将 exc 参数传递给这个 teardown 函数。
                    self.ensure_sync(func)(exc)

        # request_tearing_down 信号表示请求即将被拆除（tearing down）。
        request_tearing_down.send(self, _async_wrapper=self.ensure_sync, exc=exc)


    # 在应用上下文即将被弹出（popped）时调用，目的是在应用上下文即将被弹出时进行清理工作。
    def do_teardown_appcontext(
        self,
        exc: BaseException | None = _sentinel,  # type: ignore[assignment]
    ) -> None:
        """Called right before the application context is popped.

        When handling a request, the application context is popped
        after the request context. See :meth:`do_teardown_request`.

        This calls all functions decorated with
        :meth:`teardown_appcontext`. Then the
        :data:`appcontext_tearing_down` signal is sent.

        This is called by
        :meth:`AppContext.pop() <flask.ctx.AppContext.pop>`.

        .. versionadded:: 0.9
        """
        if exc is _sentinel:
            exc = sys.exc_info()[1]


        # 遍历应用上下文的清理函数（teardown_appcontext），使用 self.ensure_sync 
        # 包装并调用每个函数。这确保了清理函数的同步执行。
        for func in reversed(self.teardown_appcontext_funcs):
            self.ensure_sync(func)(exc)

        # 通知应用上下文即将被拆除。与之前提到的 request_tearing_down 类似，
        # 这个信号可以用于执行与应用上下文结束相关的操作，如清理数据库连接、关闭文件等。
        appcontext_tearing_down.send(self, _async_wrapper=self.ensure_sync, exc=exc)


    # 用于创建一个应用上下文 (AppContext)。
    # 应用上下文是 Flask 应用程序在运行时的上下文环境，可以使用 with 语句将其推入堆栈。
    # 这样做后，current_app 将指向这个应用程序。
    def app_context(self) -> AppContext:
        """Create an :class:`~flask.ctx.AppContext`. Use as a ``with``
        block to push the context, which will make :data:`current_app`
        point at this application.

        An application context is automatically pushed by
        :meth:`RequestContext.push() <flask.ctx.RequestContext.push>`
        when handling a request, and when running a CLI command. Use
        this to manually create a context outside of these situations.

        ::

            with app.app_context():
                init_db()

        See :doc:`/appcontext`.

        .. versionadded:: 0.9
        """
        return AppContext(self)


    # 用于创建一个请求上下文 (RequestContext)，表示一个 WSGI 环境。
    def request_context(self, environ: dict) -> RequestContext:
        """Create a :class:`~flask.ctx.RequestContext` representing a
        WSGI environment. Use a ``with`` block to push the context,
        which will make :data:`request` point at this request.

        See :doc:`/reqcontext`.

        Typically you should not call this from your own code. A request
        context is automatically pushed by the :meth:`wsgi_app` when
        handling a request. Use :meth:`test_request_context` to create
        an environment and context instead of this method.

        :param environ: a WSGI environment
        """
        return RequestContext(self, environ)


    # 用于在测试期间创建一个模拟的请求上下文 (RequestContext)。
    # 它允许你运行使用请求数据的函数，而无需触发完整的请求分发。
    def test_request_context(self, *args: t.Any, **kwargs: t.Any) -> RequestContext:
        """Create a :class:`~flask.ctx.RequestContext` for a WSGI
        environment created from the given values. This is mostly useful
        during testing, where you may want to run a function that uses
        request data without dispatching a full request.

        See :doc:`/reqcontext`.

        Use a ``with`` block to push the context, which will make
        :data:`request` point at the request for the created
        environment. ::

            with app.test_request_context(...):
                generate_report()

        When using the shell, it may be easier to push and pop the
        context manually to avoid indentation. ::

            ctx = app.test_request_context(...)
            ctx.push()
            ...
            ctx.pop()

        Takes the same arguments as Werkzeug's
        :class:`~werkzeug.test.EnvironBuilder`, with some defaults from
        the application. See the linked Werkzeug docs for most of the
        available arguments. Flask-specific behavior is listed here.

        :param path: URL path being requested.
        :param base_url: Base URL where the app is being served, which
            ``path`` is relative to. If not given, built from
            :data:`PREFERRED_URL_SCHEME`, ``subdomain``,
            :data:`SERVER_NAME`, and :data:`APPLICATION_ROOT`.
        :param subdomain: Subdomain name to append to
            :data:`SERVER_NAME`.
        :param url_scheme: Scheme to use instead of
            :data:`PREFERRED_URL_SCHEME`.
        :param data: The request body, either as a string or a dict of
            form keys and values.
        :param json: If given, this is serialized as JSON and passed as
            ``data``. Also defaults ``content_type`` to
            ``application/json``.
        :param args: other positional arguments passed to
            :class:`~werkzeug.test.EnvironBuilder`.
        :param kwargs: other keyword arguments passed to
            :class:`~werkzeug.test.EnvironBuilder`.
        """
        from .testing import EnvironBuilder

        builder = EnvironBuilder(self, *args, **kwargs)

        try:
            return self.request_context(builder.get_environ())
        finally:
            builder.close()

    # Flask 中的 wsgi_app 方法，它是真正的 WSGI 应用程序。该方法处理了整个请求-响应过程。
    def wsgi_app(self, environ: dict, start_response: t.Callable) -> t.Any:
        """The actual WSGI application. This is not implemented in
        :meth:`__call__` so that middlewares can be applied without
        losing a reference to the app object. Instead of doing this::

            app = MyMiddleware(app)

        It's a better idea to do this instead::

            app.wsgi_app = MyMiddleware(app.wsgi_app)

        Then you still have the original application object around and
        can continue to call methods on it.

        .. versionchanged:: 0.7
            Teardown events for the request and app contexts are called
            even if an unhandled error occurs. Other events may not be
            called depending on when an error occurs during dispatch.
            See :ref:`callbacks-and-errors`.

        :param environ: A WSGI environment.
        :param start_response: A callable accepting a status code,
            a list of headers, and an optional exception context to
            start the response.
        """
        # 创建请求上下文 (RequestContext) 对象。
        # 该对象与给定的 WSGI 环境（environ）相关联。
        ctx = self.request_context(environ)
        # error 这个变量的类型可以是 BaseException 或 None，并且初始值为 None。
        error: BaseException | None = None
        try:
            # 尝试推送请求上下文。
            try:
                ctx.push()
                # 调用 full_dispatch_request 处理请求并获取响应。
                response = self.full_dispatch_request()
            # 如果在处理请求时发生异常，捕获该异常，并调用 handle_exception 处理异常。
            except Exception as e:
                error = e
                response = self.handle_exception(e)
            except:  # noqa: B001
                error = sys.exc_info()[1]
                raise
            return response(environ, start_response)
        # 在 finally 块中，执行一些清理工作。
        finally:
            # 如果设置了 "werkzeug.debug.preserve_context"，则将上下文保存下来。
            if "werkzeug.debug.preserve_context" in environ:
                environ["werkzeug.debug.preserve_context"](_cv_app.get())
                environ["werkzeug.debug.preserve_context"](_cv_request.get())

            # 如果发生了错误并且该错误应该被忽略，则将错误设置为 None。
            if error is not None and self.should_ignore_error(error):
                error = None

            # 弹出请求上下文。
            ctx.pop(error)

    # 这个 __call__ 方法定义了 Flask 应用对象是如何被 WSGI 服务器调用的，使其成为一个
    # WSGI 应用程序。是 Flask 应用对象作为 WSGI 应用程序时的入口点，负责将请求传递给
    # 实际的请求处理逻辑。
    # 在这个方法中，实际的请求处理逻辑被委托给了 wsgi_app 方法。
    # 这种设计的好处在于，它允许应用对象的 wsgi_app 方法被中间件包装，
    # 从而实现对请求和响应的自定义处理。
    def __call__(self, environ: dict, start_response: t.Callable) -> t.Any:
        """The WSGI server calls the Flask application object as the
        WSGI application. This calls :meth:`wsgi_app`, which can be
        wrapped to apply middleware.
        """
        return self.wsgi_app(environ, start_response)








