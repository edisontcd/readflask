from __future__ import annotations

# typing模块是Python标准库的一部分，主要用于提供类型提示（type hinting）和静态类型检查。
import typing as t

# 只在类型检查时执行，不会在运行时执行。这用于避免不必要的导入，以减少运行时开销。
if t.TYPE_CHECKING:  # pragma: no cover
    from _typeshed.wsgi import WSGIApplication  # noqa: F401
    from werkzeug.datastructures import Headers  # noqa: F401
    from werkzeug.sansio.response import Response  # noqa: F401

# 定义了可能的 HTTP 响应值类型，包括 Response 对象、字符串、字节序列、列表、映射和迭代器。
# The possible types that are directly convertible or are a Response object.
ResponseValue = t.Union[
    "Response",
    str,
    bytes,
    t.List[t.Any],
    # Only dict is actually accepted, but Mapping allows for TypedDict.
    t.Mapping[str, t.Any],
    t.Iterator[str],
    t.Iterator[bytes],
]

# 定义了单个 HTTP 头的可能类型，包括字符串、字符串列表或字符串元组。
# the possible types for an individual HTTP header
# This should be a Union, but mypy doesn't pass unless it's a TypeVar.
HeaderValue = t.Union[str, t.List[str], t.Tuple[str, ...]]

# 定义了可能的HTTP头集合的类型，可能是Headers对象、映射或元组序列。
# the possible types for HTTP headers
HeadersValue = t.Union[
    "Headers",
    t.Mapping[str, HeaderValue],
    t.Sequence[t.Tuple[str, HeaderValue]],
]

# 定义了Flask路由函数可能返回的类型，包括各种响应值、状态码和头信息的组合，
# 以及 WSGIApplication 对象。
# The possible types returned by a route function.
ResponseReturnValue = t.Union[
    ResponseValue,
    t.Tuple[ResponseValue, HeadersValue],
    t.Tuple[ResponseValue, int],
    t.Tuple[ResponseValue, int, HeadersValue],
    "WSGIApplication",
]

# 定义了一个类型变量 ResponseClass，用于表示 Response 或其子类。
# 这允许我们在使用回调函数时，保留对特定 Response 子类的类型信息。
# Allow any subclass of werkzeug.Response, such as the one from Flask,
# as a callback argument. Using werkzeug.Response directly makes a
# callback annotated with flask.Response fail type checking.
ResponseClass = t.TypeVar("ResponseClass", bound="Response")

# 定义了应用或蓝图的键的类型，可以是字符串或 None。
AppOrBlueprintKey = t.Optional[str]  # The App key is None, whereas blueprints are named

# 定义了在 Flask 中常见的各种回调函数的类型。它们可以同步或异步，并接受特定的参数和返回值类型。
AfterRequestCallable = t.Union[
    t.Callable[[ResponseClass], ResponseClass],
    t.Callable[[ResponseClass], t.Awaitable[ResponseClass]],
]
BeforeFirstRequestCallable = t.Union[
    t.Callable[[], None], t.Callable[[], t.Awaitable[None]]
]
BeforeRequestCallable = t.Union[
    t.Callable[[], t.Optional[ResponseReturnValue]],
    t.Callable[[], t.Awaitable[t.Optional[ResponseReturnValue]]],
]
ShellContextProcessorCallable = t.Callable[[], t.Dict[str, t.Any]]
TeardownCallable = t.Union[
    t.Callable[[t.Optional[BaseException]], None],
    t.Callable[[t.Optional[BaseException]], t.Awaitable[None]],
]
TemplateContextProcessorCallable = t.Union[
    t.Callable[[], t.Dict[str, t.Any]],
    t.Callable[[], t.Awaitable[t.Dict[str, t.Any]]],
]
TemplateFilterCallable = t.Callable[..., t.Any]
TemplateGlobalCallable = t.Callable[..., t.Any]
TemplateTestCallable = t.Callable[..., bool]
URLDefaultCallable = t.Callable[[str, t.Dict[str, t.Any]], None]
URLValuePreprocessorCallable = t.Callable[
    [t.Optional[str], t.Optional[t.Dict[str, t.Any]]], None
]

# ErrorHandlerCallable 定义了处理错误的回调函数类型，
# RouteCallable 定义了 Flask 路由的回调函数类型。
# 这两者都可以是同步函数或异步函数，返回值必须是有效的 HTTP 响应值类型。
# This should take Exception, but that either breaks typing the argument
# with a specific exception, or decorating multiple times with different
# exceptions (and using a union type on the argument).
# https://github.com/pallets/flask/issues/4095
# https://github.com/pallets/flask/issues/4295
# https://github.com/pallets/flask/issues/4297
ErrorHandlerCallable = t.Union[
    t.Callable[[t.Any], ResponseReturnValue],
    t.Callable[[t.Any], t.Awaitable[ResponseReturnValue]],
]

RouteCallable = t.Union[
    t.Callable[..., ResponseReturnValue],
    t.Callable[..., t.Awaitable[ResponseReturnValue]],
]