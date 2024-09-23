# 通过标签化 JSON 的方式来处理 Flask 中的非标准 JSON 类型（如 OrderedDict），
# 使得在应用中可以安全而准确地序列化和反序列化会话数据。

"""
Tagged JSON
~~~~~~~~~~~

A compact representation for lossless serialization of non-standard JSON
types. :class:`~flask.sessions.SecureCookieSessionInterface` uses this
to serialize the session data, but it may be useful in other places. It
can be extended to support other types.

.. autoclass:: TaggedJSONSerializer
    :members:

.. autoclass:: JSONTag
    :members:

Let's see an example that adds support for
:class:`~collections.OrderedDict`. Dicts don't have an order in JSON, so
to handle this we will dump the items as a list of ``[key, value]``
pairs. Subclass :class:`JSONTag` and give it the new key ``' od'`` to
identify the type. The session serializer processes dicts first, so
insert the new tag at the front of the order since ``OrderedDict`` must
be processed before ``dict``.

.. code-block:: python

    from flask.json.tag import JSONTag

    class TagOrderedDict(JSONTag):
        __slots__ = ('serializer',)
        key = ' od'

        def check(self, value):
            return isinstance(value, OrderedDict)

        def to_json(self, value):
            return [[k, self.serializer.tag(v)] for k, v in iteritems(value)]

        def to_python(self, value):
            return OrderedDict(value)

    app.session_interface.serializer.register(TagOrderedDict, index=0)
"""

from __future__ import annotations

import typing as t
from base64 import b64decode
from base64 import b64encode
from datetime import datetime
from uuid import UUID

from markupsafe import Markup
from werkzeug.http import http_date
from werkzeug.http import parse_date

from ..json import dumps
from ..json import loads

# JSONTag 类为 TaggedJSONSerializer 提供了一种标准化的方式来标记和序列化特定类型的对象，
# 便于在 Flask 应用中处理更复杂的数据结构。
class JSONTag:
    """Base class for defining type tags for :class:`TaggedJSONSerializer`."""

    # 限定该类实例只能有一个名为 serializer 的属性，这样可以节省内存。
    __slots__ = ("serializer",)

    #: The tag to mark the serialized object with. If empty, this tag is
    #: only used as an intermediate step during tagging.
    # 用于标记序列化对象的标签。如果为空，表示该标签只是标记过程中的一个中间步骤。
    key: str = ""

    # 初始化方法，接受一个 TaggedJSONSerializer 实例并将其存储在 serializer 属性中。
    def __init__(self, serializer: TaggedJSONSerializer) -> None:
        """Create a tagger for the given serializer."""
        self.serializer = serializer

    # 检查给定的值是否应该被此标签标记。该方法需要在子类中实现。
    def check(self, value: t.Any) -> bool:
        """Check if the given value should be tagged by this tag."""
        raise NotImplementedError

    # 将 Python 对象转换为有效的 JSON 类型。该方法同样需要在子类中实现。
    def to_json(self, value: t.Any) -> t.Any:
        """Convert the Python object to an object that is a valid JSON type.
        The tag will be added later."""
        raise NotImplementedError

    # 将 JSON 表示转换回正确的 Python 类型。此方法在子类中实现。
    def to_python(self, value: t.Any) -> t.Any:
        """Convert the JSON representation back to the correct type. The tag
        will already be removed."""
        raise NotImplementedError

    # 将值转换为有效的 JSON 类型，并将标签结构包裹在其中。返回一个包含标签的字典。
    def tag(self, value: t.Any) -> dict[str, t.Any]:
        """Convert the value to a valid JSON type and add the tag structure
        around it."""
        return {self.key: self.to_json(value)}











