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

    # 从环境变量中加载配置，并将其填充到配置对象中。
    def from_prefixed_env(
        # 接受一个可选的前缀参数和一个可选的加载函数参数，并返回一个布尔值表示是否成功加载配置。
        self, prefix: str = "FLASK", *, loads: t.Callable[[str], t.Any] = json.loads
    ) -> bool:
        """Load any environment variables that start with ``FLASK_``,
        dropping the prefix from the env key for the config key. Values
        are passed through a loading function to attempt to convert them
        to more specific types than strings.

        Keys are loaded in :func:`sorted` order.

        The default loading function attempts to parse values as any
        valid JSON type, including dicts and lists.

        Specific items in nested dicts can be set by separating the
        keys with double underscores (``__``). If an intermediate key
        doesn't exist, it will be initialized to an empty dict.

        :param prefix: Load env vars that start with this prefix,
            separated with an underscore (``_``).
        :param loads: Pass each string value to this function and use
            the returned value as the config value. If any error is
            raised it is ignored and the value remains a string. The
            default is :func:`json.loads`.

        .. versionadded:: 2.1
        """
        # 给前缀添加下划线后缀，以便后续检查环境变量时更方便地判断是否以特定前缀开头。
        prefix = f"{prefix}_"
        # 获取前缀字符串的长度，并赋值给变量 len_prefix。
        # 这样做是为了在后续操作中避免重复计算前缀长度。
        len_prefix = len(prefix)

        # 遍历环境变量中的所有键，按键名排序。
        for key in sorted(os.environ):
            # 检查当前键名是否以指定前缀开头，如果不是，则跳过后续操作。
            if not key.startswith(prefix):
                continue

            # 获取环境变量中指定键的值，并将其赋给变量 value。
            value = os.environ[key]

            # 尝试将环境变量的值转换为特定类型，使用了指定的 loads 函数。
            # 如果转换失败，则保持值为字符串类型。
            try:
                value = loads(value)
            except Exception:
                # Keep the value as a string if loading failed.
                pass

            # 去除键名中的前缀部分，以便后续将剩余部分作为配置的键名。
            # Change to key.removeprefix(prefix) on Python >= 3.9.
            key = key[len_prefix:]

            # 检查键名中是否包含双下划线，如果不包含，则表示这是一个非嵌套的键，
            # 直接将键值对设置到配置中，并继续处理下一个环境变量。
            if "__" not in key:
                # A non-nested key, set directly.
                self[key] = value
                continue

            # Traverse nested dictionaries with keys separated by "__".
            # 始化变量 current 为配置对象本身，用于追踪当前的配置字典。
            current = self
            # 拆分键名，将除最后一部分外的所有部分赋值给 *parts，将最后一部分赋值给变量 tail。
            *parts, tail = key.split("__")

            # 根据拆分后的部分逐层创建嵌套的字典结构，确保每一级的嵌套字典存在。
            for part in parts:
                # If an intermediate dict does not exist, create it.
                if part not in current:
                    current[part] = {}

                current = current[part]

            # 将值设置到最内层的嵌套字典中。
            current[tail] = value

        # 返回 True，表示环境变量加载完成。
        return True


    # 从一个Python文件中更新配置的值。
    # 它的作用类似于将文件作为模块导入，并使用 from_object 方法来加载配置。
    def from_pyfile(
        # 接受一个文件名和一个可选的静默参数，并返回一个布尔值表示是否成功加载配置。
        self, filename: str | os.PathLike[str], silent: bool = False
    ) -> bool:
        """Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        :meth:`from_object` function.

        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        :return: ``True`` if the file was loaded successfully.

        .. versionadded:: 0.7
           `silent` parameter.
        """
        # 构造文件的完整路径，使用了配置对象的根路径作为基础路径。
        filename = os.path.join(self.root_path, filename)
        # 创建一个名为 "config" 的模块对象。
        d = types.ModuleType("config")
        # 将模块对象的 __file__ 属性设置为文件名，以便在加载文件时可以正确获取文件路径。
        d.__file__ = filename
        # 尝试打开配置文件并执行其中的代码。
        try:
            # 使用二进制读取模式打开配置文件。
            with open(filename, mode="rb") as config_file:
                # compile 函数将文件内容编译成字节码对象，然后通过 exec 函数在指定的命名空间中执行。
                # 这里的命名空间是模块对象 d 的 __dict__ 属性，因此配置文件中的变量将被添加到模块对象中。
                exec(compile(config_file.read(), filename, "exec"), d.__dict__)
        # 如果打开或执行过程中出现异常，则根据静默参数决定是否忽略异常。
        except OSError as e:
            # 如果设置了静默参数，并且出现了文件不存在、是目录或者不是目录等异常情况，
            # 则返回 False，表示加载配置文件失败但不抛出异常。
            if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
                return False
            # 更新异常对象的错误信息，指示无法加载配置文件。
            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise
        # 调用 from_object 方法，将模块对象作为参数，更新配置对象的值。
        self.from_object(d)
        return True


    # 用于从给定的对象中更新配置值。对象可以是以下两种类型之一：
    # 1.字符串：在这种情况下，将导入具有该名称的对象。2.实际对象引用：直接使用该对象。
    # 通常情况下，对象可以是模块或类。from_object 方法仅加载模块/类的大写属性。
    # dict 对象不适用于 from_object，因为字典的键不是字典类的属性。
    def from_object(self, obj: object | str) -> None:
        """Updates the values from the given object.  An object can be of one
        of the following two types:

        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly

        Objects are usually either modules or classes. :meth:`from_object`
        loads only the uppercase attributes of the module/class. A ``dict``
        object will not work with :meth:`from_object` because the keys of a
        ``dict`` are not attributes of the ``dict`` class.

        Example of module-based configuration::

            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)

        Nothing is done to the object before loading. If the object is a
        class and has ``@property`` attributes, it needs to be
        instantiated before being passed to this method.
        在加载之前，不对对象执行任何操作。如果对象是一个类，并且具有 @property 属性，
        则需要在传递给此方法之前将其实例化。

        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.
        不应该使用此函数加载实际的配置，而应该使用此函数加载配置的默认值。
        实际的配置应该使用 from_pyfile 方法加载，并且最好从不在包内的位置加载，
        因为包可能是系统范围内安装的。

        See :ref:`config-dev-prod` for an example of class-based configuration
        using :meth:`from_object`.

        :param obj: an import name or object
        """
        # 先检查传入的 obj 是否是字符串类型。如果是字符串类型，
        # 则使用 import_string 函数将其转换为相应的对象。
        if isinstance(obj, str):
            obj = import_string(obj)
        # 通过遍历 obj 对象的属性，将所有大写属性的值添加到当前配置对象中。
        # 这样做是为了加载配置对象中的大写属性作为配置项。
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)


    # 从指定文件中加载配置，并根据文件内容更新应用的配置设置。
    def from_file(
        self,
        # 指定要加载的文件的路径。可以是绝对或相对路径。
        filename: str | os.PathLike[str],
        # 函数类型的参数，定义了如何从文件中读取数据。这使得该方法可以处理不同格式的文件
        # （如 JSON, YAML, TOML 等），只需传入相应的加载函数即可。
        load: t.Callable[[t.IO[t.Any]], t.Mapping[str, t.Any]],
        # 当文件不存在时，如果此参数为 True，方法会静默失败（返回 False），否则会抛出异常。
        silent: bool = False,
        # 指定文件应以文本模式还是二进制模式打开。这对于处理那些必须以二进制形式读取的数据格式
        #（如某些特定版本的 TOML 文件）是有用的。
        text: bool = True,
    ) -> bool:
        """Update the values in the config from a file that is loaded
        using the ``load`` parameter. The loaded data is passed to the
        :meth:`from_mapping` method.

        .. code-block:: python

            import json
            app.config.from_file("config.json", load=json.load)

            import tomllib
            app.config.from_file("config.toml", load=tomllib.load, text=False)

        :param filename: The path to the data file. This can be an
            absolute path or relative to the config root path.
        :param load: A callable that takes a file handle and returns a
            mapping of loaded data from the file.
        :type load: ``Callable[[Reader], Mapping]`` where ``Reader``
            implements a ``read`` method.
        :param silent: Ignore the file if it doesn't exist.
        :param text: Open the file in text or binary mode.
        :return: ``True`` if the file was loaded successfully.

        .. versionchanged:: 2.3
            The ``text`` parameter was added.

        .. versionadded:: 2.0
        """
        filename = os.path.join(self.root_path, filename)

        try:
            # 根据 text 参数的值，以文本模式或二进制模式打开文件。
            with open(filename, "r" if text else "rb") as f:
                # 使用 load 函数从打开的文件中读取数据。load 函数应该能处理相应的文件格式，
                # 并返回一个映射类型的数据。
                obj = load(f)
        except OSError as e:
            # 如果在文件打开或数据加载过程中出现 OSError，根据 silent 参数决定是否忽略错误。
            # 如果不忽略错误，则修改错误消息并重新抛出。
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False

            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise

        # 如果文件成功加载，调用 from_mapping 方法来将加载的数据更新到配置中。
        return self.from_mapping(obj)


    # 将给定的键值对更新到当前配置中，但仅更新那些键（key）为大写的条目。
    # 这种设计通常用于环境变量或配置设置，确保只有符合特定命名规范的设置被接受和应用
    def from_mapping(
        # 一个包含配置条目的映射对象，如字典。默认为 None，如果提供，方法将从中读取条目进行更新。
        # 关键字参数，允许在方法调用时直接传入多个配置条目作为参数。
        self, mapping: t.Mapping[str, t.Any] | None = None, **kwargs: t.Any
    ) -> bool:
        """Updates the config like :meth:`update` ignoring items with
        non-upper keys.

        :return: Always returns ``True``.

        .. versionadded:: 0.11
        """
        # 首先创建一个空字典 mappings，用于收集所有需要更新的配置条目。
        mappings: dict[str, t.Any] = {}
        # 如果 mapping 参数不为 None，则将其条目添加到 mappings 字典中。
        if mapping is not None:
            mappings.update(mapping)
        # 将通过关键字参数 kwargs 传递的所有配置条目也合并到 mappings 字典中。
        mappings.update(kwargs)
        # 检查每个键是否为大写。如果是大写，则将该键-值对更新到配置中。
        # 这里使用 self[key] = value 进行赋值，这表明该方法是在一个支持键值赋值操作的
        # 对象上执行，例如一个字典或类似字典的对象。
        for key, value in mappings.items():
            if key.isupper():
                self[key] = value
        return True


    # 用于从配置中提取以特定命名空间为前缀的配置项，并将它们以字典形式返回。
    def get_namespace(
        # namespace (str): 配置项的前缀，方法将返回所有以这个前缀开始的配置项。
        # lowercase (bool, 默认为 True): 指示返回的字典中的键是否应转换为小写。
        # trim_namespace (bool, 默认为 True): 指示是否应从键中去除前缀。
        self, namespace: str, lowercase: bool = True, trim_namespace: bool = True
    ) -> dict[str, t.Any]:
        """Returns a dictionary containing a subset of configuration options
        that match the specified namespace/prefix. Example usage::

            app.config['IMAGE_STORE_TYPE'] = 'fs'
            app.config['IMAGE_STORE_PATH'] = '/var/app/images'
            app.config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
            image_store_config = app.config.get_namespace('IMAGE_STORE_')

        The resulting dictionary `image_store_config` would look like::

            {
                'type': 'fs',
                'path': '/var/app/images',
                'base_url': 'http://img.website.com'
            }

        This is often useful when configuration options map directly to
        keyword arguments in functions or class constructors.

        :param namespace: a configuration namespace
        :param lowercase: a flag indicating if the keys of the resulting
                          dictionary should be lowercase
        :param trim_namespace: a flag indicating if the keys of the resulting
                          dictionary should not include the namespace

        .. versionadded:: 0.11
        """
        # 创建一个空字典 rv，用于存储最终的配置项。
        rv = {}
        # 历配置中的所有项 (self.items())，查找所有键名以 namespace 开头的项。
        for k, v in self.items():
            if not k.startswith(namespace):
                continue
            # 如果 trim_namespace 为 True，则从键名中移除前缀部分。
            if trim_namespace:
                key = k[len(namespace) :]
            else:
                key = k
            # 如果 lowercase 为 True，则将处理后的键名转换为小写。
            if lowercase:
                key = key.lower()
            # 将处理后的键和对应的值存入结果字典 rv。
            rv[key] = v
        # 方法返回结果字典 rv。
        return rv


    # 定义了一个 Python 类的 __repr__ 方法，用于生成对象的官方字符串表示，通常用于调试和开发中。
    # 该方法重写了类的默认 __repr__ 方法，提供了一个更具可读性和有用信息的字符串表示。
    # 重写 __repr__ 方法是提高类在实际应用中的可用性和可维护性的常用技巧。为类提供一个清晰的
    # 字符串表示可以大大简化调试过程，特别是在复杂的应用中，能够快速查看对象的当前状态非常有用。
    def __repr__(self) -> str:
        # 通过 type(self).__name__ 获取当前对象的类名称。type(self) 返回对象的类型，
        # __name__ 属性则提供了类型的名称。
        # dict.__repr__(self) 调用字典的 __repr__ 方法，返回当前对象
        # （假设对象继承自 dict 或表现得像字典）的字典形式的字符串表示。
        # 这个表示将包括所有键值对，格式为 {key: value, ...}。

        # 返回一个字符串，格式为 "<ClassName {dictionary representation}>"。
        # 例如，如果对象的类名是 Config 并且包含数据 { 'a': 1, 'b': 2 }，
        # 则返回的字符串可能看起来像这样："<Config {'a': 1, 'b': 2}>"。
        return f"<{type(self).__name__} {dict.__repr__(self)}>"

