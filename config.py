# 这行代码是 Python 3.7+ 的特性，允许开发者在类型注解中使用尚未定义的类名。
# 从 Python 3.10 开始，这成为了默认行为。
# 这对于解决循环导入问题或在同一个文件中定义互相引用的类非常有用。
from __future__ import annotations

# 导入 Python 的 errno 模块，用于处理操作系统相关的错误码。
import errno
# 导入 Python 的 json 模块，用于处理 JSON 数据的编码和解码。
import json
# 导入 Python 的 os 模块，用于与操作系统交互，例如文件操作、环境变量等。
import os
# 导入 Python 的 types 模块，用于操作 Python 中的类型和类。
import types
# 导入 Python 的 typing 模块，并将其重命名为 t，以便在代码中使用类型提示。
import typing as t

# 从 Werkzeug 工具包中导入 import_string 函数，该函数用于根据字符串导入模块或对象。
from werkzeug.utils import import_string

# 用于检查是否在类型检查模式下执行代码，并在类型检查模式下导入模块。
if t.TYPE_CHECKING:
    import typing_extensions as te

    from .sansio.app import App

# 使用 TypeVar 类创建一个类型变量，名称为 "T"。
# 类型变量通常用于泛型编程中，表示可以是任何类型的占位符。
T = t.TypeVar("T")


# 一个泛型类，用于将属性委托给配置对象。
# 泛型类是一种具有泛型参数的类，其中泛型参数可以用来定义类中的属性、方法或方法参数的类型。
# 泛型类允许在类定义中使用未知类型，以便在实际使用时进行具体化。
# 在 Python 中，泛型类通常使用 typing 模块中的 TypeVar 和 Generic 类进行定义。
# TypeVar 用于声明类型变量，表示任意类型的占位符，而 Generic 类则表示泛型类的基类。
class ConfigAttribute(t.Generic[T]):
    """Makes an attribute forward to the config"""

    def __init__(
        # name 表示属性的名称，get_converter 是一个可选的回调函数，用于将配置值转换为指定类型。
        self, name: str, get_converter: t.Callable[[t.Any], T] | None = None
    ) -> None:
        # 将属性名称存储在 __name__ 属性中。
        self.__name__ = name
        # 将传入的转换器函数存储在 get_converter 属性中。
        self.get_converter = get_converter

    # @t.overload：使用 typing 模块中的 overload 装饰器进行函数重载。
    @t.overload
    def __get__(self, obj: None, owner: None) -> te.Self:
        ...

    @t.overload
    def __get__(self, obj: App, owner: type[App]) -> T:
        ...

    # 定义 __get__ 方法，用于获取属性值。它接受两个参数，obj 表示属性所属的对象
    #（例如 App 对象），owner 表示拥有属性的类。方法返回类型可以是 T 或 te.Self。
    def __get__(self, obj: App | None, owner: type[App] | None = None) -> T | te.Self:
        # 如果 obj 为 None，则返回 self，即返回 ConfigAttribute 实例本身。
        if obj is None:
            return self

        # 否则，从对象的配置中获取属性值 rv = obj.config[self.__name__]。
        rv = obj.config[self.__name__]

        # 如果存在转换器函数，则将属性值传递给转换器进行转换。
        if self.get_converter is not None:
            rv = self.get_converter(rv)

        return rv  # type: ignore[no-any-return]

    # 定义 __set__ 方法，用于设置属性值。它接受两个参数，obj 表示属性所属的对象，
    # value 表示要设置的值。该方法没有返回值，只是将值存储到对象的配置中。
    def __set__(self, obj: App, value: t.Any) -> None:
        obj.config[self.__name__] = value


# 继承自内置的 dict 类，可以像字典一样工作，但提供了一些从文件或特殊字典填充配置的方法。
class Config(dict):  # type: ignore[type-arg]
    """Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.

    Either you can fill the config from a config file::

        app.config.from_pyfile('yourconfig.cfg')

    Or alternatively you can define the configuration options in the
    module that calls :meth:`from_object` or provide an import path to
    a module that should be loaded.  It is also possible to tell it to
    use the same module and with that provide the configuration values
    just before the call::

        DEBUG = True
        SECRET_KEY = 'development key'
        app.config.from_object(__name__)

    In both cases (loading from any Python file or loading from modules),
    only uppercase keys are added to the config.  This makes it possible to use
    lowercase values in the config file for temporary values that are not added
    to the config or to define the config keys in the same file that implements
    the application.

    Probably the most interesting way to load configurations is from an
    environment variable pointing to a file::

        app.config.from_envvar('YOURAPPLICATION_SETTINGS')

    In this case before launching the application you have to set this
    environment variable to the file you want to use.  On Linux and OS X
    use the export statement::

        export YOURAPPLICATION_SETTINGS='/path/to/config/file'

    On windows use `set` instead.

    :param root_path: path to which files are read relative from.  When the
                      config object is created by the application, this is
                      the application's :attr:`~flask.Flask.root_path`.
    :param defaults: an optional dictionary of default values
    """

    # 初始化方法。
    def __init__(
        self,
        # 相对于其读取文件的路径，通常为应用程序的根路径；
        root_path: str | os.PathLike[str],
        # 可选的字典，包含默认配置值。
        defaults: dict[str, t.Any] | None = None,
    ) -> None:
        # 使用父类的 __init__ 方法初始化配置对象，并传入默认值或空字典。
        super().__init__(defaults or {})
        # 将 root_path 存储在实例的 root_path 属性中，以供后续使用。
        self.root_path = root_path

    # 用于从环境变量指定的配置文件中加载配置。
    # 是一个简便的方法，相当于以下代码的快捷方式：
    # app.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])
    # variable_name: str: 环境变量的名称，该变量指定了配置文件的路径。
    # silent: bool = False: 如果设置为 True，当找不到配置文件时，方法将静默失败而不会引发异常。
    def from_envvar(self, variable_name: str, silent: bool = False) -> bool:
        """Loads a configuration from an environment variable pointing to
        a configuration file.  This is basically just a shortcut with nicer
        error messages for this line of code::

            app.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])

        :param variable_name: name of the environment variable
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        :return: ``True`` if the file was loaded successfully.
        """
        # 这行代码从环境变量中获取指定名称的变量值，并将其赋给变量 rv。
        rv = os.environ.get(variable_name)
        # 这行代码检查变量 rv 是否为空，如果为空则表示环境变量未设置。
        if not rv:
            # 如果 silent 参数为 True，表示静默失败，那么这行代码会直接返回 False，不会引发异常。
            if silent:
                return False
            # 如果 silent 参数为 False，表示非静默失败，那么这行代码会引发 RuntimeError 异常，
            # 指示环境变量未设置，并提醒用户设置该变量以指向配置文件。
            raise RuntimeError(
                f"The environment variable {variable_name!r} is not set"
                " and as such configuration could not be loaded. Set"
                " this variable and make it point to a configuration"
                " file"
            )
        # 无论是否引发异常，方法都会调用 from_pyfile 方法，传入获取到的配置文件路径 rv，并返回其结果。
        return self.from_pyfile(rv, silent=silent)















