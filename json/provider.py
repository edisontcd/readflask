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





