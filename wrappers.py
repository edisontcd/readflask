from __future__ import annotations

import typing as t

# BadRequest：表示客户端错误（HTTP 400 错误），通常用于请求无效的情况。
from werkzeug.exceptions import BadRequest
# HTTPException：Werkzeug 中的所有 HTTP 异常的基类。
from werkzeug.exceptions import HTTPException
# RequestBase：表示 HTTP 请求对象的基类。
from werkzeug.wrappers import Request as RequestBase
# ResponseBase：表示 HTTP 响应对象的基类。
from werkzeug.wrappers import Response as ResponseBase

from . import json
from .globals import current_app
from .helpers import _split_blueprint_path

# 在运行时不会执行内部代码块，只有在类型检查（如使用 mypy 或 IDE 类型检查）时才会执行。
# 这可以防止在实际运行时导入不必要的模块，减少开销。
if t.TYPE_CHECKING:  # pragma: no cover 告诉代码覆盖率工具忽略这一行，这通常用于避免不必要的覆盖报告。
    from werkzeug.routing import Rule

# 用于处理 HTTP 请求的核心类之一。
# Request 类继承自 werkzeug.wrappers.Request，并扩展了其功能以支持 Flask 特定的功能和属性。
class Request(RequestBase):
    """The request object used by default in Flask.  Remembers the
    matched endpoint and view arguments.

    It is what ends up as :class:`~flask.request`.  If you want to replace
    the request object used you can subclass this and set
    :attr:`~flask.Flask.request_class` to your subclass.

    The request object is a :class:`~werkzeug.wrappers.Request` subclass and
    provides all of the attributes Werkzeug defines plus a few Flask
    specific ones.
    """

    # 定义了一个 json_module 属性，默认设置为 Flask 内置的 json 模块。
    # 这允许开发者在处理请求时使用 Flask 特定的 JSON 序列化和反序列化方法。
    # json_module 变量使用了类型注解，json_module 被注解为 t.Any 类型。
    # 这意味着 json_module 可以是任意类型。t.Any 是 typing 模块中的一个特殊类型，
    # 表示此变量可以是任何类型的值。
    json_module: t.Any = json

    #: The internal URL rule that matched the request.  This can be
    #: useful to inspect which methods are allowed for the URL from
    #: a before/after handler (``request.url_rule.methods``) etc.
    #: Though if the request's method was invalid for the URL rule,
    #: the valid list is available in ``routing_exception.valid_methods``
    #: instead (an attribute of the Werkzeug exception
    #: :exc:`~werkzeug.exceptions.MethodNotAllowed`)
    #: because the request was never internally bound.
    #:
    #: .. versionadded:: 0.6
    # url_rule 属性保存了匹配请求的内部 URL 规则。它可以在请求处理中访问，
    # 例如在 before_request 或 after_request 处理器中查看匹配的 URL 规则和允许的方法。
    url_rule: Rule | None = None

    # view_args 是一个字典，包含了从 URL 中提取的视图参数。如果在 URL 匹配过程中发生异常，该属性将为 None。
    #: A dict of view arguments that matched the request.  If an exception
    #: happened when matching, this will be ``None``.
    view_args: dict[str, t.Any] | None = None

    #: If matching the URL failed, this is the exception that will be
    #: raised / was raised as part of the request handling.  This is
    #: usually a :exc:`~werkzeug.exceptions.NotFound` exception or
    #: something similar.
    # 如果在 URL 匹配过程中发生异常（如 404 Not Found），该属性会保存此异常。
    # 它可以用于在请求处理期间进行异常处理。
    routing_exception: HTTPException | None = None

    # 这是一个只读属性，返回 Flask 应用配置中设置的 MAX_CONTENT_LENGTH，
    # 表示请求体的最大长度。如果未设置，则返回 None。
    @property
    def max_content_length(self) -> int | None:  # type: ignore[override]
        """Read-only view of the ``MAX_CONTENT_LENGTH`` config key."""
        if current_app:
            return current_app.config["MAX_CONTENT_LENGTH"]  # type: ignore[no-any-return]
        else:
            return None

    # 返回与请求 URL 匹配的端点名称（通常是视图函数的名称）。
    # 如果 URL 匹配失败或未执行匹配，则返回 None。
    @property
    def endpoint(self) -> str | None:
        """The endpoint that matched the request URL.

        This will be ``None`` if matching failed or has not been
        performed yet.

        This in combination with :attr:`view_args` can be used to
        reconstruct the same URL or a modified URL.
        """
        if self.url_rule is not None:
            return self.url_rule.endpoint  # type: ignore[no-any-return]

        return None

    # 返回当前请求所属的蓝图（Blueprint）名称。
    # 如果请求未匹配到蓝图或 URL 匹配失败，则返回 None。
    @property
    def blueprint(self) -> str | None:
        """The registered name of the current blueprint.

        This will be ``None`` if the endpoint is not part of a
        blueprint, or if URL matching failed or has not been performed
        yet.

        This does not necessarily match the name the blueprint was
        created with. It may have been nested, or registered with a
        different name.
        """
        endpoint = self.endpoint

        if endpoint is not None and "." in endpoint:
            return endpoint.rpartition(".")[0]

        return None

    # 返回当前蓝图以及其父蓝图的名称列表。如果没有蓝图，则返回一个空列表。
    @property
    def blueprints(self) -> list[str]:
        """The registered names of the current blueprint upwards through
        parent blueprints.

        This will be an empty list if there is no current blueprint, or
        if URL matching failed.

        .. versionadded:: 2.0.1
        """
        name = self.blueprint

        if name is None:
            return []

        return _split_blueprint_path(name)

    # 重载了父类的 _load_form_data 方法。在 Flask 的调试模式下，如果请求的 MIME 类型不是
    # multipart/form-data 且请求没有文件上传，则为 request.files 创建一个特殊的字典类，
    # 用于在开发者忘记设置 enctype 属性时提供更有用的错误信息。
    def _load_form_data(self) -> None:
        super()._load_form_data()

        # In debug mode we're replacing the files multidict with an ad-hoc
        # subclass that raises a different error for key errors.
        if (
            current_app
            and current_app.debug
            and self.mimetype != "multipart/form-data"
            and not self.files
        ):
            from .debughelpers import attach_enctype_error_multidict

            attach_enctype_error_multidict(self)

    # 重载了处理 JSON 解析错误的方法。如果解析失败且 Flask 处于调试模式，
    # 重新引发异常以便调试。如果不是调试模式，则抛出一个通用的 BadRequest 异常。
    def on_json_loading_failed(self, e: ValueError | None) -> t.Any:
        try:
            return super().on_json_loading_failed(e)
        except BadRequest as e:
            if current_app and current_app.debug:
                raise

            raise BadRequest() from e


# 用于处理 HTTP 响应的核心类之一。
# Response 类继承自 ResponseBase（werkzeug.wrappers.Response），
# 并扩展了它的功能以支持 Flask 的特性。
class Response(ResponseBase):
    """The response object that is used by default in Flask.  Works like the
    response object from Werkzeug but is set to have an HTML mimetype by
    default.  Quite often you don't have to create this object yourself because
    :meth:`~flask.Flask.make_response` will take care of that for you.

    If you want to replace the response object used you can subclass this and
    set :attr:`~flask.Flask.response_class` to your subclass.

    .. versionchanged:: 1.0
        JSON support is added to the response, like the request. This is useful
        when testing to get the test client response data as JSON.

    .. versionchanged:: 1.0

        Added :attr:`max_cookie_size`.
    """

    # 定义了响应对象的默认 MIME 类型。
    default_mimetype: str | None = "text/html"

    # 指定了用于处理 JSON 数据的模块。默认情况下，它使用 Flask 的内部 json 模块。
    # 这个模块负责将 Python 对象序列化为 JSON 格式的字符串，
    # 并将 JSON 字符串反序列化为 Python 对象。
    json_module = json

    # 用于控制是否自动修正 Location 头部字段。浏览器要求 Location 头部字段是一个完整的 URL，
    # 而不是相对路径。如果设置为 True，Flask 会自动修正这个头部字段以满足这种要求。
    autocorrect_location_header = False

    # 只读属性，返回 Flask 应用配置中的 MAX_COOKIE_SIZE 配置项，
    # 表示可以设置的最大 Cookie 大小。
    @property
    def max_cookie_size(self) -> int:  # type: ignore
        """Read-only view of the :data:`MAX_COOKIE_SIZE` config key.

        See :attr:`~werkzeug.wrappers.Response.max_cookie_size` in
        Werkzeug's docs.
        """
        if current_app:
            return current_app.config["MAX_COOKIE_SIZE"]  # type: ignore[no-any-return]

        # return Werkzeug's default when not in an app context
        return super().max_cookie_size



