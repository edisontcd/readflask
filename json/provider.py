from __future__ import annotations

import dataclasses
import decimal
import json
import typing as t
import uuid
import weakref
from datetime import date

from werkzeug.http import http_date

if t.TYPE_CHECKING:  # pragma: no cover
    from werkzeug.sansio.response import Response

    from ..sansio.app import App

# 在 Flask 应用程序中提供标准的 JSON 操作，它可以用来序列化和反序列化 JSON 数据。
class JSONProvider:
    """A standard set of JSON operations for an application. Subclasses
    of this can be used to customize JSON behavior or use different
    JSON libraries.

    To implement a provider for a specific library, subclass this base
    class and implement at least :meth:`dumps` and :meth:`loads`. All
    other methods have default implementations.

    To use a different provider, either subclass ``Flask`` and set
    :attr:`~flask.Flask.json_provider_class` to a provider class, or set
    :attr:`app.json <flask.Flask.json>` to an instance of the class.

    :param app: An application instance. This will be stored as a
        :class:`weakref.proxy` on the :attr:`_app` attribute.

    .. versionadded:: 2.2
    """

    # 初始化时，app 参数是 Flask 应用的实例，并且将其保存为弱引用 self._app。
    # 这样可以避免循环引用。
    def __init__(self, app: App) -> None:
        self._app: App = weakref.proxy(app)

    # 这是一个抽象方法，要求子类必须实现，用于将数据对象序列化为 JSON 字符串。
    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
        """Serialize data as JSON.

        :param obj: The data to serialize.
        :param kwargs: May be passed to the underlying JSON library.
        """
        raise NotImplementedError

    # 将数据对象序列化为 JSON 并将其写入到文件中，具体是通过 dumps 方法来完成序列化。
    def dump(self, obj: t.Any, fp: t.IO[str], **kwargs: t.Any) -> None:
        """Serialize data as JSON and write to a file.

        :param obj: The data to serialize.
        :param fp: A file opened for writing text. Should use the UTF-8
            encoding to be valid JSON.
        :param kwargs: May be passed to the underlying JSON library.
        """
        # 它将调用 dumps 方法，并将其输出写入到传入的文件对象 fp 中。
        fp.write(self.dumps(obj, **kwargs))

    # 要求子类必须实现，用于从 JSON 字符串中反序列化数据。
    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any:
        """Deserialize data as JSON.

        :param s: Text or UTF-8 bytes.
        :param kwargs: May be passed to the underlying JSON library.
        """
        raise NotImplementedError

    # 用于从文件中读取 JSON 数据并反序列化。
    def load(self, fp: t.IO[t.AnyStr], **kwargs: t.Any) -> t.Any:
        """Deserialize data as JSON read from a file.

        :param fp: A file opened for reading text or UTF-8 bytes.
        :param kwargs: May be passed to the underlying JSON library.
        """
        # 通过读取文件的内容并调用 loads 方法来解析 JSON 数据。
        return self.loads(fp.read(), **kwargs)

    # 在 JSONProvider 类的 response 方法中，预处理传递给 response 方法的参数，
    # 确保参数的使用方式符合预期的规则。
    def _prepare_response_obj(
        self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
    ) -> t.Any:
        # 为了避免参数冲突，规定函数只能接受位置参数或者关键字参数中的一种，而不能同时传递两者。
        if args and kwargs:
            raise TypeError("app.json.response() takes either args or kwargs, not both")

        # 这种情况下，表示没有内容需要序列化为 JSON，可能是返回空响应。
        if not args and not kwargs:
            return None

        # 如果只传递了一个位置参数，则直接返回该参数（不需要再进行列表或字典包装）。
        # 这确保当只传递一个参数时，不会额外包装成列表。
        if len(args) == 1:
            return args[0]

        return args or kwargs

    # 负责将传入的参数序列化为 JSON，并返回一个带有 application/json MIME 类型的 Flask 响应对象。
    # 它的作用是生成一个 JSON 格式的 HTTP 响应。
    # 返回值是 Response 类型的对象，这是 Flask 框架用于返回 HTTP 响应的类。
    def response(self, *args: t.Any, **kwargs: t.Any) -> Response:
        """Serialize the given arguments as JSON, and return a
        :class:`~flask.Response` object with the ``application/json``
        mimetype.

        The :func:`~flask.json.jsonify` function calls this method for
        the current application.

        Either positional or keyword arguments can be given, not both.
        If no arguments are given, ``None`` is serialized.

        :param args: A single value to serialize, or multiple values to
            treat as a list to serialize.
        :param kwargs: Treat as a dict to serialize.
        """
        # 调用 _prepare_response_obj 方法来处理 args 和 kwargs。
        obj = self._prepare_response_obj(args, kwargs)
        # 调用 self.dumps(obj) 将 obj 序列化为 JSON 字符串。
        # dumps 方法负责将 Python 对象转换为 JSON 格式。
        # self._app.response_class 是一个工厂函数，生成一个带有指定 MIME 类型的 Response 对象。
        # 在这里，MIME 类型被设置为 application/json，表明响应内容是 JSON 格式。
        return self._app.response_class(self.dumps(obj), mimetype="application/json")

# 用于处理一些 Python 内建的、复杂的对象类型（例如日期、UUID、Decimal 类型等），
# 将一些默认无法直接序列化的复杂类型转换为可以序列化为 JSON 的格式。
# 它通常作为 json.dumps 的 default 参数使用，当 json.dumps 遇到无法直接序列化的对象时，
# default 参数会调用这个函数来进行转换。
# 这是一个泛型函数，接受任何类型的参数 o。返回值也是任意类型（t.Any），
# 因为函数的目的就是将复杂对象转换为可以序列化为 JSON 的简单类型。
def _default(o: t.Any) -> t.Any:
    # 如果对象 o 是 date 类型（包括 datetime.date 和 datetime.datetime），
    # 则调用 werkzeug.http.http_date 方法将其转换为符合 HTTP 标准的
    # 日期字符串格式（RFC 822 格式），比如 "Mon, 12 Sep 2022 12:00:00 GMT"。
    if isinstance(o, date):
        return http_date(o)

    # 如果对象是 decimal.Decimal 或 uuid.UUID 类型，将其转换为字符串。
    # 这些类型在 JSON 中没有直接的对应类型，因此需要转换为字符串形式。
    if isinstance(o, (decimal.Decimal, uuid.UUID)):
        return str(o)

    # 如果 o 是一个数据类（dataclass），则使用 dataclasses.asdict 方法将其转换为字典。
    # dataclasses 是 Python 3.7 引入的一种类装饰器，允许轻松定义数据对象。
    if dataclasses and dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)  # type: ignore[call-overload]

    # 如果对象 o 有 __html__ 方法（通常用于生成 HTML 的对象，如 markupsafe.Markup），
    # 调用 __html__ 方法并将其返回值转换为字符串。
    if hasattr(o, "__html__"):
        return str(o.__html__())

    # 如果对象 o 不是上面列出的类型，函数会抛出 TypeError 异常，提示该对象无法序列化为 JSON。
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


# 继承了 JSONProvider，用于处理 Flask 应用中的 JSON 序列化与反序列化操作。
class DefaultJSONProvider(JSONProvider):
    """Provide JSON operations using Python's built-in :mod:`json`
    library. Serializes the following additional data types:

    -   :class:`datetime.datetime` and :class:`datetime.date` are
        serialized to :rfc:`822` strings. This is the same as the HTTP
        date format.
    -   :class:`uuid.UUID` is serialized to a string.
    -   :class:`dataclasses.dataclass` is passed to
        :func:`dataclasses.asdict`.
    -   :class:`~markupsafe.Markup` (or any object with a ``__html__``
        method) will call the ``__html__`` method to get a string.
    """

    # 静态方法，作为 json.dumps 的 default 参数使用。
    # _default 函数的作用是在遇到无法直接序列化的数据类型时，提供如何处理这些类型的逻辑。
    default: t.Callable[[t.Any], t.Any] = staticmethod(_default)  # type: ignore[assignment]
    """Apply this function to any object that :meth:`json.dumps` does
    not know how to serialize. It should return a valid JSON type or
    raise a ``TypeError``.
    """

    # 用于控制是否在 JSON 序列化时将非 ASCII 字符替换为 Unicode 转义字符。
    # 默认值为 True，会将非 ASCII 字符转义。可以设置为 False 以保持原始字符，
    # 减少输出体积，提高性能。
    ensure_ascii = True
    """Replace non-ASCII characters with escape sequences. This may be
    more compatible with some clients, but can be disabled for better
    performance and size.
    """

    # 这个属性用于控制是否在 JSON 序列化时对字典的键进行排序。
    # 启用此选项时，字典中的键必须都是字符串。排序对某些缓存场景有用，但会影响性能。
    sort_keys = True
    """Sort the keys in any serialized dicts. This may be useful for
    some caching situations, but can be disabled for better performance.
    When enabled, keys must all be strings, they are not converted
    before sorting.
    """

    # 控制输出是否为紧凑格式。如果 compact 设置为 True，输出不会有额外的缩进、换行或空格；
    # 如果为 False 或在调试模式下，它将以易读的格式输出。默认为 None，根据调试模式决定格式。
    compact: bool | None = None
    """If ``True``, or ``None`` out of debug mode, the :meth:`response`
    output will not add indentation, newlines, or spaces. If ``False``,
    or ``None`` in debug mode, it will use a non-compact representation.
    """

    # 定义返回响应的默认 MIME 类型，表示生成的响应内容为 application/json。
    mimetype = "application/json"
    """The mimetype set in :meth:`response`."""

    # 该方法使用 Python 的 json.dumps 函数将 Python 对象序列化为 JSON 字符串。
    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
        """Serialize data as JSON to a string.

        Keyword arguments are passed to :func:`json.dumps`. Sets some
        parameter defaults from the :attr:`default`,
        :attr:`ensure_ascii`, and :attr:`sort_keys` attributes.

        :param obj: The data to serialize.
        :param kwargs: Passed to :func:`json.dumps`.
        """
        # 设置了一些默认的参数。
        kwargs.setdefault("default", self.default)
        kwargs.setdefault("ensure_ascii", self.ensure_ascii)
        kwargs.setdefault("sort_keys", self.sort_keys)
        return json.dumps(obj, **kwargs)

    # 该方法用于将 JSON 字符串或字节反序列化为 Python 对象。它调用了标准库的 json.loads。
    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any:
        """Deserialize data as JSON from a string or bytes.

        :param s: Text or UTF-8 bytes.
        :param kwargs: Passed to :func:`json.loads`.
        """
        return json.loads(s, **kwargs)

    # 该方法是 Flask 中 jsonify 的核心逻辑，它将对象序列化为 JSON，
    # 并返回一个 Flask Response 对象，设置 MIME 类型为 application/json。
    def response(self, *args: t.Any, **kwargs: t.Any) -> Response:
        """Serialize the given arguments as JSON, and return a
        :class:`~flask.Response` object with it. The response mimetype
        will be "application/json" and can be changed with
        :attr:`mimetype`.

        If :attr:`compact` is ``False`` or debug mode is enabled, the
        output will be formatted to be easier to read.

        Either positional or keyword arguments can be given, not both.
        If no arguments are given, ``None`` is serialized.

        :param args: A single value to serialize, or multiple values to
            treat as a list to serialize.
        :param kwargs: Treat as a dict to serialize.
        """
        # 根据传入的参数准备好需要序列化为 JSON 的对象，确保 args 和 kwargs 中只能传递一种形式。
        obj = self._prepare_response_obj(args, kwargs)
        # 初始化一个空字典 dump_args，用于存储 JSON 序列化时的参数，比如缩进或分隔符等。
        dump_args: dict[str, t.Any] = {}

        # 如果 compact 是 None 并且应用处于调试模式，或者 compact 显式设置为 False，
        # 则使用缩进 (indent=2)，这样生成的 JSON 更容易阅读。
        if (self.compact is None and self._app.debug) or self.compact is False:
            dump_args.setdefault("indent", 2)
        else:
            # 使用紧凑的格式，定义分隔符为 , 和 :，不会有额外的空格和换行。
            dump_args.setdefault("separators", (",", ":"))

        # 调用 Flask 应用的 response_class 来创建响应对象。
        # 使用 self.dumps 将 obj 序列化为 JSON 字符串，传入 dump_args 中的参数来控制格式。
        # 在 JSON 字符串末尾添加一个换行符 \n，这在调试模式下有助于更清晰的输出。
        # 返回的响应对象的 mimetype 被设置为 application/json（默认值，可以通过子类化进行修改）。
        return self._app.response_class(
            f"{self.dumps(obj, **dump_args)}\n", mimetype=self.mimetype
        )


