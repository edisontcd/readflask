from __future__ import annotations

# 用于动态加载模块。
import importlib.util
# 提供与操作系统交互的函数，如文件路径操作。
import os
# 提供面向对象的文件系统路径操作方式，常用于代替 os.path。
import pathlib
# 与 Python 解释器进行交互，比如访问命令行参数、模块、路径等。
import sys
# 引入 typing 模块，用于类型注解，重命名为 t 方便简写。
import typing as t
# 来自 collections 模块，是一种字典类型，支持为每个键提供默认值。
from collections import defaultdict
# 用于更新一个函数的包装器（如装饰器），使其保留原函数的元数据（如名称和文档字符串）。
from functools import update_wrapper

# jinja2 模板引擎的基类，用于加载模板。
from jinja2 import BaseLoader
# 从文件系统中加载模板的加载器。
from jinja2 import FileSystemLoader
# Werkzeug 提供的一组默认 HTTP 异常，如 404、500 等。
from werkzeug.exceptions import default_exceptions
# Werkzeug 提供的基础 HTTP 异常类，所有 HTTP 异常都继承自它。
from werkzeug.exceptions import HTTPException
# Werkzeug 提供的装饰器，将一个方法的结果缓存为属性，只计算一次，之后多次调用时使用缓存结果。
from werkzeug.utils import cached_property

# 表示从当前模块的上一级导入模块或函数。
from .. import typing as ft
# 获取 Flask 应用的根目录路径。
from ..helpers import get_root_path
# templating 模块中的默认模板上下文处理器，它提供给 Jinja2 模板引擎的默认上下文变量
#（如 request, session, g 等）。
from ..templating import _default_template_ctx_processor

# 此代码块仅在类型检查工具（如 MyPy）运行时执行，不会在实际运行时执行。
if t.TYPE_CHECKING:  # pragma: no cover
    # 从 click 模块导入 Group 类，click 是一个用于创建命令行接口的 Python 包，Group 表示命令组。
    from click import Group

# a singleton sentinel value for parameter defaults
# 创建了一个单例哨兵对象，用于表示某种特殊状态或默认值。
_sentinel = object()

# F 是一个类型变量，表示函数类型，约束为任何可调用对象。
# TypeVar 用于泛型编程，这里用于函数装饰器中，表示该装饰器可以接受并返回任意可调用对象。
F = t.TypeVar("F", bound=t.Callable[..., t.Any])
# 定义了若干类型变量 T_after_request, T_before_request, T_error_handler, T_teardown，
# 分别约束为不同的回调函数类型。这些类型通常用于 Flask 应用中的请求处理流程，
# 包括请求前后处理、错误处理和上下文清理。
T_after_request = t.TypeVar("T_after_request", bound=ft.AfterRequestCallable[t.Any])
T_before_request = t.TypeVar("T_before_request", bound=ft.BeforeRequestCallable)
T_error_handler = t.TypeVar("T_error_handler", bound=ft.ErrorHandlerCallable)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
# 表示模板上下文处理器的回调函数类型。
T_template_context_processor = t.TypeVar(
    "T_template_context_processor", bound=ft.TemplateContextProcessorCallable
)
# URL 默认值处理器。
T_url_defaults = t.TypeVar("T_url_defaults", bound=ft.URLDefaultCallable)
# URL 值预处理器的回调函数类型。
T_url_value_preprocessor = t.TypeVar(
    "T_url_value_preprocessor", bound=ft.URLValuePreprocessorCallable
)
# 表示路由处理函数的类型。
T_route = t.TypeVar("T_route", bound=ft.RouteCallable)


# 饰器函数 setupmethod，它用于包装类方法，并在调用该方法之前检查类是否已经完成了某些 "设置" 工作。
# F 是一个泛型，表示任何类型的函数。
def setupmethod(f: F) -> F:
    # 通过 f.__name__，获取被装饰函数的名称 f_name。这通常用于后续调试或错误提示。
    f_name = f.__name__

    def wrapper_func(self: Scaffold, *args: t.Any, **kwargs: t.Any) -> t.Any:
        # 检查当前类实例的设置是否已经完成。
        self._check_setup_finished(f_name)
        # 如果设置完成，调用原始函数 f 并返回其结果。
        return f(self, *args, **kwargs)

    # 将原始函数 f 的元数据（如函数名称、文档字符串等）复制到包装函数 wrapper_func 上。
    # 这样即使函数被装饰，它的名称和文档字符串仍然保持原样。
    return t.cast(F, update_wrapper(wrapper_func, f))


# 定义了 Flask 应用程序和蓝图（Blueprint）所共有的操作，抽象了它们的共同部分，
# 使得 Flask 框架中的应用和蓝图能够共享相同的功能。
# 它提供了静态文件、模板管理、视图函数注册、请求处理钩子和错误处理的核心功能。
class Scaffold:
    """Common behavior shared between :class:`~flask.Flask` and
    :class:`~flask.blueprints.Blueprint`.

    :param import_name: The import name of the module where this object
        is defined. Usually :attr:`__name__` should be used.
    :param static_folder: Path to a folder of static files to serve.
        If this is set, a static route will be added.
    :param static_url_path: URL prefix for the static route.
    :param template_folder: Path to a folder containing template files.
        for rendering. If this is set, a Jinja loader will be added.
    :param root_path: The path that static, template, and resource files
        are relative to. Typically not set, it is discovered based on
        the ``import_name``.

    .. versionadded:: 2.0
    """

    # Flask 的命令行接口 (CLI) 使用 click.Group，这个属性用于存储命令行命令的分组。
    cli: Group
    # Flask 应用程序或 Blueprint 的名称。
    name: str
    # 用于定义静态文件夹路径和 URL 路径，提供静态文件服务。
    _static_folder: str | None = None
    _static_url_path: str | None = None

    # 构造函数。
    def __init__(
        self,
        # 当前对象所属模块的导入名称，通常是 __name__。
        import_name: str,
        # 用于指定静态文件的路径。
        static_folder: str | os.PathLike[str] | None = None,
        # 静态文件 URL 的前缀路径。
        static_url_path: str | None = None,
        # 模板文件的路径，Flask 会从这里加载 Jinja 模板。
        template_folder: str | os.PathLike[str] | None = None,
        # 静态文件、模板、资源的根路径，如果不指定，将自动根据 import_name 计算。
        root_path: str | None = None,
    ):
        #: The name of the package or module that this object belongs
        #: to. Do not change this once it is set by the constructor.
        # 将传入的参数 import_name 赋值给 self.import_name，
        # 这样这个值就会成为当前对象的一个实例属性，可以在类的其他方法中使用。
        self.import_name = import_name

        self.static_folder = static_folder  # type: ignore
        self.static_url_path = static_url_path

        #: The path to the templates folder, relative to
        #: :attr:`root_path`, to add to the template loader. ``None`` if
        #: templates should not be added.
        self.template_folder = template_folder

        if root_path is None:
            root_path = get_root_path(self.import_name)

        #: Absolute path to the package on the filesystem. Used to look
        #: up resources contained in the package.
        self.root_path = root_path

        #: A dictionary mapping endpoint names to view functions.
        #:
        #: To register a view function, use the :meth:`route` decorator.
        #:
        #: This data structure is internal. It should not be modified
        #: directly and its format may change at any time.
        # 存储视图函数（即路由对应的处理函数）。每个路由的 endpoint 名称映射到一个视图函数。
        self.view_functions: dict[str, ft.RouteCallable] = {}

        #: A data structure of registered error handlers, in the format
        #: ``{scope: {code: {class: handler}}}``. The ``scope`` key is
        #: the name of a blueprint the handlers are active for, or
        #: ``None`` for all requests. The ``code`` key is the HTTP
        #: status code for ``HTTPException``, or ``None`` for
        #: other exceptions. The innermost dictionary maps exception
        #: classes to handler functions.
        #:
        #: To register an error handler, use the :meth:`errorhandler`
        #: decorator.
        #:
        #: This data structure is internal. It should not be modified
        #: directly and its format may change at any time.
        # 错误处理函数的注册表，以 HTTP 状态码或异常类型为键，存储相应的错误处理函数。
        # 支持全局和 Blueprint 范围内的错误处理。
        self.error_handler_spec: dict[
            ft.AppOrBlueprintKey,
            dict[int | None, dict[type[Exception], ft.ErrorHandlerCallable]],
        ] = defaultdict(lambda: defaultdict(dict))

        #: A data structure of functions to call at the beginning of
        #: each request, in the format ``{scope: [functions]}``. The
        #: ``scope`` key is the name of a blueprint the functions are
        #: active for, or ``None`` for all requests.
        #:
        #: To register a function, use the :meth:`before_request`
        #: decorator.
        #:
        #: This data structure is internal. It should not be modified
        #: directly and its format may change at any time.
        # 存储请求前的处理函数，在每次请求开始前调用。支持全局和 Blueprint 范围。
        self.before_request_funcs: dict[
            ft.AppOrBlueprintKey, list[ft.BeforeRequestCallable]
        ] = defaultdict(list)

        #: A data structure of functions to call at the end of each
        #: request, in the format ``{scope: [functions]}``. The
        #: ``scope`` key is the name of a blueprint the functions are
        #: active for, or ``None`` for all requests.
        #:
        #: To register a function, use the :meth:`after_request`
        #: decorator.
        #:
        #: This data structure is internal. It should not be modified
        #: directly and its format may change at any time.
        # 存储请求后的处理函数，在请求处理完成后调用。支持全局和 Blueprint 范围。
        self.after_request_funcs: dict[
            ft.AppOrBlueprintKey, list[ft.AfterRequestCallable[t.Any]]
        ] = defaultdict(list)

        #: A data structure of functions to call at the end of each
        #: request even if an exception is raised, in the format
        #: ``{scope: [functions]}``. The ``scope`` key is the name of a
        #: blueprint the functions are active for, or ``None`` for all
        #: requests.
        #:
        #: To register a function, use the :meth:`teardown_request`
        #: decorator.
        #:
        #: This data structure is internal. It should not be modified
        #: directly and its format may change at any time.
        # 存储清理处理函数，响应生成之后，甚至是发生异常时都会调用。支持全局和 Blueprint 范围。
        self.teardown_request_funcs: dict[
            ft.AppOrBlueprintKey, list[ft.TeardownCallable]
        ] = defaultdict(list)

        #: A data structure of functions to call to pass extra context
        #: values when rendering templates, in the format
        #: ``{scope: [functions]}``. The ``scope`` key is the name of a
        #: blueprint the functions are active for, or ``None`` for all
        #: requests.
        #:
        #: To register a function, use the :meth:`context_processor`
        #: decorator.
        #:
        #: This data structure is internal. It should not be modified
        #: directly and its format may change at any time.
        # 模板上下文处理器，用于在渲染模板时提供额外的上下文。默认包含 _default_template_ctx_processor，
        # 这个处理器会在渲染时注入一些常用的上下文变量，比如 request 和 g。
        self.template_context_processors: dict[
            ft.AppOrBlueprintKey, list[ft.TemplateContextProcessorCallable]
        ] = defaultdict(list, {None: [_default_template_ctx_processor]})

        #: A data structure of functions to call to modify the keyword
        #: arguments passed to the view function, in the format
        #: ``{scope: [functions]}``. The ``scope`` key is the name of a
        #: blueprint the functions are active for, or ``None`` for all
        #: requests.
        #:
        #: To register a function, use the
        #: :meth:`url_value_preprocessor` decorator.
        #:
        #: This data structure is internal. It should not be modified
        #: directly and its format may change at any time.
        # 在 URL 和视图函数之间传递的参数处理函数。这些处理函数会在请求到达视图函数之前，对参数进行预处理。
        self.url_value_preprocessors: dict[
            ft.AppOrBlueprintKey,
            list[ft.URLValuePreprocessorCallable],
        ] = defaultdict(list)

        #: A data structure of functions to call to modify the keyword
        #: arguments when generating URLs, in the format
        #: ``{scope: [functions]}``. The ``scope`` key is the name of a
        #: blueprint the functions are active for, or ``None`` for all
        #: requests.
        #:
        #: To register a function, use the :meth:`url_defaults`
        #: decorator.
        #:
        #: This data structure is internal. It should not be modified
        #: directly and its format may change at any time.
        # 用于在生成 URL 时添加额外参数的处理函数，主要作用是在生成 URL 时提供默认参数。
        self.url_default_functions: dict[
            ft.AppOrBlueprintKey, list[ft.URLDefaultCallable]
        ] = defaultdict(list)


        # Python 的特殊方法之一，用来为对象提供“官方的”字符串表示。
        # 用于返回对象的字符串表示，用于调试或查看对象的相关信息。
        def __repr__(self) -> str:
            # 表示对象的类名和属性 name。
            return f"<{type(self).__name__} {self.name!r}>"

        # 是一个占位符方法，表明某个功能尚未实现，子类应该重写该方法并提供具体的逻辑。
        def _check_setup_finished(self, f_name: str) -> None:
            # 表示该方法是抽象的或者是未实现的，如果该方法被调用，会抛出 NotImplementedError 异常。
            raise NotImplementedError


        # 定义了一个名为 static_folder 的只读属性，用于获取静态文件夹的绝对路径。
        # @property 装饰器将方法转换为一个只读属性。
        # 这意味着我们可以像访问类的普通属性那样访问 static_folder，而不需要像调用方法一样使用括号。
        @property
        def static_folder(self) -> str | None:
            """The absolute path to the configured static folder. ``None``
            if no static folder is set.
            """
            # self._static_folder 是 Scaffold 类的一个属性，表示静态文件夹的路径，相对 root_path 而言。
            if self._static_folder is not None:
                return os.path.join(self.root_path, self._static_folder)
            else:
                return None

        # Python 属性的 setter 方法装饰器。它用于为之前定义的 static_folder 属性提供一个设置值的接口。
        # 这使得 static_folder 属性可以像普通变量那样被重新赋值。
        @static_folder.setter
        def static_folder(self, value: str | os.PathLike[str] | None) -> None:
            if value is not None:
                # 将 value 转换为文件系统路径字符串。
                # 如果 value 是一个 os.PathLike 对象（例如 pathlib.Path 实例），
                # 它会被转换为一个字符串路径。
                # rstrip(r"\/")：去除路径末尾的斜杠和反斜杠（例如 / 和 \），以保证路径格式一致。
                value = os.fspath(value).rstrip(r"\/")

            # 将处理后的 value 赋给内部属性 _static_folder。
            self._static_folder = value


        # @property 把判断 static_folder 是否存在的逻辑变成了属性访问的方式，
        # 调用时不需要括号，并返回一个布尔值。
        @property
        # 这个方法用于检查当前实例是否有一个 static_folder 属性。
        def has_static_folder(self) -> bool:
            """``True`` if :attr:`static_folder` is set.

            .. versionadded:: 0.5
            """
            return self.static_folder is not None


        # 是一个动态属性，用于表示静态资源文件的 URL 路径。
        @property
        def static_url_path(self) -> str | None:
            """The URL prefix that the static route will be accessible from.

            If it was not configured during init, it is derived from
            :attr:`static_folder`.
            """
            # 首先检查私有属性 _static_url_path 是否已经有值。如果它不为 None，则直接返回该值。
            if self._static_url_path is not None:
                return self._static_url_path

            # static_folder 已设置，则从 static_folder 推导出路径。
            if self.static_folder is not None:
                # 返回 static_folder 路径的最后一个部分（即目录名称）。
                basename = os.path.basename(self.static_folder)
                # 创建一个 URL 路径格式，并去除结尾的 /，以确保路径格式一致。
                return f"/{basename}".rstrip("/")

            return None

        # 设置 static_url_path 属性的值。
        @static_url_path.setter
        # 处理值：如果传入的 value 不为 None，则去除该字符串末尾的斜杠 /。
        def static_url_path(self, value: str | None) -> None:
            if value is not None:
                # 目的是：为了保持路径的一致性，去掉末尾可能出现的多余 /。
                value = value.rstrip("/")

            self._static_url_path = value


        # @cached_property 是一个装饰器，用来将方法的返回值缓存起来。
        # 第一次访问时执行方法并缓存结果，之后的访问直接返回缓存的结果，而不再调用方法。
        # 这在需要重复计算、但结果不会改变的属性中非常有用。
        # 适合那些需要在实例生命周期中只初始化一次的属性，避免重复计算或加载（如模板加载器）。
        @cached_property
        def jinja_loader(self) -> BaseLoader | None:
            """The Jinja loader for this object's templates. By default this
            is a class :class:`jinja2.loaders.FileSystemLoader` to
            :attr:`template_folder` if it is set.

            .. versionadded:: 0.5
            """
            if self.template_folder is not None:
                # FileSystemLoader 是 Jinja 的模板加载器，用于从文件系统中加载模板。
                # os.path.join(self.root_path, self.template_folder) 
                # 通过拼接 root_path 和 template_folder 构成模板文件夹的完整路径，
                # 传递给 FileSystemLoader 来创建加载器。
                return FileSystemLoader(os.path.join(self.root_path, self.template_folder))
            else:
                return None


        # 方法名前加了 _，意味着这是一个私有方法，通常仅在类的内部使用，不用于公开接口。
        # 用于为单个 HTTP 方法（如 "GET"、"POST"）创建路由。
        def _method_route(
            self,
            # 传入的 HTTP 方法（例如 "GET", "POST" 等）。
            method: str,
            # 这是 URL 路径规则，用于为某个路径设置路由。
            rule: str,
            options: dict[str, t.Any],
        ) -> t.Callable[[T_route], T_route]:
            # 判断 options 字典中是否包含 methods 参数。
            if "methods" in options:
                raise TypeError("Use the 'route' decorator to use the 'methods' argument.")

            return self.route(rule, methods=[method], **options)


        # 为HTTP GET请求提供了快捷方式，简化了路由的定义。
        # @setupmethod 是一个自定义的装饰器，通常用于框架内的方法来指示这些方法是设置相关的
        #（例如，用于配置路由或初始化）。它可以用于确保这些方法仅在应用启动时调用。
        @setupmethod
        def get(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
            """Shortcut for :meth:`route` with ``methods=["GET"]``.

            .. versionadded:: 2.0
            """
            # _method_route 返回的是一个装饰器函数，这个函数可以用于将指定路径的 GET 请求与视图函数关联。
            return self._method_route("GET", rule, options)

        # 为HTTP POST请求提供了快捷方式，简化了路由的定义。
        @setupmethod
        def post(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
            """Shortcut for :meth:`route` with ``methods=["POST"]``.

            .. versionadded:: 2.0
            """
            # 返回一个装饰器函数，用于绑定指定路径和 POST 请求的处理函数。
            return self._method_route("POST", rule, options)

        # 为HTTP PUT请求提供了快捷方式，简化了路由的定义。
        @setupmethod
        def put(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
            """Shortcut for :meth:`route` with ``methods=["PUT"]``.

            .. versionadded:: 2.0
            """
            return self._method_route("PUT", rule, options)

        # 为HTTP DELETE请求提供了快捷方式，简化了路由的定义。
        @setupmethod
        def delete(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
            """Shortcut for :meth:`route` with ``methods=["DELETE"]``.

            .. versionadded:: 2.0
            """
            return self._method_route("DELETE", rule, options)

        # 提供了为 HTTP PATCH 请求定义路由的快捷方式。
        @setupmethod
        def patch(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
            """Shortcut for :meth:`route` with ``methods=["PATCH"]``.

            .. versionadded:: 2.0
            """
            return self._method_route("PATCH", rule, options)

        # 一个更通用的装饰器，用于为任何 URL 路径注册视图函数。
        @setupmethod
        def route(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
            """Decorate a view function to register it with the given URL
            rule and options. Calls :meth:`add_url_rule`, which has more
            details about the implementation.

            .. code-block:: python

                @app.route("/")
                def index():
                    return "Hello, World!"

            See :ref:`url-route-registrations`.

            The endpoint name for the route defaults to the name of the view
            function if the ``endpoint`` parameter isn't passed.

            The ``methods`` parameter defaults to ``["GET"]``. ``HEAD`` and
            ``OPTIONS`` are added automatically.

            :param rule: The URL rule string.
            :param options: Extra options passed to the
                :class:`~werkzeug.routing.Rule` object.
            """

            # 实际装饰视图函数的内部函数。
            def decorator(f: T_route) -> T_route:
                # 从 options 字典中弹出（移除并返回）endpoint 参数，
                # 如果没有传入 endpoint，则默认为 None。
                endpoint = options.pop("endpoint", None)
                # 将路由规则、端点名称、视图函数和其他选项注册到路由系统中。
                self.add_url_rule(rule, endpoint, f, **options)
                return f

            return decorator

        # 用于在 Flask-like 框架中注册一个 URL 规则，并将其与指定的视图函数（view_func）关联。
        @setupmethod
        def add_url_rule(
            self,
            rule: str,
            endpoint: str | None = None,
            # 处理请求的视图函数。如果没有指定视图函数，路由可以暂时只注册路径，稍后通过端点进行关联。
            view_func: ft.RouteCallable | None = None,
            provide_automatic_options: bool | None = None,
            **options: t.Any,
        ) -> None:
            """Register a rule for routing incoming requests and building
            URLs. The :meth:`route` decorator is a shortcut to call this
            with the ``view_func`` argument. These are equivalent:

            .. code-block:: python

                @app.route("/")
                def index():
                    ...

            .. code-block:: python

                def index():
                    ...

                app.add_url_rule("/", view_func=index)

            See :ref:`url-route-registrations`.

            The endpoint name for the route defaults to the name of the view
            function if the ``endpoint`` parameter isn't passed. An error
            will be raised if a function has already been registered for the
            endpoint.

            The ``methods`` parameter defaults to ``["GET"]``. ``HEAD`` is
            always added automatically, and ``OPTIONS`` is added
            automatically by default.

            ``view_func`` does not necessarily need to be passed, but if the
            rule should participate in routing an endpoint name must be
            associated with a view function at some point with the
            :meth:`endpoint` decorator.

            .. code-block:: python

                app.add_url_rule("/", endpoint="index")

                @app.endpoint("index")
                def index():
                    ...

            If ``view_func`` has a ``required_methods`` attribute, those
            methods are added to the passed and automatic methods. If it
            has a ``provide_automatic_methods`` attribute, it is used as the
            default if the parameter is not passed.

            :param rule: The URL rule string.
            :param endpoint: The endpoint name to associate with the rule
                and view function. Used when routing and building URLs.
                Defaults to ``view_func.__name__``.
            :param view_func: The view function to associate with the
                endpoint name.
            :param provide_automatic_options: Add the ``OPTIONS`` method and
                respond to ``OPTIONS`` requests automatically.
            :param options: Extra options passed to the
                :class:`~werkzeug.routing.Rule` object.
            """
            raise NotImplementedError


        # 将视图函数注册到特定的端点。
        @setupmethod
        def endpoint(self, endpoint: str) -> t.Callable[[F], F]:
            """Decorate a view function to register it for the given
            endpoint. Used if a rule is added without a ``view_func`` with
            :meth:`add_url_rule`.

            .. code-block:: python

                app.add_url_rule("/ex", endpoint="example")

                @app.endpoint("example")
                def example():
                    ...

            :param endpoint: The endpoint name to associate with the view
                function.
            """

            # 这个内部函数 decorator 是实际的装饰器，用于将视图函数 f 与指定的端点 endpoint 关联。
            def decorator(f: F) -> F:
                # 是一个字典，存储了所有已注册的端点与视图函数的映射关系。
                self.view_functions[endpoint] = f
                return f

            return decorator


        # 注册一个函数，在每个请求处理之前运行。
        # 通常用于执行一些预处理操作，例如打开数据库连接或从会话中加载当前用户。
        @setupmethod
        def before_request(self, f: T_before_request) -> T_before_request:
            """Register a function to run before each request.

            For example, this can be used to open a database connection, or
            to load the logged in user from the session.

            .. code-block:: python

                @app.before_request
                def load_user():
                    if "user_id" in session:
                        g.user = db.session.get(session["user_id"])

            The function will be called without any arguments. If it returns
            a non-``None`` value, the value is handled as if it was the
            return value from the view, and further request handling is
            stopped.

            This is available on both app and blueprint objects. When used on an app, this
            executes before every request. When used on a blueprint, this executes before
            every request that the blueprint handles. To register with a blueprint and
            execute before every request, use :meth:`.Blueprint.before_app_request`.
            """
            # before_request_funcs 字典：这是一个存储所有 before_request 注册函数的字典。
            # 如果字典中还没有 None 键，就为它创建一个空列表。
            # 将传入的函数 f 添加到列表中。
            self.before_request_funcs.setdefault(None, []).append(f)
            return f


        # 注册一个函数，在每次请求处理完成并生成响应后执行。
        # 注册的函数会接收响应对象作为参数，并且可以对响应对象进行修改或替换，然后返回修改后的响应。
        @setupmethod
        def after_request(self, f: T_after_request) -> T_after_request:
            """Register a function to run after each request to this object.

            The function is called with the response object, and must return
            a response object. This allows the functions to modify or
            replace the response before it is sent.

            If a function raises an exception, any remaining
            ``after_request`` functions will not be called. Therefore, this
            should not be used for actions that must execute, such as to
            close resources. Use :meth:`teardown_request` for that.

            This is available on both app and blueprint objects. When used on an app, this
            executes after every request. When used on a blueprint, this executes after
            every request that the blueprint handles. To register with a blueprint and
            execute after every request, use :meth:`.Blueprint.after_app_request`.
            """
            self.after_request_funcs.setdefault(None, []).append(f)
            return f


        # 注册一个函数，在请求上下文（request context）弹出时执行。
        # 这个函数会在每次请求结束时调用，用于清理资源或执行其他与请求结束相关的操作。
        # 如果请求因为未处理的异常结束，函数会接收到异常对象。
        @setupmethod
        def teardown_request(self, f: T_teardown) -> T_teardown:
            """Register a function to be called when the request context is
            popped. Typically this happens at the end of each request, but
            contexts may be pushed manually as well during testing.

            .. code-block:: python

                with app.test_request_context():
                    ...

            When the ``with`` block exits (or ``ctx.pop()`` is called), the
            teardown functions are called just before the request context is
            made inactive.

            When a teardown function was called because of an unhandled
            exception it will be passed an error object. If an
            :meth:`errorhandler` is registered, it will handle the exception
            and the teardown will not receive it.

            Teardown functions must avoid raising exceptions. If they
            execute code that might fail they must surround that code with a
            ``try``/``except`` block and log any errors.

            The return values of teardown functions are ignored.

            This is available on both app and blueprint objects. When used on an app, this
            executes after every request. When used on a blueprint, this executes after
            every request that the blueprint handles. To register with a blueprint and
            execute after every request, use :meth:`.Blueprint.teardown_app_request`.
            """
            self.teardown_request_funcs.setdefault(None, []).append(f)
            return f


        # 用于注册一个模板上下文处理器函数，该函数会在渲染模板之前运行。
        # 常用于在模板中提供一些全局的变量或常用数据（如用户信息、当前时间等），便于在模板中直接访问。
        @setupmethod
        def context_processor(
            self,
            f: T_template_context_processor,
        ) -> T_template_context_processor:
            """Registers a template context processor function. These functions run before
            rendering a template. The keys of the returned dict are added as variables
            available in the template.

            This is available on both app and blueprint objects. When used on an app, this
            is called for every rendered template. When used on a blueprint, this is called
            for templates rendered from the blueprint's views. To register with a blueprint
            and affect every template, use :meth:`.Blueprint.app_context_processor`.
            """
            self.template_context_processors[None].append(f)
            return f


        # 用于注册一个 URL 值预处理器函数。
        # 该函数会在请求匹配 URL 后和视图函数调用前运行，并可以对 URL 中提取的参数进行修改。
        # 常用于提取 URL 参数中的公共数据并存储到全局对象（如 g 对象）中，避免将其显式传递给每个视图函数。
        @setupmethod
        def url_value_preprocessor(
            self,
            f: T_url_value_preprocessor,
        ) -> T_url_value_preprocessor:
            """Register a URL value preprocessor function for all view
            functions in the application. These functions will be called before the
            :meth:`before_request` functions.

            The function can modify the values captured from the matched url before
            they are passed to the view. For example, this can be used to pop a
            common language code value and place it in ``g`` rather than pass it to
            every view.

            The function is passed the endpoint name and values dict. The return
            value is ignored.

            This is available on both app and blueprint objects. When used on an app, this
            is called for every request. When used on a blueprint, this is called for
            requests that the blueprint handles. To register with a blueprint and affect
            every request, use :meth:`.Blueprint.app_url_value_preprocessor`.
            """
            self.url_value_preprocessors[None].append(f)
            return f

        
        # 用于注册一个 URL 默认值回调函数，在生成 URL 时添加或修改默认参数。
        # 可用于在构建 URL 时自动填充一些常用的参数值（例如语言或版本），从而简化 URL 生成。
        @setupmethod
        def url_defaults(self, f: T_url_defaults) -> T_url_defaults:
            """Callback function for URL defaults for all view functions of the
            application.  It's called with the endpoint and values and should
            update the values passed in place.

            This is available on both app and blueprint objects. When used on an app, this
            is called for every request. When used on a blueprint, this is called for
            requests that the blueprint handles. To register with a blueprint and affect
            every request, use :meth:`.Blueprint.app_url_defaults`.
            """
            self.url_default_functions[None].append(f)
            return f


        # 用于注册一个错误处理函数，可以指定 HTTP 状态码或异常类型。
        # 函数将在匹配的错误或异常发生时调用。
        # 常用于自定义 HTTP 错误页（如 404、500 错误页面）或为特定异常类型提供自定义响应。
        @setupmethod
        def errorhandler(
            self, code_or_exception: type[Exception] | int
        ) -> t.Callable[[T_error_handler], T_error_handler]:
            """Register a function to handle errors by code or exception class.

            A decorator that is used to register a function given an
            error code.  Example::

                @app.errorhandler(404)
                def page_not_found(error):
                    return 'This page does not exist', 404

            You can also register handlers for arbitrary exceptions::

                @app.errorhandler(DatabaseError)
                def special_exception_handler(error):
                    return 'Database connection failed', 500

            This is available on both app and blueprint objects. When used on an app, this
            can handle errors from every request. When used on a blueprint, this can handle
            errors from requests that the blueprint handles. To register with a blueprint
            and affect every request, use :meth:`.Blueprint.app_errorhandler`.

            .. versionadded:: 0.7
                Use :meth:`register_error_handler` instead of modifying
                :attr:`error_handler_spec` directly, for application wide error
                handlers.

            .. versionadded:: 0.7
                One can now additionally also register custom exception types
                that do not necessarily have to be a subclass of the
                :class:`~werkzeug.exceptions.HTTPException` class.

            :param code_or_exception: the code as integer for the handler, or
                                  an arbitrary exception
            """

            # 是实际的装饰器函数，用于将错误处理函数 f 与指定的错误代码或异常类型关联。
            def decorator(f: T_error_handler) -> T_error_handler:
                self.register_error_handler(code_or_exception, f)
                return f

            return decorator


        # 用于注册错误处理程序，可以处理特定的 HTTP 状态码或异常类型，提供了一种非装饰器的使用方式。
        # 常用于在应用初始化时为特定错误或异常设置响应，例如自定义错误页或记录异常。
        @setupmethod
        def register_error_handler(
            self,
            code_or_exception: type[Exception] | int,
            f: ft.ErrorHandlerCallable,
        ) -> None:
            """Alternative error attach function to the :meth:`errorhandler`
            decorator that is more straightforward to use for non decorator
            usage.

            .. versionadded:: 0.7
            """
            # 从 code_or_exception 参数中提取异常类和状态码。
            # exc_class 是异常类，code 是对应的 HTTP 状态码。
            exc_class, code = self._get_exc_class_and_code(code_or_exception)
            # 将错误处理函数 f 注册到相应的状态码和异常类下。
            self.error_handler_spec[None][code][exc_class] = f


        # 用于获取指定的异常类和其状态码，确保处理的错误是有效的 HTTP 错误代码或异常类型。
        # 常用于注册错误处理程序时，以确保处理的异常类或代码是有效的，从而正确处理错误情况。
        @staticmethod
        def _get_exc_class_and_code(
            # 参数可以是异常类（类型）或 HTTP 状态码（整数）。
            exc_class_or_code: type[Exception] | int,
        # 返回一个元组，包含异常类和可选的状态码。
        ) -> tuple[type[Exception], int | None]:
            """Get the exception class being handled. For HTTP status codes
            or ``HTTPException`` subclasses, return both the exception and
            status code.

            :param exc_class_or_code: Any exception class, or an HTTP status
            code as an integer.
            """
            # 声明变量 exc_class，类型为异常类。
            exc_class: type[Exception]

            # 如果 exc_class_or_code 是整数，尝试从 default_exceptions 字典中获取对应的异常类。
            if isinstance(exc_class_or_code, int):
                try:
                    exc_class = default_exceptions[exc_class_or_code]
                except KeyError:
                    raise ValueError(
                        f"'{exc_class_or_code}' is not a recognized HTTP"
                        " error code. Use a subclass of HTTPException with"
                     " that code instead."
                    ) from None
            # 如果不是整数，直接将其赋值给 exc_class。
            else:
                exc_class = exc_class_or_code

            # 如果 exc_class 是异常的实例，抛出 TypeError，提示只能注册异常类。
            if isinstance(exc_class, Exception):
                raise TypeError(
                    f"{exc_class!r} is an instance, not a class. Handlers"
                    " can only be registered for Exception classes or HTTP"
                    " error codes."
                )

            # 如果 exc_class 不是 Exception 的子类，抛出 ValueError。
            if not issubclass(exc_class, Exception):
                raise ValueError(
                    f"'{exc_class.__name__}' is not a subclass of Exception."
                    " Handlers can only be registered for Exception classes"
                    " or HTTP error codes."
                )

            # 如果 exc_class 是 HTTPException 的子类，返回 exc_class 和对应的状态码。
            if issubclass(exc_class, HTTPException):
                return exc_class, exc_class.code
            else:
                return exc_class, None


# 用于提取给定视图函数的名称，以便用作默认的端点名称。
# 参数 view_func 是一个可调用的视图函数，类型为 RouteCallable，通常表示处理请求的函数。
# 返回一个字符串，表示端点名称。
def _endpoint_from_view_func(view_func: ft.RouteCallable) -> str:
    """Internal helper that returns the default endpoint for a given
    function.  This always is the function name.
    """
    # 断言检查：确保 view_func 不是 None。如果为 None，则抛出异常，提示必须提供视图函数。
    assert view_func is not None, "expected view func if endpoint is not provided."
    # 直接返回 view_func 的名称，即 __name__ 属性，
    # 这是 Python 中每个函数都有的一个属性，用于获取函数的名称。
    return view_func.__name__


# 用于检查给定的路径是否相对于指定的基路径。
def _path_is_relative_to(path: pathlib.PurePath, base: str) -> bool:
    # Path.is_relative_to doesn't exist until Python 3.9
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


# 查找包含指定包或模块的路径。
# 参数 import_name 是一个字符串，表示要查找的包或模块的名称。
def _find_package_path(import_name: str) -> str:
    """Find the path that contains the package or module."""
    # 将 import_name 按照第一个点分隔，提取出根模块名称 root_mod_name。
    root_mod_name, _, _ = import_name.partition(".")

    try:
        # 查找根模块的规范。
        root_spec = importlib.util.find_spec(root_mod_name)

        if root_spec is None:
            raise ValueError("not found")
    # 如果捕获到 ImportError 或 ValueError，返回当前工作目录，表示模块未找到。
    except (ImportError, ValueError):
        # ImportError: the machinery told us it does not exist
        # ValueError:
        #    - the module name was invalid
        #    - the module name is __main__
        #    - we raised `ValueError` due to `root_spec` being `None`
        # 如果发生这些异常，则返回当前工作目录 os.getcwd()，表示未找到模块或包。
        return os.getcwd()

    # 检查根模块是否有子模块的搜索位置，如果有，则继续处理。
    if root_spec.submodule_search_locations:
        # 如果模块的原始来源为 None 或 namespace，表示它是一个命名空间包。
        if root_spec.origin is None or root_spec.origin == "namespace":
            # namespace package
            # 再次使用 find_spec 方法查找完整的包规范。
            package_spec = importlib.util.find_spec(import_name)

            # 如果找到包规范并且具有子模块搜索位置，继续处理。
            if package_spec is not None and package_spec.submodule_search_locations:
                # Pick the path in the namespace that contains the submodule.
                package_path = pathlib.Path(
                    # 获取所有子模块搜索位置的共同路径，并将其转换为 Path 对象。
                    os.path.commonpath(package_spec.submodule_search_locations)
                )
                # 在根模块的子模块搜索位置中，找到与 package_path 相对的路径。
                search_location = next(
                    location
                    for location in root_spec.submodule_search_locations
                    if _path_is_relative_to(package_path, location)
                )
            else:
                # Pick the first path.
                # 如果未找到相对路径，则选择第一个子模块搜索位置。
                search_location = root_spec.submodule_search_locations[0]

            # 返回包含子模块的目录路径。
            return os.path.dirname(search_location)
        else:
            # package with __init__.py
            # 如果模块有 __init__.py，则返回包的上级目录路径。
            return os.path.dirname(os.path.dirname(root_spec.origin))
    else:
        # module
        # 如果没有子模块搜索位置，返回模块的目录路径。
        return os.path.dirname(root_spec.origin)  # type: ignore[type-var, return-value]


# 用于查找给定包的安装前缀和导入路径。
# 能够区分系统安装和虚拟环境的情况，并处理不同操作系统的目录结构。
def find_package(import_name: str) -> tuple[str | None, str]:
    """Find the prefix that a package is installed under, and the path
    that it would be imported from.

    The prefix is the directory containing the standard directory
    hierarchy (lib, bin, etc.). If the package is not installed to the
    system (:attr:`sys.prefix`) or a virtualenv (``site-packages``),
    ``None`` is returned.

    The path is the entry in :attr:`sys.path` that contains the package
    for import. If the package is not installed, it's assumed that the
    package was imported from the current working directory.
    """
    # 使用 _find_package_path 函数查找给定包的路径，并将其存储在 package_path 变量中。
    package_path = _find_package_path(import_name)
    # 获取当前 Python 环境的前缀路径（如虚拟环境或全局安装路径），并将其转换为绝对路径。
    py_prefix = os.path.abspath(sys.prefix)

    # 函数检查 package_path 是否相对于 py_prefix。
    # installed to the system
    if _path_is_relative_to(pathlib.PurePath(package_path), py_prefix):
        # 返回该前缀和包路径。
        return py_prefix, package_path

    # 将包路径分为其父目录 site_parent 和当前目录 site_folder。
    site_parent, site_folder = os.path.split(package_path)

    # installed to a virtualenv
    # 如果当前目录为 site-packages（不区分大小写），表示包可能安装在虚拟环境中。
    if site_folder.lower() == "site-packages":
        # 将 site_parent 进一步分割为其父目录 parent 和当前目录 folder。
        parent, folder = os.path.split(site_parent)

        # 如果 folder 为 lib，表示包安装在 Windows 系统的标准目录结构中。
        # Windows (prefix/lib/site-packages)
        if folder.lower() == "lib":
            # 返回虚拟环境的父目录和包路径。
            return parent, package_path

        # 如果 parent 的基本名称为 lib，表示包安装在 Unix 系统的标准目录结构中。
        # Unix (prefix/lib/pythonX.Y/site-packages)
        if os.path.basename(parent).lower() == "lib":
            # 返回 parent 的上级目录和包路径。
            return os.path.dirname(parent), package_path

        # 如果以上条件都不满足，则返回 site_parent 和包路径，表示包安装在非标准位置。
        # something else (prefix/site-packages)
        return site_parent, package_path

    # 如果包没有安装到系统或虚拟环境中，返回 None 和包路径，表示包可能是从当前工作目录导入的。
    # not installed
    return None, package_path


