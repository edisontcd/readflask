from __future__ import annotations

import json as _json
import typing as t

from ..globals import current_app
from .provider import _default

if t.TYPE_CHECKING:  # pragma: no cover
    from ..wrappers import Response


# 将 Python 对象序列化为 JSON 字符串。
def dumps(obj: t.Any, **kwargs: t.Any) -> str:
    """Serialize data as JSON.

    If :data:`~flask.current_app` is available, it will use its
    :meth:`app.json.dumps() <flask.json.provider.JSONProvider.dumps>`
    method, otherwise it will use :func:`json.dumps`.

    :param obj: The data to serialize.
    :param kwargs: Arguments passed to the ``dumps`` implementation.

    .. versionchanged:: 2.3
        The ``app`` parameter was removed.

    .. versionchanged:: 2.2
        Calls ``current_app.json.dumps``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.0.2
        :class:`decimal.Decimal` is supported by converting to a string.

    .. versionchanged:: 2.0
        ``encoding`` will be removed in Flask 2.1.

    .. versionchanged:: 1.0.3
        ``app`` can be passed directly, rather than requiring an app
        context for configuration.
    """
    # 如果有活跃的 Flask 应用上下文（current_app），调用应用中自定义的 dumps 方法。
    if current_app:
        return current_app.json.dumps(obj, **kwargs)

    # 否则使用标准库中的 json.dumps，并将 _default 函数作为默认的序列化函数。
    kwargs.setdefault("default", _default)
    return _json.dumps(obj, **kwargs)


# 将 Python 对象序列化为 JSON 并写入到文件。
def dump(obj: t.Any, fp: t.IO[str], **kwargs: t.Any) -> None:
    """Serialize data as JSON and write to a file.

    If :data:`~flask.current_app` is available, it will use its
    :meth:`app.json.dump() <flask.json.provider.JSONProvider.dump>`
    method, otherwise it will use :func:`json.dump`.

    :param obj: The data to serialize.
    :param fp: A file opened for writing text. Should use the UTF-8
        encoding to be valid JSON.
    :param kwargs: Arguments passed to the ``dump`` implementation.

    .. versionchanged:: 2.3
        The ``app`` parameter was removed.

    .. versionchanged:: 2.2
        Calls ``current_app.json.dump``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.0
        Writing to a binary file, and the ``encoding`` argument, will be
        removed in Flask 2.1.
    """
    # 如果有活跃的 Flask 应用上下文，使用应用中自定义的 dump 方法。
    if current_app:
        current_app.json.dump(obj, fp, **kwargs)
    else:
        # 否则调用标准库中的 json.dump。
        kwargs.setdefault("default", _default)
        _json.dump(obj, fp, **kwargs)


# 将 JSON 字符串反序列化为 Python 对象。
def loads(s: str | bytes, **kwargs: t.Any) -> t.Any:
    """Deserialize data as JSON.

    If :data:`~flask.current_app` is available, it will use its
    :meth:`app.json.loads() <flask.json.provider.JSONProvider.loads>`
    method, otherwise it will use :func:`json.loads`.

    :param s: Text or UTF-8 bytes.
    :param kwargs: Arguments passed to the ``loads`` implementation.

    .. versionchanged:: 2.3
        The ``app`` parameter was removed.

    .. versionchanged:: 2.2
        Calls ``current_app.json.loads``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.0
        ``encoding`` will be removed in Flask 2.1. The data must be a
        string or UTF-8 bytes.

    .. versionchanged:: 1.0.3
        ``app`` can be passed directly, rather than requiring an app
        context for configuration.
    """
    # 如果有活跃的 Flask 应用上下文，使用应用中自定义的 loads 方法。
    if current_app:
        return current_app.json.loads(s, **kwargs)

    # 否则使用标准库中的 json.loads。
    return _json.loads(s, **kwargs)


# 将文件中的 JSON 数据反序列化为 Python 对象。
def load(fp: t.IO[t.AnyStr], **kwargs: t.Any) -> t.Any:
    """Deserialize data as JSON read from a file.

    If :data:`~flask.current_app` is available, it will use its
    :meth:`app.json.load() <flask.json.provider.JSONProvider.load>`
    method, otherwise it will use :func:`json.load`.

    :param fp: A file opened for reading text or UTF-8 bytes.
    :param kwargs: Arguments passed to the ``load`` implementation.

    .. versionchanged:: 2.3
        The ``app`` parameter was removed.

    .. versionchanged:: 2.2
        Calls ``current_app.json.load``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.2
        The ``app`` parameter will be removed in Flask 2.3.

    .. versionchanged:: 2.0
        ``encoding`` will be removed in Flask 2.1. The file must be text
        mode, or binary mode with UTF-8 bytes.
    """
    # 如果有活跃的 Flask 应用上下文，使用应用中自定义的 load 方法。
    if current_app:
        return current_app.json.load(fp, **kwargs)

    # 否则使用标准库中的 json.load。
    return _json.load(fp, **kwargs)

# 将给定的参数序列化为 JSON 并返回一个 Response 对象，MIME 类型设置为 application/json。
def jsonify(*args: t.Any, **kwargs: t.Any) -> Response:
    """Serialize the given arguments as JSON, and return a
    :class:`~flask.Response` object with the ``application/json``
    mimetype. A dict or list returned from a view will be converted to a
    JSON response automatically without needing to call this.

    This requires an active request or application context, and calls
    :meth:`app.json.response() <flask.json.provider.JSONProvider.response>`.

    In debug mode, the output is formatted with indentation to make it
    easier to read. This may also be controlled by the provider.

    Either positional or keyword arguments can be given, not both.
    If no arguments are given, ``None`` is serialized.

    :param args: A single value to serialize, or multiple values to
        treat as a list to serialize.
    :param kwargs: Treat as a dict to serialize.

    .. versionchanged:: 2.2
        Calls ``current_app.json.response``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.0.2
        :class:`decimal.Decimal` is supported by converting to a string.

    .. versionchanged:: 0.11
        Added support for serializing top-level arrays. This was a
        security risk in ancient browsers. See :ref:`security-json`.

    .. versionadded:: 0.2
    """
    # 调用 current_app.json.response 来创建 JSON 响应对象。
    # jsonify 通常用来快速创建返回 JSON 的 API 响应。
    return current_app.json.response(*args, **kwargs)  # type: ignore[return-value]


