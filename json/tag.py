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


# 序列化和反序列化那些只有一个键的字典，并且字典的键必须匹配已经注册的标签。
class TagDict(JSONTag):
    """Tag for 1-item dicts whose only key matches a registered tag.

    Internally, the dict key is suffixed with `__`, and the suffix is removed
    when deserializing.
    """

    # 这是一个空的 __slots__，表示这个类没有额外的实例属性，使用这个方式可以节省内存。
    __slots__ = ()
    # 用于标识该标签的键值，序列化过程中会添加到数据中作为标签。
    key = " di"

    # 检查是否某个值符合此类的处理标准。
    def check(self, value: t.Any) -> bool:
        return (
            # 确保值是字典。
            isinstance(value, dict)
            # 确保字典只有一个键。
            and len(value) == 1
            # 确保字典的键在已注册的标签中。
            and next(iter(value)) in self.serializer.tags
        )

    # 将 Python 对象转换为 JSON 兼容类型。
    def to_json(self, value: t.Any) -> t.Any:
        # 获取字典的第一个键。
        key = next(iter(value))
        # self.serializer.tag(value[key]): 将字典的值进行序列化。
        # 在字典的键名后面添加 __，这是该类序列化时的特有行为。
        return {f"{key}__": self.serializer.tag(value[key])}

    # 将 JSON 中的表示恢复为原来的 Python 类型。
    def to_python(self, value: t.Any) -> t.Any:
        # 去掉键名的最后两个字符，也就是 __，从而恢复为原始的键。
        key = next(iter(value))
        return {key[:-2]: value[key]}


# 处理一般的字典类型，确保字典中的值能够被正确序列化，而不对键进行任何特殊处理。
class PassDict(JSONTag):
    __slots__ = ()

    # 检查传入的值是否是一个字典。
    def check(self, value: t.Any) -> bool:
        return isinstance(value, dict)

    # 将 Python 的字典类型序列化为 JSON 格式。
    # 只对字典的值进行处理，键被认为是已经可以直接作为 JSON 的部分，因此没有进行标记。
    def to_json(self, value: t.Any) -> t.Any:
        # JSON objects may only have string keys, so don't bother tagging the
        # key here.
        # 它遍历字典的每个键值对，并使用 self.serializer.tag 方法对值进行递归处理。
        return {k: self.serializer.tag(v) for k, v in value.items()}

    # 这里直接将 tag 方法指向 to_json，即 tag 和 to_json 方法是同一个方法。
    # 这意味着当需要对值进行标记时，直接调用 to_json 方法的实现。
    # 这种方式简化了代码，避免重复定义两个类似功能的方法。
    tag = to_json


# 处理元组（tuple）类型的序列化和反序列化。
class TagTuple(JSONTag):
    __slots__ = ()
    # 给元组类型数据加的标记，表示序列化后的 JSON 中带有 key 为 " t" 的结构是一个元组。
    key = " t"

    # 用来检查传入的值是否是元组类型。
    def check(self, value: t.Any) -> bool:
        return isinstance(value, tuple)

    # 将元组类型转换为 JSON 可以接受的格式，即列表。
    def to_json(self, value: t.Any) -> t.Any:
        # 对元组中的每个元素使用 self.serializer.tag 方法，确保每个元素能够正确序列化。
        return [self.serializer.tag(item) for item in value]

    # 将 JSON 格式中的列表转换回 Python 的元组。
    def to_python(self, value: t.Any) -> t.Any:
        # 假设输入的 value 是一个列表（因为 JSON 中没有元组的概念），
        # 这个方法通过 tuple(value) 将其转换回元组。
        return tuple(value)


# 序列化和反序列化 Python 的 list 类型。
# 虽然 JSON 本身支持列表，但列表中的元素可能包含一些复杂类型（如元组、字典等），
# 这些类型需要特殊处理。
class PassList(JSONTag):
    __slots__ = ()

    # 检查传入的值是否是 list 类型。
    def check(self, value: t.Any) -> bool:
        return isinstance(value, list)

    # 将列表中的每个元素递归转换为 JSON 可接受的格式。
    # 列表本身是 JSON 支持的类型，所以只需确保列表中的每个元素都被正确标记和序列化。
    def to_json(self, value: t.Any) -> t.Any:
        return [self.serializer.tag(item) for item in value]

    tag = to_json


# 序列化和反序列化 bytes 类型的数据。
# 由于 JSON 不直接支持 bytes 类型，所以需要将 bytes 转换为 Base64 编码的字符串格式
class TagBytes(JSONTag):
    __slots__ = ()
    # bytes 类型会被标记为 " b"，以便在反序列化时识别。
    key = " b"

    # 检查传入的 value 是否是 bytes 类型。
    def check(self, value: t.Any) -> bool:
        return isinstance(value, bytes)

    # 将 bytes 类型的值转换为 Base64 编码的字符串。
    # 用 b64encode 来将其转换为 Base64 字符串。
    # 为了符合 JSON 的标准，我们调用 .decode("ascii") 将其转换为 ASCII 字符串。
    def to_json(self, value: t.Any) -> t.Any:
        return b64encode(value).decode("ascii")

    # 将 Base64 编码的字符串还原为原始的 bytes。
    # 使用 b64decode 将字符串转换回 bytes。
    def to_python(self, value: t.Any) -> t.Any:
        return b64decode(value)


# 将实现了 __html__ 方法的对象序列化为 __html__ 方法的结果，
# 并在反序列化时，将其还原为 Markup 类型的对象。
class TagMarkup(JSONTag):
    """Serialize anything matching the :class:`~markupsafe.Markup` API by
    having a ``__html__`` method to the result of that method. Always
    deserializes to an instance of :class:`~markupsafe.Markup`."""

    __slots__ = ()
    # 在序列化为 JSON 时，会使用该 key 来标识数据对应的类型。
    # 在这里，key 为 " m"，表示与 Markup 类相关的对象。
    key = " m"

    # 检查传入的 value 是否符合 Markup 类型，具体来说，是检查对象是否有 __html__ 方法。
    def check(self, value: t.Any) -> bool:
        # 判断 value 是否实现了 __html__ 方法。
        return callable(getattr(value, "__html__", None))

    # 将符合 Markup API 的对象转换为字符串，序列化为 __html__() 方法的结果。
    # 在调用 to_json 时，会执行 __html__ 方法，并将其返回的字符串作为 JSON 值。
    def to_json(self, value: t.Any) -> t.Any:
        return str(value.__html__())

    # 将序列化的 JSON 字符串转换为 Markup 对象。
    def to_python(self, value: t.Any) -> t.Any:
        return Markup(value)


# 处理 UUID 对象的序列化和反序列化。
class TagUUID(JSONTag):
    __slots__ = ()
    key = " u"

    # 检查传入的 value 是否是一个 UUID 对象。
    def check(self, value: t.Any) -> bool:
        return isinstance(value, UUID)

    # 将 UUID 对象转换为其十六进制表示形式。
    def to_json(self, value: t.Any) -> t.Any:
        return value.hex

    # 将存储在 JSON 中的字符串还原为 UUID 对象。
    def to_python(self, value: t.Any) -> t.Any:
        return UUID(value)


# 为 datetime 对象在 JSON 序列化和反序列化过程中提供标记和转换方法。
class TagDateTime(JSONTag):
    __slots__ = ()
    key = " d"

    # 检查给定的 value 是否为 datetime 对象。
    def check(self, value: t.Any) -> bool:
        return isinstance(value, datetime)

    # 将 datetime 对象转换为一个可以被 JSON 处理的类型。
    def to_json(self, value: t.Any) -> t.Any:
        return http_date(value)

    # 将之前序列化为 HTTP 日期字符串的值还原为一个 datetime 对象。
    def to_python(self, value: t.Any) -> t.Any:
        return parse_date(value)


# 通过使用标签系统来序列化和反序列化一些非标准的 JSON 数据类型。
# 这类类型在标准 JSON 中不能被直接表示，因此该类通过为这些类型添加标记（标签）来实现序列化和反序列化的功能。
class TaggedJSONSerializer:
    """Serializer that uses a tag system to compactly represent objects that
    are not JSON types. Passed as the intermediate serializer to
    :class:`itsdangerous.Serializer`.

    The following extra types are supported:

    * :class:`dict`
    * :class:`tuple`
    * :class:`bytes`
    * :class:`~markupsafe.Markup`
    * :class:`~uuid.UUID`
    * :class:`~datetime.datetime`
    """

    # tags 是存储已注册标签类的字典。
    # order 则是标签类的顺序列表，用于序列化和反序列化时按照顺序依次检查数据类型。
    __slots__ = ("tags", "order")

    #: Tag classes to bind when creating the serializer. Other tags can be
    #: added later using :meth:`~register`.
    # 包含一组默认的标签类。
    default_tags = [
        TagDict,
        PassDict,
        TagTuple,
        PassList,
        TagBytes,
        TagMarkup,
        TagUUID,
        TagDateTime,
    ]

    # 构造函数初始化 tags 和 order。tags 存储每个标签的键值对，order 则是序列化时的处理顺序。
    def __init__(self) -> None:
        self.tags: dict[str, JSONTag] = {}
        self.order: list[JSONTag] = []

        # 通过 register 方法将默认的标签类注册到 tags 和 order 中。
        for cls in self.default_tags:
            self.register(cls)

    # 用于注册新的标签类。
    # 可以通过 force 参数决定是否覆盖现有的标签，并且可以通过 index 参数控制标签插入的顺序。
    def register(
        self,
        tag_class: type[JSONTag],
        force: bool = False,
        index: int | None = None,
    ) -> None:
        """Register a new tag with this serializer.

        :param tag_class: tag class to register. Will be instantiated with this
            serializer instance.
        :param force: overwrite an existing tag. If false (default), a
            :exc:`KeyError` is raised.
        :param index: index to insert the new tag in the tag order. Useful when
            the new tag is a special case of an existing tag. If ``None``
            (default), the tag is appended to the end of the order.

        :raise KeyError: if the tag key is already registered and ``force`` is
            not true.
        """
        tag = tag_class(self)
        key = tag.key

        if key:
            if not force and key in self.tags:
                raise KeyError(f"Tag '{key}' is already registered.")

            self.tags[key] = tag

        if index is None:
            self.order.append(tag)
        else:
            self.order.insert(index, tag)

    # 检查传入的 value 是否需要标签。
    # 如果 value 是可序列化的类型（例如 dict、tuple 等），则会调用对应标签类的 tag 方法。
    # 如果 value 是原生 JSON 支持的类型，则直接返回。
    def tag(self, value: t.Any) -> t.Any:
        """Convert a value to a tagged representation if necessary."""
        for tag in self.order:
            if tag.check(value):
                return tag.tag(value)

        return value

    # 用于将打上标签的对象转换回原始的 Python 对象。
    # 通过标签的 key 来确定使用哪个标签类来处理该对象。
    def untag(self, value: dict[str, t.Any]) -> t.Any:
        """Convert a tagged representation back to the original type."""
        if len(value) != 1:
            return value

        key = next(iter(value))

        if key not in self.tags:
            return value

        return self.tags[key].to_python(value[key])

    # 这是一个递归方法，扫描并处理嵌套的数据结构（如 dict 和 list），逐层对其进行反序列化。
    def _untag_scan(self, value: t.Any) -> t.Any:
        if isinstance(value, dict):
            # untag each item recursively
            value = {k: self._untag_scan(v) for k, v in value.items()}
            # untag the dict itself
            value = self.untag(value)
        elif isinstance(value, list):
            # untag each item recursively
            value = [self._untag_scan(item) for item in value]

        return value

    # 序列化对象为紧凑的 JSON 字符串。
    # 首先通过 tag 方法对对象打上标签，然后使用 json.dumps 进行序列化。
    def dumps(self, value: t.Any) -> str:
        """Tag the value and dump it to a compact JSON string."""
        return dumps(self.tag(value), separators=(",", ":"))

    # 反序列化 JSON 字符串，并对任何带标签的对象进行处理，恢复成原始的 Python 类型。
    def loads(self, value: str) -> t.Any:
        """Load data from a JSON string and deserialized any tagged objects."""
        return self._untag_scan(loads(value))


