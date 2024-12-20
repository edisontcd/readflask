from __future__ import annotations

import logging
import os
import sys
import typing as t
from datetime import timedelta
from itertools import chain

from werkzeug.exceptions import Aborter
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.routing import BuildError
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.sansio.response import Response
from werkzeug.utils import cached_property
from werkzeug.utils import redirect as _wz_redirect

from .. import typing as ft
from ..config import Config
from ..config import ConfigAttribute
from ..ctx import _AppCtxGlobals
from ..helpers import _split_blueprint_path
from ..helpers import get_debug_flag
from ..json.provider import DefaultJSONProvider
from ..json.provider import JSONProvider
from ..logging import create_logger
from ..templating import DispatchingJinjaLoader
from ..templating import Environment
from .scaffold import _endpoint_from_view_func
from .scaffold import find_package
from .scaffold import Scaffold
from .scaffold import setupmethod

if t.TYPE_CHECKING:  # pragma: no cover
    from werkzeug.wrappers import Response as BaseResponse

    from ..testing import FlaskClient
    from ..testing import FlaskCliRunner
    from .blueprints import Blueprint

T_shell_context_processor = t.TypeVar(
    "T_shell_context_processor", bound=ft.ShellContextProcessorCallable
)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
T_template_filter = t.TypeVar("T_template_filter", bound=ft.TemplateFilterCallable)
T_template_global = t.TypeVar("T_template_global", bound=ft.TemplateGlobalCallable)
T_template_test = t.TypeVar("T_template_test", bound=ft.TemplateTestCallable)


# 它用于将传入的值转换为 timedelta 类型，以便统一处理时间间隔。
def _make_timedelta(value: timedelta | int | None) -> timedelta | None:
    if value is None or isinstance(value, timedelta):
        return value

    return timedelta(seconds=value)


# Flask 框架中的核心类，继承自 Scaffold。它实现了 WSGI 应用程序，并充当了应用的中心对象，
# 负责管理视图函数、URL 路由、模板引擎、错误处理、会话管理等。
class App(Scaffold):
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

    #: The class of the object assigned to :attr:`aborter`, created by
    #: :meth:`create_aborter`. That object is called by
    #: :func:`flask.abort` to raise HTTP errors, and can be
    #: called directly as well.
    #:
    #: Defaults to :class:`werkzeug.exceptions.Aborter`.
    #:
    #: .. versionadded:: 2.2
    # 处理 HTTP 错误的类，默认为 Aborter，由 flask.abort 使用。
    aborter_class = Aborter

    #: The class that is used for the Jinja environment.
    #:
    #: .. versionadded:: 0.11
    # Flask 使用的 Jinja 环境类，默认为 Environment。
    jinja_environment = Environment

    #: The class that is used for the :data:`~flask.g` instance.
    #:
    #: Example use cases for a custom class:
    #:
    #: 1. Store arbitrary attributes on flask.g.
    #: 2. Add a property for lazy per-request database connectors.
    #: 3. Return None instead of AttributeError on unexpected attributes.
    #: 4. Raise exception if an unexpected attr is set, a "controlled" flask.g.
    #:
    #: In Flask 0.9 this property was called `request_globals_class` but it
    #: was changed in 0.10 to :attr:`app_ctx_globals_class` because the
    #: flask.g object is now application context scoped.
    #:
    #: .. versionadded:: 0.10
    # 用于 flask.g 的类，默认是 _AppCtxGlobals。
    # 可以扩展 flask.g 来存储额外的属性，或者提供自定义的行为。
    app_ctx_globals_class = _AppCtxGlobals

    #: The class that is used for the ``config`` attribute of this app.
    #: Defaults to :class:`~flask.Config`.
    #:
    #: Example use cases for a custom class:
    #:
    #: 1. Default values for certain config options.
    #: 2. Access to config values through attributes in addition to keys.
    #:
    #: .. versionadded:: 0.11
    # 应用的配置类，默认是 Config，负责读取和管理应用的配置。
    config_class = Config

    #: The testing flag.  Set this to ``True`` to enable the test mode of
    #: Flask extensions (and in the future probably also Flask itself).
    #: For example this might activate test helpers that have an
    #: additional runtime cost which should not be enabled by default.
    #:
    #: If this is enabled and PROPAGATE_EXCEPTIONS is not changed from the
    #: default it's implicitly enabled.
    #:
    #: This attribute can also be configured from the config with the
    #: ``TESTING`` configuration key.  Defaults to ``False``.
    # 测试模式的开关。如果为 True，启用测试模式，允许某些扩展和 Flask 本身的额外调试功能。
    testing = ConfigAttribute[bool]("TESTING")

    #: If a secret key is set, cryptographic components can use this to
    #: sign cookies and other things. Set this to a complex random value
    #: when you want to use the secure cookie for instance.
    #:
    #: This attribute can also be configured from the config with the
    #: :data:`SECRET_KEY` configuration key. Defaults to ``None``.
    # 用于签名和加密 cookies 等的密钥。必须设置为复杂的随机值。
    secret_key = ConfigAttribute[t.Union[str, bytes, None]]("SECRET_KEY")

    #: A :class:`~datetime.timedelta` which is used to set the expiration
    #: date of a permanent session.  The default is 31 days which makes a
    #: permanent session survive for roughly one month.
    #:
    #: This attribute can also be configured from the config with the
    #: ``PERMANENT_SESSION_LIFETIME`` configuration key.  Defaults to
    #: ``timedelta(days=31)``
    # 永久会话的过期时间，默认是 timedelta(days=31)，即大约 31 天。
    permanent_session_lifetime = ConfigAttribute[timedelta](
        "PERMANENT_SESSION_LIFETIME",
        get_converter=_make_timedelta,  # type: ignore[arg-type]
    )

    # 用于 JSON 处理的类，默认是 DefaultJSONProvider。
    json_provider_class: type[JSONProvider] = DefaultJSONProvider
    """A subclass of :class:`~flask.json.provider.JSONProvider`. An
    instance is created and assigned to :attr:`app.json` when creating
    the app.

    The default, :class:`~flask.json.provider.DefaultJSONProvider`, uses
    Python's built-in :mod:`json` library. A different provider can use
    a different JSON library.

    .. versionadded:: 2.2
    """

    #: Options that are passed to the Jinja environment in
    #: :meth:`create_jinja_environment`. Changing these options after
    #: the environment is created (accessing :attr:`jinja_env`) will
    #: have no effect.
    #:
    #: .. versionchanged:: 1.1.0
    #:     This is a ``dict`` instead of an ``ImmutableDict`` to allow
    #:     easier configuration.
    #:
    # 用于配置 Jinja 环境的选项。
    jinja_options: dict[str, t.Any] = {}

    #: The rule object to use for URL rules created.  This is used by
    #: :meth:`add_url_rule`.  Defaults to :class:`werkzeug.routing.Rule`.
    #:
    #: .. versionadded:: 0.7
    # 用于创建 URL 规则的类，默认是 Rule。
    url_rule_class = Rule

    #: The map object to use for storing the URL rules and routing
    #: configuration parameters. Defaults to :class:`werkzeug.routing.Map`.
    #:
    #: .. versionadded:: 1.1.0
    # URL 映射表的类，默认是 Map。
    url_map_class = Map

    #: The :meth:`test_client` method creates an instance of this test
    #: client class. Defaults to :class:`~flask.testing.FlaskClient`.
    #:
    #: .. versionadded:: 0.7
    # 用于测试客户端的类，默认是 FlaskClient。
    test_client_class: type[FlaskClient] | None = None

    #: The :class:`~click.testing.CliRunner` subclass, by default
    #: :class:`~flask.testing.FlaskCliRunner` that is used by
    #: :meth:`test_cli_runner`. Its ``__init__`` method should take a
    #: Flask app object as the first argument.
    #:
    #: .. versionadded:: 1.0
    # 用于测试 CLI 命令的类，默认是 FlaskCliRunner。
    test_cli_runner_class: type[FlaskCliRunner] | None = None

    # Flask 应用的默认配置字典。
    default_config: dict[str, t.Any]
    # 返回响应的类，通常是 Response。
    response_class: type[Response]

    # Flask 类的初始化方法，用于创建一个新的 Flask 应用实例。
    def __init__(
        self,
        # 应用包的名称
        import_name: str,
        # 用于设置静态文件的 URL 路径。
        static_url_path: str | None = None,
        # 指定静态文件的目录位置，默认值为 static。
        static_folder: str | os.PathLike[str] | None = "static",
        # 指定静态文件所在的主机名。
        static_host: str | None = None,
        # 设置是否在路由规则中启用主机名匹配。
        host_matching: bool = False,
        # 设置是否启用子域名匹配。
        subdomain_matching: bool = False,
        # 指定模板文件所在的目录。
        template_folder: str | os.PathLike[str] | None = "templates",
        # 用于设置实例路径，默认是相对于应用包的 'instance' 目录。
        instance_path: str | None = None,
        # 如果设置为 True，则配置文件路径将相对于实例路径，而不是应用根路径。
        instance_relative_config: bool = False,
        # 用于手动设置根路径。
        root_path: str | None = None,
    ) -> None:
        # 通过 super() 调用了父类 Scaffold 的 __init__ 方法，并传递了一些参数。
        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            static_url_path=static_url_path,
            template_folder=template_folder,
            root_path=root_path,
        )

        # 如果 instance_path 未提供（即为 None），Flask 会自动调用
        # self.auto_find_instance_path() 方法来确定实例路径。
        if instance_path is None:
            instance_path = self.auto_find_instance_path()
        # 如果 instance_path 是相对路径，就会引发错误。
        elif not os.path.isabs(instance_path):
            raise ValueError(
                "If an instance path is provided it must be absolute."
                " A relative path was given instead."
            )

        #: Holds the path to the instance folder.
        #:
        #: .. versionadded:: 0.8
        # 保存实例文件夹的路径。
        self.instance_path = instance_path

        #: The configuration dictionary as :class:`Config`.  This behaves
        #: exactly like a regular dictionary but supports additional methods
        #: to load a config from files.
        # 用来存储应用的各种配置（如 DEBUG、SECRET_KEY）。
        self.config = self.make_config(instance_relative_config)

        #: An instance of :attr:`aborter_class` created by
        #: :meth:`make_aborter`. This is called by :func:`flask.abort`
        #: to raise HTTP errors, and can be called directly as well.
        #:
        #: .. versionadded:: 2.2
        #:     Moved from ``flask.abort``, which calls this object.
        # abort 方法使用的 Aborter 实例，用于引发 HTTP 错误。
        self.aborter = self.make_aborter()

        # 处理 JSON 请求和响应的提供者。
        self.json: JSONProvider = self.json_provider_class(self)
        """Provides access to JSON methods. Functions in ``flask.json``
        will call methods on this provider when the application context
        is active. Used for handling JSON requests and responses.

        An instance of :attr:`json_provider_class`. Can be customized by
        changing that attribute on a subclass, or by assigning to this
        attribute afterwards.

        The default, :class:`~flask.json.provider.DefaultJSONProvider`,
        uses Python's built-in :mod:`json` library. A different provider
        can use a different JSON library.

        .. versionadded:: 2.2
        """

        #: A list of functions that are called by
        #: :meth:`handle_url_build_error` when :meth:`.url_for` raises a
        #: :exc:`~werkzeug.routing.BuildError`. Each function is called
        #: with ``error``, ``endpoint`` and ``values``. If a function
        #: returns ``None`` or raises a ``BuildError``, it is skipped.
        #: Otherwise, its return value is returned by ``url_for``.
        #:
        #: .. versionadded:: 0.9
        # 存储处理 URL 生成错误的函数列表。
        self.url_build_error_handlers: list[
            t.Callable[[Exception, str, dict[str, t.Any]], str]
        ] = []

        #: A list of functions that are called when the application context
        #: is destroyed.  Since the application context is also torn down
        #: if the request ends this is the place to store code that disconnects
        #: from databases.
        #:
        #: .. versionadded:: 0.9
        # 存储在应用上下文销毁时调用的函数。
        self.teardown_appcontext_funcs: list[ft.TeardownCallable] = []

        #: A list of shell context processor functions that should be run
        #: when a shell context is created.
        #:
        #: .. versionadded:: 0.11
        # 存储在创建 Shell 上下文时要运行的处理器函数。
        self.shell_context_processors: list[ft.ShellContextProcessorCallable] = []

        #: Maps registered blueprint names to blueprint objects. The
        #: dict retains the order the blueprints were registered in.
        #: Blueprints can be registered multiple times, this dict does
        #: not track how often they were attached.
        #:
        #: .. versionadded:: 0.7
        # 存储应用中注册的蓝图。
        self.blueprints: dict[str, Blueprint] = {}

        #: a place where extensions can store application specific state.  For
        #: example this is where an extension could store database engines and
        #: similar things.
        #:
        #: The key must match the name of the extension module. For example in
        #: case of a "Flask-Foo" extension in `flask_foo`, the key would be
        #: ``'foo'``.
        #:
        #: .. versionadded:: 0.7
        # 存储扩展的状态。
        self.extensions: dict[str, t.Any] = {}

        #: The :class:`~werkzeug.routing.Map` for this instance.  You can use
        #: this to change the routing converters after the class was created
        #: but before any routes are connected.  Example::
        #:
        #:    from werkzeug.routing import BaseConverter
        #:
        #:    class ListConverter(BaseConverter):
        #:        def to_python(self, value):
        #:            return value.split(',')
        #:        def to_url(self, values):
        #:            return ','.join(super(ListConverter, self).to_url(value)
        #:                            for value in values)
        #:
        #:    app = Flask(__name__)
        #:    app.url_map.converters['list'] = ListConverter
        # 存储应用的 URL 映射表。
        self.url_map = self.url_map_class(host_matching=host_matching)

        # 是否启用子域名匹配。
        self.subdomain_matching = subdomain_matching

        # tracks internally if the application already handled at least one
        # request.
        # 录应用是否已经处理过至少一个请求。
        self._got_first_request = False

    # 方法名前面加下划线通常表示这是一个私有方法。
    # 用于检查 Flask 应用程序是否已经处理过请求。
    def _check_setup_finished(self, f_name: str) -> None:
        if self._got_first_request:
            raise AssertionError(
                f"The setup method '{f_name}' can no longer be called"
                " on the application. It has already handled its first"
                " request, any changes will not be applied"
                " consistently.\n"
                "Make sure all imports, decorators, functions, etc."
                " needed to set up the application are done before"
                " running it."
            )

    # @property：将方法转换为属性，@cached_property：在 @property 基础上进一步优化，
    # 使方法的结果在首次计算后缓存起来，后续访问时直接返回缓存的结果，而不再重复计算。
    # 提供应用的名称，通常用于调试或显示应用信息。
    @cached_property
    def name(self) -> str:  # type: ignore
        """The name of the application.  This is usually the import name
        with the difference that it's guessed from the run file if the
        import name is main.  This name is used as a display name when
        Flask needs the name of the application.  It can be set and overridden
        to change the value.

        .. versionadded:: 0.8
        """
        # 当 Flask 应用直接作为主程序运行（即 __name__ == "__main__"）时，
        # import_name 将被设置为 "__main__"，这种情况下，name 应该返回运行文件的名称，
        # 而不是 "__main__"。
        if self.import_name == "__main__":
            # sys.modules["__main__"] 是当前运行脚本的模块对象，通过 getattr 获取该模块的
            # __file__ 属性，来获取文件路径。
            fn: str | None = getattr(sys.modules["__main__"], "__file__", None)
            if fn is None:
                return "__main__"
            # 从文件路径中提取文件名并去掉扩展名。
            return os.path.splitext(os.path.basename(fn))[0]
        return self.import_name

    # 缓存了一个配置好的 Logger 实例，便于应用记录日志信息。
    @cached_property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app, with
        the same name as :attr:`name`.

        In debug mode, the logger's :attr:`~logging.Logger.level` will
        be set to :data:`~logging.DEBUG`.

        If there are no handlers configured, a default handler will be
        added. See :doc:`/logging` for more information.

        .. versionchanged:: 1.1.0
            The logger takes the same name as :attr:`name` rather than
            hard-coding ``"flask.app"``.

        .. versionchanged:: 1.0.0
            Behavior was simplified. The logger is always named
            ``"flask.app"``. The level is only set during configuration,
            it doesn't check ``app.debug`` each time. Only one format is
            used, not different ones depending on ``app.debug``. No
            handlers are removed, and a handler is only added if no
            handlers are already configured.

        .. versionadded:: 0.3
        """
        return create_logger(self)

    # Flask 应用的 Jinja 环境，通过 @cached_property 缓存。
    # 在第一次访问时创建，以确保应用的 Jinja 配置在初始化时应用。
    @cached_property
    def jinja_env(self) -> Environment:
        """The Jinja environment used to load templates.

        The environment is created the first time this property is
        accessed. Changing :attr:`jinja_options` after that will have no
        effect.
        """
        return self.create_jinja_environment()

    # 一个接口方法，要求子类提供实现。
    # 抛出 NotImplementedError 强制子类实现该方法。
    def create_jinja_environment(self) -> Environment:
        raise NotImplementedError()

    # 根据应用的根路径和实例路径来初始化配置。
    def make_config(self, instance_relative: bool = False) -> Config:
        """Used to create the config attribute by the Flask constructor.
        The `instance_relative` parameter is passed in from the constructor
        of Flask (there named `instance_relative_config`) and indicates if
        the config should be relative to the instance path or the root path
        of the application.

        .. versionadded:: 0.8
        """
        # 默认设置根路径为应用的 root_path。
        root_path = self.root_path
        # 如果 instance_relative 为 True，使用实例路径作为根路径。
        # 参数控制配置路径是否相对于实例路径（instance_path）而不是应用的根路径（root_path）。
        if instance_relative:
            root_path = self.instance_path
        # 创建一个默认配置字典，继承默认配置（self.default_config）并添加 DEBUG 设置。
        defaults = dict(self.default_config)
        # 根据当前的调试标志来设置 DEBUG。
        defaults["DEBUG"] = get_debug_flag()
        return self.config_class(root_path, defaults)

    # 用于创建并返回一个 Aborter 类的实例。
    # Aborter 负责处理 HTTP 错误，并在需要时通过 flask.abort() 触发错误响应。
    # 默认情况下，Flask 使用 werkzeug.exceptions.Aborter 作为 Aborter 类，但它允许用户自定义错误处理类。
    def make_aborter(self) -> Aborter:
        """Create the object to assign to :attr:`aborter`. That object
        is called by :func:`flask.abort` to raise HTTP errors, and can
        be called directly as well.

        By default, this creates an instance of :attr:`aborter_class`,
        which defaults to :class:`werkzeug.exceptions.Aborter`.

        .. versionadded:: 2.2
        """
        # 创建并返回一个 Aborter 实例。
        return self.aborter_class()

    # 用于在没有提供实例路径的情况下自动计算实例路径，它通过检查包的前缀路径来决定实例路径的位置。
    # 实例路径是 Flask 应用用来存放配置文件、数据库文件或其他实例特定文件的文件夹。
    def auto_find_instance_path(self) -> str:
        """Tries to locate the instance path if it was not provided to the
        constructor of the application class.  It will basically calculate
        the path to a folder named ``instance`` next to your main file or
        the package.

        .. versionadded:: 0.8
        """
        # 解包赋值（unpacking assignment），prefix, package_path 是对返回值的解包操作，
        # 它告诉 Python 将返回的元组中的第一个值赋给 prefix 变量，将第二个值赋给 package_path 变量。
        # find_package(self.import_name) 是 Flask 中用来查找包的路径的函数。它返回两个值：
        # prefix: 包的前缀路径，通常是包含该包的目录路径。
        # package_path: 包的实际路径，可能是一个文件路径或者目录路径。
        prefix, package_path = find_package(self.import_name)
        if prefix is None:
            return os.path.join(package_path, "instance")
        return os.path.join(prefix, "var", f"{self.name}-instance")

    # 创建一个 Jinja2 环境的全局加载器（DispatchingJinjaLoader）。
    # 这个加载器用于处理 Jinja2 模板的加载，且能够区分应用本身和单独的蓝图（Blueprints）的模板加载需求。
    def create_global_jinja_loader(self) -> DispatchingJinjaLoader:
        """Creates the loader for the Jinja2 environment.  Can be used to
        override just the loader and keeping the rest unchanged.  It's
        discouraged to override this function.  Instead one should override
        the :meth:`jinja_loader` function instead.

        The global loader dispatches between the loaders of the application
        and the individual blueprints.

        .. versionadded:: 0.7
        """
        return DispatchingJinjaLoader(self)

    # 用于选择是否启用 Jinja2 模板的 自动转义 (autoescaping) 功能的方法。
    # 自动转义是防止跨站脚本攻击 (XSS) 的重要措施，它会自动转义 HTML、XML 等格式中的特殊字符，
    # 确保它们不会被错误地解释为 HTML 或 JavaScript 代码。
    def select_jinja_autoescape(self, filename: str) -> bool:
        """Returns ``True`` if autoescaping should be active for the given
        template name. If no template name is given, returns `True`.

        .. versionchanged:: 2.2
            Autoescaping is now enabled by default for ``.svg`` files.

        .. versionadded:: 0.5
        """
        if filename is None:
            return True
        # 如果是其中之一，则返回 True，启用自动转义；
        return filename.endswith((".html", ".htm", ".xml", ".xhtml", ".svg"))

    # debug 属性是 Flask 中用于判断是否启用调试模式的属性。
    @property
    def debug(self) -> bool:
        """Whether debug mode is enabled. When using ``flask run`` to start the
        development server, an interactive debugger will be shown for unhandled
        exceptions, and the server will be reloaded when code changes. This maps to the
        :data:`DEBUG` config key. It may not behave as expected if set late.

        **Do not enable debug mode when deploying in production.**

        Default: ``False``
        """
        return self.config["DEBUG"]  # type: ignore[no-any-return]

    # 定义了一个 setter 方法，让你能够在修改 debug 属性时自动更新相关配置。
    @debug.setter
    def debug(self, value: bool) -> None:
        self.config["DEBUG"] = value

        # 更新 jinja_env.auto_reload，以便根据调试模式的开启与否调整模板的自动重载行为。
        if self.config["TEMPLATES_AUTO_RELOAD"] is None:
            self.jinja_env.auto_reload = value

    # 用于将蓝图注册到应用中的方法，支持各种配置选项，如 URL 前缀、子域名、URL 默认值等。
    @setupmethod
    def register_blueprint(self, blueprint: Blueprint, **options: t.Any) -> None:
        """Register a :class:`~flask.Blueprint` on the application. Keyword
        arguments passed to this method will override the defaults set on the
        blueprint.

        Calls the blueprint's :meth:`~flask.Blueprint.register` method after
        recording the blueprint in the application's :attr:`blueprints`.

        :param blueprint: The blueprint to register.
        :param url_prefix: Blueprint routes will be prefixed with this.
        :param subdomain: Blueprint routes will match on this subdomain.
        :param url_defaults: Blueprint routes will use these default values for
            view arguments.
        :param options: Additional keyword arguments are passed to
            :class:`~flask.blueprints.BlueprintSetupState`. They can be
            accessed in :meth:`~flask.Blueprint.record` callbacks.

        .. versionchanged:: 2.0.1
            The ``name`` option can be used to change the (pre-dotted)
            name the blueprint is registered with. This allows the same
            blueprint to be registered multiple times with unique names
            for ``url_for``.

        .. versionadded:: 0.7
        """
        blueprint.register(self, options)

    # 返回应用中所有已注册蓝图的迭代器，顺序与蓝图注册顺序一致。
    def iter_blueprints(self) -> t.ValuesView[Blueprint]:
        """Iterates over all blueprints by the order they were registered.

        .. versionadded:: 0.11
        """
        return self.blueprints.values()

    # Flask 路由系统的核心方法，通过它可以将特定的 URL 规则和视图函数关联起来。
    @setupmethod
    def add_url_rule(
        self,
        rule: str, # 表示 URL 路由规则，例如 /home 或 /api/<id>。
        endpoint: str | None = None, # 指定此路由的终点名称，默认为视图函数的名称。
        # 关联到路由规则的视图函数。它是实际处理该路由请求的逻辑。
        view_func: ft.RouteCallable | None = None, 
        # 决定是否自动为该路由提供 OPTIONS 方法支持。
        provide_automatic_options: bool | None = None,
        # 其他传递给路由规则的附加选项，例如 methods 表示支持的 HTTP 方法。
        **options: t.Any,
    ) -> None:
        # 如果没有显式提供 endpoint，会使用视图函数的名称作为默认终点。
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)  # type: ignore
        options["endpoint"] = endpoint
        methods = options.pop("methods", None)

        # if the methods are not given and the view_func object knows its
        # methods we can use that instead.  If neither exists, we go with
        # a tuple of only ``GET`` as default.
        # 从 options 中提取 methods 参数，如果未指定：检查视图函数是否定义了 methods 属性；
        # 否则默认仅支持 GET 方法。
        if methods is None:
            methods = getattr(view_func, "methods", None) or ("GET",)
        # 如果 methods 是字符串而非列表，抛出错误；
        if isinstance(methods, str):
            raise TypeError(
                "Allowed methods must be a list of strings, for"
                ' example: @app.route(..., methods=["POST"])'
            )
        # 将 methods 转换为大写的集合（set），便于后续操作。
        methods = {item.upper() for item in methods}

        # 检查视图函数是否声明了 required_methods 属性，强制添加到 methods。
        # Methods that should always be added
        required_methods: set[str] = set(getattr(view_func, "required_methods", ()))

        # starting with Flask 0.8 the view_func object can disable and
        # force-enable the automatic options handling.
        # 如果未显式设置 provide_automatic_options，从视图函数的属性中获取该值。
        if provide_automatic_options is None:
            provide_automatic_options = getattr(
                view_func, "provide_automatic_options", None
            )

        # 如果未设置且 PROVIDE_AUTOMATIC_OPTIONS 配置为 True，自动启用 OPTIONS 方法支持。
        if provide_automatic_options is None:
            if "OPTIONS" not in methods and self.config["PROVIDE_AUTOMATIC_OPTIONS"]:
                provide_automatic_options = True
                required_methods.add("OPTIONS")
            else:
                provide_automatic_options = False

        # Add the required methods now.
        # 将 required_methods 添加到 methods 集合中。
        methods |= required_methods

        # 使用 self.url_rule_class（通常是 werkzeug.routing.Rule）创建路由规则对象；
        rule_obj = self.url_rule_class(rule, methods=methods, **options)
        # 设置 provide_automatic_options 以处理 OPTIONS 请求。
        rule_obj.provide_automatic_options = provide_automatic_options  # type: ignore[attr-defined]

        # 将创建的路由规则对象添加到应用的 url_map 中，url_map 是管理所有路由规则的核心数据结构。
        self.url_map.add(rule_obj)
        # 如果提供了视图函数，检查是否已存在与该 endpoint 绑定的其他视图函数；
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            # 如果冲突（即终点名称已被其他视图函数使用），抛出异常；
            if old_func is not None and old_func != view_func:
                raise AssertionError(
                    "View function mapping is overwriting an existing"
                    f" endpoint function: {endpoint}"
                )
            # 否则将视图函数绑定到 view_functions 字典中。
            self.view_functions[endpoint] = view_func

    # 用于将自定义的模板过滤器注册到 Flask 应用中。
    @setupmethod # 标识该方法是一个设置方法，通常在应用启动时调用。
    def template_filter(
        self, name: str | None = None
    ) -> t.Callable[[T_template_filter], T_template_filter]:
        """A decorator that is used to register custom template filter.
        You can specify a name for the filter, otherwise the function
        name will be used. Example::

          @app.template_filter()
          def reverse(s):
              return s[::-1]

        :param name: the optional name of the filter, otherwise the
                     function name will be used.
        """

        def decorator(f: T_template_filter) -> T_template_filter:
            # 将过滤器注册到 Flask 应用中。
            self.add_template_filter(f, name=name)
            return f

        return decorator

    # 用于直接向 Flask 应用的 Jinja2 环境中注册自定义模板过滤器。
    # 它的作用与 template_filter 类似，但不是以装饰器的形式，而是直接调用方法。
    @setupmethod
    def add_template_filter(
        self, f: ft.TemplateFilterCallable, name: str | None = None
    ) -> None:
        """Register a custom template filter.  Works exactly like the
        :meth:`template_filter` decorator.

        :param name: the optional name of the filter, otherwise the
                     function name will be used.
        """
        self.jinja_env.filters[name or f.__name__] = f

    # 用于注册自定义的模板测试（template test）。
    @setupmethod
    def template_test(
        self, name: str | None = None
    ) -> t.Callable[[T_template_test], T_template_test]:
        """A decorator that is used to register custom template test.
        You can specify a name for the test, otherwise the function
        name will be used. Example::

          @app.template_test()
          def is_prime(n):
              if n == 2:
                  return True
              for i in range(2, int(math.ceil(math.sqrt(n))) + 1):
                  if n % i == 0:
                      return False
              return True

        .. versionadded:: 0.10

        :param name: the optional name of the test, otherwise the
                     function name will be used.
        """

        def decorator(f: T_template_test) -> T_template_test:
            self.add_template_test(f, name=name)
            return f

        return decorator

    # 用于直接向 Flask 应用的 Jinja2 环境中注册自定义模板测试（template test）。
    @setupmethod
    def add_template_test(
        self, f: ft.TemplateTestCallable, name: str | None = None
    ) -> None:
        """Register a custom template test.  Works exactly like the
        :meth:`template_test` decorator.

        .. versionadded:: 0.10

        :param name: the optional name of the test, otherwise the
                     function name will be used.
        """
        self.jinja_env.tests[name or f.__name__] = f

    # 用于注册模板全局函数，方便在 Jinja2 模板中调用。
    @setupmethod
    def template_global(
        self, name: str | None = None
    ) -> t.Callable[[T_template_global], T_template_global]:
        """A decorator that is used to register a custom template global function.
        You can specify a name for the global function, otherwise the function
        name will be used. Example::

            @app.template_global()
            def double(n):
                return 2 * n

        .. versionadded:: 0.10

        :param name: the optional name of the global function, otherwise the
                     function name will be used.
        """

        def decorator(f: T_template_global) -> T_template_global:
            self.add_template_global(f, name=name)
            return f

        return decorator

    # 将函数注册为模板全局函数，使得函数可以在 Jinja2 模板中直接调用。
    @setupmethod
    def add_template_global(
        self, f: ft.TemplateGlobalCallable, name: str | None = None
    ) -> None:
        """Register a custom template global function. Works exactly like the
        :meth:`template_global` decorator.

        .. versionadded:: 0.10

        :param name: the optional name of the global function, otherwise the
                     function name will be used.
        """
        self.jinja_env.globals[name or f.__name__] = f

    # 方法用于注册回调函数，在应用上下文销毁时执行清理操作。
    @setupmethod
    def teardown_appcontext(self, f: T_teardown) -> T_teardown:
        """Registers a function to be called when the application
        context is popped. The application context is typically popped
        after the request context for each request, at the end of CLI
        commands, or after a manually pushed context ends.

        .. code-block:: python

            with app.app_context():
                ...

        When the ``with`` block exits (or ``ctx.pop()`` is called), the
        teardown functions are called just before the app context is
        made inactive. Since a request context typically also manages an
        application context it would also be called when you pop a
        request context.

        When a teardown function was called because of an unhandled
        exception it will be passed an error object. If an
        :meth:`errorhandler` is registered, it will handle the exception
        and the teardown will not receive it.

        Teardown functions must avoid raising exceptions. If they
        execute code that might fail they must surround that code with a
        ``try``/``except`` block and log any errors.

        The return values of teardown functions are ignored.

        .. versionadded:: 0.9
        """
        # self.teardown_appcontext_funcs 是一个列表，用于存储所有注册的销毁回调函数。
        self.teardown_appcontext_funcs.append(f)
        return f

    # 用于注册一个函数，该函数返回的字典将变量或对象添加到 Flask Shell 上下文中。
    @setupmethod
    def shell_context_processor(
        self, f: T_shell_context_processor
    ) -> T_shell_context_processor:
        """Registers a shell context processor function.

        .. versionadded:: 0.11
        """
        self.shell_context_processors.append(f)
        return f

    # Flask 中一个内部方法，用于按优先级顺序查找合适的错误处理函数。
    def _find_error_handler(
        self, e: Exception, blueprints: list[str]
    ) -> ft.ErrorHandlerCallable | None:
        """Return a registered error handler for an exception in this order:
        blueprint handler for a specific code, app handler for a specific code,
        blueprint handler for an exception class, app handler for an exception
        class, or ``None`` if a suitable handler is not found.
        """
        # 提取异常的类（exc_class）和 HTTP 状态码（code，如果有）。
        exc_class, code = self._get_exc_class_and_code(type(e))
        # 将蓝图名称列表 blueprints 解包，并在末尾追加 None。
        names = (*blueprints, None)

        # 如果 code 存在，先尝试使用 code 查找处理函数，
        # 然后尝试不带状态码的处理函数（异常类级别的处理器）。
        # 如果 code 不存在，只查找基于异常类的处理器。
        for c in (code, None) if code is not None else (None,):
            for name in names:
                # 根据蓝图名称和状态码获取对应的处理器映射。
                handler_map = self.error_handler_spec[name][c]

                # 如果当前处理器映射为空，跳过。
                if not handler_map:
                    continue

                # 使用异常类的 方法解析顺序（MRO），即从当前类开始，逐层检查父类。
                for cls in exc_class.__mro__:
                    handler = handler_map.get(cls)

                    # 如果找到处理函数，立即返回。
                    if handler is not None:
                        return handler
        return None

    # 用于检查是否需要捕获（trap）由视图函数引发的 HTTP 异常（HTTPException）。
    def trap_http_exception(self, e: Exception) -> bool:
        """Checks if an HTTP exception should be trapped or not.  By default
        this will return ``False`` for all exceptions except for a bad request
        key error if ``TRAP_BAD_REQUEST_ERRORS`` is set to ``True``.  It
        also returns ``True`` if ``TRAP_HTTP_EXCEPTIONS`` is set to ``True``.

        This is called for all HTTP exceptions raised by a view function.
        If it returns ``True`` for any exception the error handler for this
        exception is not called and it shows up as regular exception in the
        traceback.  This is helpful for debugging implicitly raised HTTP
        exceptions.

        .. versionchanged:: 1.0
            Bad request errors are not trapped by default in debug mode.

        .. versionadded:: 0.8
        """
        if self.config["TRAP_HTTP_EXCEPTIONS"]:
            return True

        # 个独立的配置项，专门控制是否捕获 BadRequest 类异常
        # （例如 400 Bad Request 或其子类 BadRequestKeyError）。
        trap_bad_request = self.config["TRAP_BAD_REQUEST_ERRORS"]

        # 如果 TRAP_BAD_REQUEST_ERRORS 未设置（即为 None），
        # 且当前应用处于调试模式（self.debug 为 True）。
        # 且异常是 BadRequestKeyError 类型（通常由访问表单或查询字符串中缺失的键引发）。
        # 返回 True，捕获该异常。
        # if unset, trap key errors in debug mode
        if (
            trap_bad_request is None
            and self.debug
            and isinstance(e, BadRequestKeyError)
        ):
            return True

        # 如果 TRAP_BAD_REQUEST_ERRORS 为 True：
        # 检查异常是否是 BadRequest 类或其子类。
        # 如果是，返回 True，捕获该异常。
        if trap_bad_request:
            return isinstance(e, BadRequest)

        return False

    # 用于判断在应用的 teardown（清理）过程中是否应该忽略某个异常。
    def should_ignore_error(self, error: BaseException | None) -> bool:
        """This is called to figure out if an error should be ignored
        or not as far as the teardown system is concerned.  If this
        function returns ``True`` then the teardown handlers will not be
        passed the error.

        .. versionadded:: 0.10
        """
        return False

    # 用于生成重定向响应，支持动态 URL 和自定义状态码。
    def redirect(self, location: str, code: int = 302) -> BaseResponse:
        """Create a redirect response object.

        This is called by :func:`flask.redirect`, and can be called
        directly as well.

        :param location: The URL to redirect to.
        :param code: The status code for the redirect.

        .. versionadded:: 2.2
            Moved from ``flask.redirect``, which calls this method.
        """
        # _wz_redirect 是 Werkzeug 提供的内部工具函数，用于创建重定向响应。
        return _wz_redirect(
            location, # 目标 URL。
            code=code, # HTTP 状态码。
            # 使用当前应用的 response_class（通常是 Flask 的响应类）。
            Response=self.response_class,  # type: ignore[arg-type]
        )

    # Flask 中的一个内部方法，用于在 URL 生成过程中为参数字典注入默认值。
    def inject_url_defaults(self, endpoint: str, values: dict[str, t.Any]) -> None:
        """Injects the URL defaults for the given endpoint directly into
        the values dictionary passed.  This is used internally and
        automatically called on URL building.

        .. versionadded:: 0.7
        """
        # 初始化 names 为包含 None 的元组。
        names: t.Iterable[str | None] = (None,)

        # url_for may be called outside a request context, parse the
        # passed endpoint instead of using request.blueprints.
        # 如果 endpoint 包含 .，说明该端点属于某个蓝图。
        # 例如，"admin.dashboard" 表示蓝图 admin 的 dashboard 端点。
        if "." in endpoint:
            # 将 None 和分解后的蓝图名称连接起来，形成按优先级排列的搜索顺序。
            names = chain(
                # 调用 _split_blueprint_path 将蓝图路径分解成各级蓝图的名称。
                # 使用 reversed 确保从具体蓝图到全局依次注入默认值。
                names, reversed(_split_blueprint_path(endpoint.rpartition(".")[0]))
            )

        # 遍历 names，从具体蓝图到全局依次查找对应的默认值函数。
        for name in names:
            if name in self.url_default_functions:
                for func in self.url_default_functions[name]:
                    func(endpoint, values)

    # 通过调用已注册的处理函数，尝试处理 URL 构建异常。
    def handle_url_build_error(
        self, error: BuildError, endpoint: str, values: dict[str, t.Any]
    ) -> str:
        """Called by :meth:`.url_for` if a
        :exc:`~werkzeug.routing.BuildError` was raised. If this returns
        a value, it will be returned by ``url_for``, otherwise the error
        will be re-raised.

        Each function in :attr:`url_build_error_handlers` is called with
        ``error``, ``endpoint`` and ``values``. If a function returns
        ``None`` or raises a ``BuildError``, it is skipped. Otherwise,
        its return value is returned by ``url_for``.

        :param error: The active ``BuildError`` being handled.
        :param endpoint: The endpoint being built.
        :param values: The keyword arguments passed to ``url_for``.
        """
        # 遍历所有注册的 URL 构建错误处理函数。
        for handler in self.url_build_error_handlers:
            # 尝试执行当前的错误处理函数。
            try:
                rv = handler(error, endpoint, values)
            # 如果函数抛出了 BuildError，捕获异常并继续尝试下一个处理函数。
            except BuildError as e:
                # make error available outside except block
                error = e
            else:
                # 如果函数返回非 None 的值，返回该值（处理成功）。
                if rv is not None:
                    return rv

        # Re-raise if called with an active exception, otherwise raise
        # the passed in exception.
        # 检查 error 是否是当前上下文中的活动异常，使用 sys.exc_info()[1] 获取当前抛出的异常。
        # 如果相同，重新抛出异常（保留原始堆栈信息）。
        if error is sys.exc_info()[1]:
            raise

        # 如果没有活动异常，或者处理函数都失败，抛出传入的 error。
        raise error


