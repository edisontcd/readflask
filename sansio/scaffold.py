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

































