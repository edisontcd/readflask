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








