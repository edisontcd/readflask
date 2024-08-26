# 这行代码是 Python 3.7+ 的特性，允许开发者在类型注解中使用尚未定义的类名。
# 从 Python 3.10 开始，这成为了默认行为。
# 这对于解决循环导入问题或在同一个文件中定义互相引用的类非常有用。
from __future__ import annotations

# 提供了一套用于支持类型提示（Type Hints）的工具，这在 Python 3.5+ 中被引入。
import typing as t

from . import typing as ft
from .globals import current_app
from .globals import request

# F：这是一个类型变量，用于泛型编程。
# bound=t.Callable[..., t.Any]：表示 F 受限于 Callable 类型，
# 即 F 必须是一个可调用对象（如函数或方法）。... 表示可接受任意数量和类型的参数，
# t.Any 表示返回值类型可以是任意类型。
F = t.TypeVar("F", bound=t.Callable[..., t.Any])

# 一个不可变集合（frozenset），包含了常见的 HTTP 方法名。
# frozenset 是一种不可变集合，类似于 set，但其内容一旦创建就不能修改。这在定义常量集合时非常有用。
# 这个集合包含了所有常见的 HTTP 方法，如 GET, POST, DELETE, PATCH 等，
# 用于后续代码中判断或匹配请求的方法。
http_method_funcs = frozenset(
    ["get", "post", "head", "options", "delete", "put", "trace", "patch"]
)


# 用于创建基于类的视图的基类，允许开发者通过子类化 View 来创建可以处理 HTTP 请求的类。
# 提供了一种结构化的方式来创建基于类的视图，使得视图逻辑更容易复用和扩展。
class View:
    """Subclass this class and override :meth:`dispatch_request` to
    create a generic class-based view. Call :meth:`as_view` to create a
    view function that creates an instance of the class with the given
    arguments and calls its ``dispatch_request`` method with any URL
    variables.

    See :doc:`views` for a detailed guide.

    .. code-block:: python

        class Hello(View):
            init_every_request = False

            def dispatch_request(self, name):
                return f"Hello, {name}!"

        app.add_url_rule(
            "/hello/<name>", view_func=Hello.as_view("hello")
        )

    Set :attr:`methods` on the class to change what methods the view
    accepts.

    Set :attr:`decorators` on the class to apply a list of decorators to
    the generated view function. Decorators applied to the class itself
    will not be applied to the generated view function!

    Set :attr:`init_every_request` to ``False`` for efficiency, unless
    you need to store request-global data on ``self``.
    """

    #: The methods this view is registered for. Uses the same default
    #: (``["GET", "HEAD", "OPTIONS"]``) as ``route`` and
    #: ``add_url_rule`` by default.
    # 指定这个视图接受的 HTTP 方法，比如 GET、POST 等。
    # 如果未设置，默认接受 ["GET", "HEAD", "OPTIONS"]。
    methods: t.ClassVar[t.Collection[str] | None] = None

    #: Control whether the ``OPTIONS`` method is handled automatically.
    #: Uses the same default (``True``) as ``route`` and
    #: ``add_url_rule`` by default.
    # 控制是否自动处理 OPTIONS 方法，默认值为 True。
    provide_automatic_options: t.ClassVar[bool | None] = None

    #: A list of decorators to apply, in order, to the generated view
    #: function. Remember that ``@decorator`` syntax is applied bottom
    #: to top, so the first decorator in the list would be the bottom
    #: decorator.
    #:
    #: .. versionadded:: 0.8
    # 
    # 一个装饰器列表，这些装饰器会应用于生成的视图函数。这些装饰器按顺序从上到下应用。
    decorators: t.ClassVar[list[t.Callable[[F], F]]] = []

    #: Create a new instance of this view class for every request by
    #: default. If a view subclass sets this to ``False``, the same
    #: instance is used for every request.
    #:
    #: A single instance is more efficient, especially if complex setup
    #: is done during init. However, storing data on ``self`` is no
    #: longer safe across requests, and :data:`~flask.g` should be used
    #: instead.
    #:
    #: .. versionadded:: 2.2
    # 决定是否在每个请求时创建这个视图类的新实例。
    # 设置为 False 可以重用实例，提升性能，但不能安全地跨请求存储数据。
    init_every_request: t.ClassVar[bool] = True

    # 这是子类需要重写的方法，表示视图的实际行为。
    # 它接收 URL 规则中的变量作为关键字参数，并返回一个 HTTP 响应。
    # 这个方法是视图的核心逻辑，必须在子类中被重写。
    def dispatch_request(self) -> ft.ResponseReturnValue:
        """The actual view function behavior. Subclasses must override
        this and return a valid response. Any variables from the URL
        rule are passed as keyword arguments.
        """
        # 如果这个方法没有被子类重写并调用，会抛出 NotImplementedError 异常。
        raise NotImplementedError()

    # 类方法装饰器，表示 as_view 是一个类方法，而不是实例方法。
    @classmethod
    # 接受视图名称 name 以及任意数量的类参数和类关键字参数，返回一个可以注册到路由的函数。
    def as_view(
        cls, name: 继承自先前定义的 View 基类。
        # 提供了一种方便的方法，将 HTTP 请求方法（如 GET、POST 等）自动分派到同名的类方法上，简化了基于类的视图的创建，特别适用于构建 RESTful API。str, *class_args: t.Any, **class_kwargs: t.Any
    ) -> ft.RouteCallable:
        """Convert the class into a view function that can be registered
        for a route.

        By default, the generated view will create a new instance of the
        view class for every request and call its
        :meth:`dispatch_request` method. If the view class sets
        :attr:`init_every_request` to ``False``, the same instance will
        be used for every request.

        Except for ``name``, all other arguments passed to this method
        are forwarded to the view class ``__init__`` method.

        .. versionchanged:: 2.2
            Added the ``init_every_request`` class attribute.
        """
        # 检查 init_every_request 是否为 True，以决定是否为每个请求创建新的视图类实例。
        if cls.init_every_request:

            # 定义了一个内部函数 view，它是实际的视图函数，接受 URL 中的变量作为关键字参数。
            def view(**kwargs: t.Any) -> ft.ResponseReturnValue:
                # 每次请求都会创建视图类的新实例。
                self = view.view_class(  # type: ignore[attr-defined]
                    *class_args, **class_kwargs
                )
                # 调用 dispatch_request 方法处理请求，ensure_sync 用于确保异步函数在同步上下文中正常工作。
                return current_app.ensure_sync(self.dispatch_request)(**kwargs)  # type: ignore[no-any-return]

        else:
            # 当 init_every_request 为 False 时，创建一个视图类的实例并在多个请求之间重用。
            self = cls(*class_args, **class_kwargs)

            # 定义一个内部函数 view，但这次重用了之前创建的 self 实例。
            def view(**kwargs: t.Any) -> ft.ResponseReturnValue:
                return current_app.ensure_sync(self.dispatch_request)(**kwargs)  # type: ignore[no-any-return]

        # 检查是否有装饰器需要应用到视图函数。
        if cls.decorators:
            # 设置视图函数的名称。
            view.__name__ = name
            # 设置视图函数的模块。
            view.__module__ = cls.__module__
            # 按顺序应用装饰器。
            for decorator in cls.decorators:
                view = decorator(view)

        # We attach the view class to the view function for two reasons:
        # first of all it allows us to easily figure out what class-based
        # view this thing came from, secondly it's also used for instantiating
        # the view class so you can actually replace it with something else
        # for testing purposes and debugging.
        # 将视图类附加到视图函数上，便于调试和测试。
        view.view_class = cls  # type: ignore
        view.__name__ = name
        # 将视图类的文档字符串赋值给视图函数。
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        # 将视图类的 methods 属性赋值给视图函数。
        view.methods = cls.methods  # type: ignore
        # 将视图类的 provide_automatic_options 属性赋值给视图函数。
        view.provide_automatic_options = cls.provide_automatic_options  # type: ignore
        return view


# 继承自先前定义的 View 基类。
# 提供了一种方便的方法，将 HTTP 请求方法（如 GET、POST 等）自动分派到同名的类方法上，
# 简化了基于类的视图的创建，特别适用于构建 RESTful API。
class MethodView(View):
    """Dispatches request methods to the corresponding instance methods.
    For example, if you implement a ``get`` method, it will be used to
    handle ``GET`` requests.

    This can be useful for defining a REST API.

    :attr:`methods` is automatically set based on the methods defined on
    the class.

    See :doc:`views` for a detailed guide.

    .. code-block:: python

        class CounterAPI(MethodView):
            def get(self):
                return str(session.get("counter", 0))

            def post(self):
                session["counter"] = session.get("counter", 0) + 1
                return redirect(url_for("counter"))

        app.add_url_rule(
            "/counter", view_func=CounterAPI.as_view("counter")
        )
    """

    # 这是 Python 在创建一个子类时自动调用的特殊方法。
    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        # 调用父类（即 View 类）的 __init_subclass__ 方法，
        # 确保任何在父类中定义的子类初始化逻辑也被执行。
        super().__init_subclass__(**kwargs)

        # 检查当前子类是否已经显式定义了 methods 属性。
        # 如果子类没有直接定义 methods 属性，那么就需要自动推断并设置。
        if "methods" not in cls.__dict__:
            # 初始化一个空的集合，用于存储该类支持的 HTTP 方法。
            methods = set()

            # 遍历当前类的所有直接父类。
            for base in cls.__bases__:
                # 检查父类是否定义了 methods 属性。
                if getattr(base, "methods", None):
                    # 如果父类定义了 methods，则将其添加到当前的 methods 集合中。
                    methods.update(base.methods)  # type: ignore[attr-defined]

            # 遍历所有标准的 HTTP 方法名称。
            for key in http_method_funcs:
                # 检查当前类是否定义了对应名称的方法。
                if hasattr(cls, key):
                    # 如果类定义了对应的方法，则将其对应的 HTTP 方法名（大写形式）添加到 methods 集合中。
                    methods.add(key.upper())

            # 将生成的 methods 集合赋值给类的 methods 属性。
            # 现在，子类的 methods 属性已经自动设置好了，
            # 包含所有在类中定义的、以及从父类继承的 HTTP 方法。
            if methods:
                cls.methods = methods

    # 定义了 dispatch_request 实例方法，用于处理实际的 HTTP 请求。
    # 根据请求的方法，将请求分派给对应的处理方法（如 get()、post() 等）。
    def dispatch_request(self, **kwargs: t.Any) -> ft.ResponseReturnValue:
        # 尝试从当前实例中获取与请求方法对应的处理方法。
        meth = getattr(self, request.method.lower(), None)

        # If the request method is HEAD and we don't have a handler for it
        # retry with GET.
        # 检查如果没有找到 head 方法处理 HEAD 请求。
        if meth is None and request.method == "HEAD":
            # 尝试使用 get 方法来处理 HEAD 请求。
            meth = getattr(self, "get", None)

        # 断言 meth 不为 None，即确保存在对应的处理方法。
        # 如果断言失败，抛出一个带有具体错误信息的 AssertionError，指明未实现的请求方法。
        assert meth is not None, f"Unimplemented method {request.method!r}"
        # 调用获取到的处理方法并返回其结果。
        return current_app.ensure_sync(meth)(**kwargs)  # type: ignore[no-any-return]


