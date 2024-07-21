from __future__ import annotations

# 用于安全哈希和消息摘要。
import hashlib
# 提供类型注解支持。
import typing as t
# 用于定义支持可变映射的类。
from collections.abc import MutableMapping
# datetime 和 timezone用于日期和时间处理。
from datetime import datetime
from datetime import timezone

# 用于表示无效签名错误。
from itsdangerous import BadSignature
# 用于创建和验证带有时间戳的签名，以确保会话数据的完整性和安全性。
from itsdangerous import URLSafeTimedSerializer
# 一种特殊的字典，当字典内容更改时可以触发回调函数。
from werkzeug.datastructures import CallbackDict

# 导入 JSON 序列化器 TaggedJSONSerializer，用于处理 JSON 数据的序列化和反序列化。
from .json.tag import TaggedJSONSerializer

# if t.TYPE_CHECKING 块中的代码不会在运行时执行，这有助于避免运行时导入错误，同时提供类型注解支持。
if t.TYPE_CHECKING:  # pragma: no cover
    import typing_extensions as te

    from .app import Flask
    from .wrappers import Request
    from .wrappers import Response


# 扩展了基本字典功能，添加了几个与会话管理相关的属性。
# 可以轻松创建自定义的会话对象，具有更丰富的会话状态管理功能。
# TODO generic when Python > 3.8
class SessionMixin(MutableMapping):  # type: ignore[type-arg]
    """Expands a basic dictionary with session attributes."""

    # 
    @property
    def permanent(self) -> bool:
        """This reflects the ``'_permanent'`` key in the dict."""
        return self.get("_permanent", False)

    @permanent.setter
    def permanent(self, value: bool) -> None:
        # 返回字典中 _permanent 键的值，如果不存在则返回 False。
        self["_permanent"] = bool(value)

    #: Some implementations can detect whether a session is newly
    #: created, but that is not guaranteed. Use with caution. The mixin
    # default is hard-coded ``False``.
    # 这个属性表示会话是否是新创建的,默认值硬编码为 False。
    new = False

    #: Some implementations can detect changes to the session and set
    #: this when that happens. The mixin default is hard coded to
    #: ``True``.
    # 这个属性表示会话是否被修改。
    modified = True

    #: Some implementations can detect when session data is read or
    #: written and set this when that happens. The mixin default is hard
    #: coded to ``True``.
    # 这个属性表示会话数据是否被读取或写入。
    accessed = True


# TODO generic when Python > 3.8
# SecureCookieSession 类扩展了 CallbackDict 和 SessionMixin，
# 用于基于签名 Cookie 的会话管理。
# 它添加了 modified 和 accessed 属性，跟踪会话数据的修改和访问情况。
# 通过这种方式，可以更方便地管理会话数据，并确保会话数据在被修改或访问时的状态。
class SecureCookieSession(CallbackDict, SessionMixin):  # type: ignore[type-arg]
    """Base class for sessions based on signed cookies.

    This session backend will set the :attr:`modified` and
    :attr:`accessed` attributes. It cannot reliably track whether a
    session is new (vs. empty), so :attr:`new` remains hard coded to
    ``False``.
    """

    #: When data is changed, this is set to ``True``. Only the session
    #: dictionary itself is tracked; if the session contains mutable
    #: data (for example a nested dict) then this must be set to
    #: ``True`` manually when modifying that data. The session cookie
    #: will only be written to the response if this is ``True``.
    modified = False

    #: When data is read or written, this is set to ``True``. Used by
    # :class:`.SecureCookieSessionInterface` to add a ``Vary: Cookie``
    #: header, which allows caching proxies to cache different pages for
    #: different users.
    accessed = False

    # 初始化 SecureCookieSession 实例。
    def __init__(self, initial: t.Any = None) -> None:
        # on_update 回调函数：当会话数据被修改时调用，设置 modified 和 accessed 属性为 True。
        def on_update(self: te.Self) -> None:
            self.modified = True
            self.accessed = True

        # 调用父类的 __init__ 方法，将 initial 和 on_update 传递给 CallbackDict。
        super().__init__(initial, on_update)

    # 获取会话数据中的指定键值，并将 accessed 属性设置为 True。
    def __getitem__(self, key: str) -> t.Any:
        self.accessed = True
        return super().__getitem__(key)

    # 获取会话数据中的指定键值，如果键不存在，则返回默认值，并将 accessed 属性设置为 True。
    def get(self, key: str, default: t.Any = None) -> t.Any:
        self.accessed = True
        return super().get(key, default)

    # 如果键不存在，则将其设置为默认值，并返回键值，同时将 accessed 属性设置为 True。
    def setdefault(self, key: str, default: t.Any = None) -> t.Any:
        self.accessed = True
        return super().setdefault(key, default)


# 用于在会话不可用时生成详细的错误消息，指导用户设置 secret_key。
# 它继承自 SecureCookieSession，允许只读访问空会话，但在尝试设置会话数据时会失败，
# 并抛出 RuntimeError。
class NullSession(SecureCookieSession):
    """Class used to generate nicer error messages if sessions are not
    available.  Will still allow read-only access to the empty session
    but fail on setting.
    """

    # 这是一个私有方法，用于在会话不可用时生成错误消息。
    # 接受任意数量的位置参数和关键字参数，但不使用它们。
    # t.NoReturn表示这个方法不会返回任何值，因为它总是抛出异常。
    def _fail(self, *args: t.Any, **kwargs: t.Any) -> t.NoReturn:
        # 抛出一个 RuntimeError，并提供详细的错误消息，提示用户需要设置应用的 secret_key。
        raise RuntimeError(
            "The session is unavailable because no secret "
            "key was set.  Set the secret_key on the "
            "application to something unique and secret."
        )

    # 将以下字典方法指向 _fail 方法，这意味着当尝试调用这些方法时，将触发 _fail 方法并抛出 RuntimeError。
    __setitem__ = __delitem__ = clear = pop = popitem = update = setdefault = _fail  # type: ignore # noqa: B950
    # 删除 _fail 方法。
    del _fail


# SessionInterface 类定义了一个接口，用于替换默认的会话接口。
# 默认的会话接口使用了 werkzeug 的 securecookie 实现。
# 通过实现 open_session 和 save_session 方法，可以自定义会话管理机制。
# 其他方法提供了有用的默认实现，可以根据需要进行重载。
class SessionInterface:
    """The basic interface you have to implement in order to replace the
    default session interface which uses werkzeug's securecookie
    implementation.  The only methods you have to implement are
    :meth:`open_session` and :meth:`save_session`, the others have
    useful defaults which you don't need to change.

    The session object returned by the :meth:`open_session` method has to
    provide a dictionary like interface plus the properties and methods
    from the :class:`SessionMixin`.  We recommend just subclassing a dict
    and adding that mixin::

        class Session(dict, SessionMixin):
            pass

    If :meth:`open_session` returns ``None`` Flask will call into
    :meth:`make_null_session` to create a session that acts as replacement
    if the session support cannot work because some requirement is not
    fulfilled.  The default :class:`NullSession` class that is created
    will complain that the secret key was not set.

    To replace the session interface on an application all you have to do
    is to assign :attr:`flask.Flask.session_interface`::

        app = Flask(__name__)
        app.session_interface = MySessionInterface()

    Multiple requests with the same session may be sent and handled
    concurrently. When implementing a new session interface, consider
    whether reads or writes to the backing store must be synchronized.
    There is no guarantee on the order in which the session for each
    request is opened or saved, it will occur in the order that requests
    begin and end processing.

    .. versionadded:: 0.8
    """

    #: :meth:`make_null_session` will look here for the class that should
    #: be created when a null session is requested.  Likewise the
    #: :meth:`is_null_session` method will perform a typecheck against
    #: this type.
    # 指向 NullSession 类，当需要创建一个空会话时，会使用这个类。
    null_session_class = NullSession

    #: A flag that indicates if the session interface is pickle based.
    #: This can be used by Flask extensions to make a decision in regards
    #: to how to deal with the session object.
    #:
    #: .. versionadded:: 0.10
    # 指示会话接口是否基于 pickle。
    pickle_based = False

    # 创建一个空会话对象，通常用于会话支持因配置错误而无法正常工作时。
    def make_null_session(self, app: Flask) -> NullSession:
        """Creates a null session which acts as a replacement object if the
        real session support could not be loaded due to a configuration
        error.  This mainly aids the user experience because the job of the
        null session is to still support lookup without complaining but
        modifications are answered with a helpful error message of what
        failed.

        This creates an instance of :attr:`null_session_class` by default.
        """
        # 返回一个 NullSession 实例。
        return self.null_session_class()

    # 检查给定对象是否是一个空会话对象。
    # obj，类型为 object，表示要检查的对象。
    # 如果对象是 NullSession 实例，则返回 True，否则返回 False。
    def is_null_session(self, obj: object) -> bool:
        """Checks if a given object is a null session.  Null sessions are
        not asked to be saved.

        This checks if the object is an instance of :attr:`null_session_class`
        by default.
        """
        return isinstance(obj, self.null_session_class)

    # 返回会话 cookie 的名称。
    # 参数：app，类型为 Flask，表示当前的 Flask 应用实例。
    def get_cookie_name(self, app: Flask) -> str:
        """The name of the session cookie. Uses``app.config["SESSION_COOKIE_NAME"]``."""
        # 返回值：会话 cookie 的名称。
        return app.config["SESSION_COOKIE_NAME"]  # type: ignore[no-any-return]

    # 返回会话 cookie 的域。
    def get_cookie_domain(self, app: Flask) -> str | None:
        """The value of the ``Domain`` parameter on the session cookie. If not set,
        browsers will only send the cookie to the exact domain it was set from.
        Otherwise, they will send it to any subdomain of the given value as well.

        Uses the :data:`SESSION_COOKIE_DOMAIN` config.

        .. versionchanged:: 2.3
            Not set by default, does not fall back to ``SERVER_NAME``.
        """
        # 返回值：会话 cookie 的域。
        return app.config["SESSION_COOKIE_DOMAIN"]  # type: ignore[no-any-return]

    # 返回会话 cookie 的路径。
    def get_cookie_path(self, app: Flask) -> str:
        """Returns the path for which the cookie should be valid.  The
        default implementation uses the value from the ``SESSION_COOKIE_PATH``
        config var if it's set, and falls back to ``APPLICATION_ROOT`` or
        uses ``/`` if it's ``None``.
        """
        # 返回值：会话 cookie 的路径。
        return app.config["SESSION_COOKIE_PATH"] or app.config["APPLICATION_ROOT"]  # type: ignore[no-any-return]

    # 返回会话 cookie 是否应该是 httponly 的。
    def get_cookie_httponly(self, app: Flask) -> bool:
        """Returns True if the session cookie should be httponly.  This
        currently just returns the value of the ``SESSION_COOKIE_HTTPONLY``
        config var.
        """
        # 返回值：布尔值，指示会话 cookie 是否应该是 httponly 的。
        return app.config["SESSION_COOKIE_HTTPONLY"]  # type: ignore[no-any-return]

    # 返回会话 cookie 是否应该是安全的（仅通过 HTTPS 发送）。
    def get_cookie_secure(self, app: Flask) -> bool:
        """Returns True if the cookie should be secure.  This currently
        just returns the value of the ``SESSION_COOKIE_SECURE`` setting.
        """
        # 返回值：布尔值，指示会话 cookie 是否应该是安全的。
        return app.config["SESSION_COOKIE_SECURE"]  # type: ignore[no-any-return]

    # 返回会话 cookie 的 SameSite 属性。
    def get_cookie_samesite(self, app: Flask) -> str | None:
        """Return ``'Strict'`` or ``'Lax'`` if the cookie should use the
        ``SameSite`` attribute. This currently just returns the value of
        the :data:`SESSION_COOKIE_SAMESITE` setting.
        """
        # SameSite 属性的值（"Strict" 或 "Lax"）。
        return app.config["SESSION_COOKIE_SAMESITE"]  # type: ignore[no-any-return]

    # 返回会话的过期时间，如果会话是永久的，则返回当前时间加上配置的永久会话生命周期。
    # session，类型为 SessionMixin，表示当前的会话对象。
    def get_expiration_time(self, app: Flask, session: SessionMixin) -> datetime | None:
        """A helper method that returns an expiration date for the session
        or ``None`` if the session is linked to the browser session.  The
        default implementation returns now + the permanent session
        lifetime configured on the application.
        """
        # 返回值：过期时间的 datetime 对象或 None。
        if session.permanent:
            return datetime.now(timezone.utc) + app.permanent_session_lifetime
        return None

    # 用于决定是否应该为该会话设置 Set-Cookie 头。
    # 如果会话已修改或会话是永久的并且配置为每次请求刷新会话，则返回 True。
    def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
        """Used by session backends to determine if a ``Set-Cookie`` header
        should be set for this session cookie for this response. If the session
        has been modified, the cookie is set. If the session is permanent and
        the ``SESSION_REFRESH_EACH_REQUEST`` config is true, the cookie is
        always set.

        This check is usually skipped if the session was deleted.

        .. versionadded:: 0.11
        """

        # 返回值：布尔值，指示是否应该设置 Set-Cookie 头。
        return session.modified or (
            session.permanent and app.config["SESSION_REFRESH_EACH_REQUEST"]
        )

    # 在每个请求开始时调用，必须返回实现了字典接口和 SessionMixin 接口的对象。
    # 如果加载失败，应返回 None。
    # request，类型为 Request，表示当前的请求对象。
    # 返回值：实现了 SessionMixin 接口的会话对象或 None。
    def open_session(self, app: Flask, request: Request) -> SessionMixin | None:
        """This is called at the beginning of each request, after
        pushing the request context, before matching the URL.

        This must return an object which implements a dictionary-like
        interface as well as the :class:`SessionMixin` interface.

        This will return ``None`` to indicate that loading failed in
        some way that is not immediately an error. The request
        context will fall back to using :meth:`make_null_session`
        in this case.
        """
        # 方法实现：未实现，抛出 NotImplementedError。
        raise NotImplementedError()

    # 在每个请求结束时调用，必须保存会话数据到响应中。
    # 返回值：无。
    def save_session(
        self, app: Flask, session: SessionMixin, response: Response
    ) -> None:
        """This is called at the end of each request, after generating
        a response, before removing the request context. It is skipped
        if :meth:`is_null_session` returns ``True``.
        """
        # 未实现，抛出 NotImplementedError。
        raise NotImplementedError()

# 定义一个 TaggedJSONSerializer 实例，用于序列化和反序列化会话数据。
session_json_serializer = TaggedJSONSerializer()


# 函数通过在运行时访问 hashlib.sha1，避免了在某些构建中（例如 FIPS 模式）
# 由于 SHA-1 不可用而导致的导入错误。
# 确保了程序在启动时不会因不可用的哈希算法而失败，
# 同时允许开发者在运行时选择和配置其他哈希算法。
# 参数：string，类型为 bytes，默认值为空字节串 b""。
def _lazy_sha1(string: bytes = b"") -> t.Any:
    """Don't access ``hashlib.sha1`` until runtime. FIPS builds may not include
    SHA-1, in which case the import and use as a default would fail before the
    developer can configure something else.
    """
    # 调用 hashlib.sha1 生成 SHA-1 哈希对象。
    return hashlib.sha1(string)


# 实现了基于签名 cookie 的会话接口。
# 通过 itsdangerous 模块签名和验证会话数据，确保会话数据的完整性和安全性。
# 它提供了默认的序列化和反序列化机制，并处理会话的打开和保存逻辑。
class SecureCookieSessionInterface(SessionInterface):
    """The default session interface that stores sessions in signed cookies
    through the :mod:`itsdangerous` module.
    """

    #: the salt that should be applied on top of the secret key for the
    #: signing of cookie based sessions.
    # 用于在签名 cookie 会话时应用于密钥的盐。
    salt = "cookie-session"
    #: the hash function to use for the signature.  The default is sha1
    # 用于签名的哈希函数，默认为 SHA-1。
    digest_method = staticmethod(_lazy_sha1)
    #: the name of the itsdangerous supported key derivation.  The default
    #: is hmac.
    # 用于签名的密钥派生方法，默认为 HMAC。
    key_derivation = "hmac"
    #: A python serializer for the payload.  The default is a compact
    #: JSON derived serializer with support for some extra Python types
    #: such as datetime objects or tuples.
    # 用于会话数据的序列化器，默认为 TaggedJSONSerializer。
    serializer = session_json_serializer
    # 用于会话数据的类，默认为 SecureCookieSession。
    session_class = SecureCookieSession

    # 返回一个用于签名和验证会话数据的 URLSafeTimedSerializer 实例。
    def get_signing_serializer(self, app: Flask) -> URLSafeTimedSerializer | None:
        # 如果未设置 secret_key，则返回 None。
        if not app.secret_key:
            return None
        # 创建一个字典 signer_kwargs，包含签名所需的参数。
        # key_derivation：密钥派生方法。
        # digest_method：摘要方法（哈希函数）。
        signer_kwargs = dict(
            key_derivation=self.key_derivation, digest_method=self.digest_method
        )
        # 创建一个 URLSafeTimedSerializer 实例并返回。
        return URLSafeTimedSerializer(
            app.secret_key,
            salt=self.salt,
            serializer=self.serializer,
            signer_kwargs=signer_kwargs,
        )

    # 打开一个会话。
    # 返回一个 SecureCookieSession 实例，如果未设置 secret_key 或其他原因导致获取失败，则返回 None。
    def open_session(self, app: Flask, request: Request) -> SecureCookieSession | None:
        # 调用 get_signing_serializer 方法获取签名序列化器。
        s = self.get_signing_serializer(app)
        # 如果未设置 secret_key 或其他原因导致获取失败，则返回 None。
        if s is None:
            return None
        # 从请求的 cookies 中获取会话 cookie 的值。
        val = request.cookies.get(self.get_cookie_name(app))
        # 如果会话 cookie 不存在，则返回一个新的空会话实例。
        if not val:
            return self.session_class()
        # 计算会话的最大存活时间（秒），这是应用配置中 permanent_session_lifetime 的值。
        max_age = int(app.permanent_session_lifetime.total_seconds())
        try:
            # 尝试使用签名序列化器加载会话数据。
            data = s.loads(val, max_age=max_age)
            # 如果加载成功，返回一个包含会话数据的 SecureCookieSession 实例。
            return self.session_class(data)
        # 如果捕获到 BadSignature 异常，返回一个新的空会话实例。打开一个会话。
        except BadSignature:
            return self.session_class()

    # 保存会话。
    def save_session(
        # session：类型为 SessionMixin，表示当前的会话对象。
        # response：类型为 Response，表示当前的响应对象。
        self, app: Flask, session: SessionMixin, response: Response
    ) -> None:
        # 获取会话 cookie 的名称、域、路径、安全标志、SameSite 属性和 HttpOnly 标志。
        name = self.get_cookie_name(app)
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        secure = self.get_cookie_secure(app)
        samesite = self.get_cookie_samesite(app)
        httponly = self.get_cookie_httponly(app)

        # 如果会话被访问过，则在响应头中添加 "Vary: Cookie"。
        # Add a "Vary: Cookie" header if the session was accessed at all.
        if session.accessed:
            response.vary.add("Cookie")

        # 如果会话为空且已修改，则删除会话 cookie。
        # 如果会话为空，则返回而不设置 cookie。
        # If the session is modified to be empty, remove the cookie.
        # If the session is empty, return without setting the cookie.
        if not session:
            if session.modified:
                response.delete_cookie(
                    name,
                    domain=domain,
                    path=path,
                    secure=secure,
                    samesite=samesite,
                    httponly=httponly,
                )
                response.vary.add("Cookie")

            return

        # 调用 should_set_cookie 方法检查是否需要设置会话 cookie。
        # 如果不需要，则返回。
        if not self.should_set_cookie(app, session):
            return

        # 获取会话的过期时间。
        expires = self.get_expiration_time(app, session)
        # 使用签名序列化器将会话数据序列化为字符串。
        val = self.get_signing_serializer(app).dumps(dict(session))  # type: ignore[union-attr]
        # 在响应头中设置会话 cookie，包含会话数据、过期时间和其他配置参数。
        response.set_cookie(
            name,
            val,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            samesite=samesite,
        )
        # 添加 "Vary: Cookie" 头。
        response.vary.add("Cookie")


