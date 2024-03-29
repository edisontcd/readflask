# 它从 Python 3.7 开始引入，用于提供更好的类型提示功能。
from __future__ import annotations

# Python 中的一个内置模块，用于处理抽象语法树（Abstract Syntax Trees），它提供了一种表示
# Python 代码结构的方式，将源代码解析为树状结构，每个节点表示代码中的一个语法结构。
import ast

# Python 标准库中的一个模块，用于访问安装的 Python 包的元数据。
# 这个模块提供了一种在运行时获取包元信息的方式，而不需要导入整个包。
import importlib.metadata

# Python 的标准库之一，提供了一组用于检查 Python 对象的工具。通过 inspect 模块，
# 你可以获取有关模块、类、方法、函数等对象的信息，包括源代码、方法签名、类层次结构、注释等。
import inspect

# os模块负责程序与操作系统的交互，提供了访问操作系统底层的接口。
import os

# Python 的标准库之一，提供了访问平台相关信息的功能。通过该模块，
# 你可以获取有关系统和硬件平台的信息，如操作系统名称、版本、处理器架构等。
import platform

#Python 中的正则表达式模块。
import re

# 用于访问和操作与 Python 解释器交互的一些系统级功能。
import sys

# 导入用于提取和格式化异常信息的模块。它允许程序捕获、处理和打印异常的堆栈跟踪信息。
import traceback

# typing 模块是 Python 3.5 及更高版本引入的一个标准库模块，
# 用于支持类型提示和类型注解，以提高代码的可读性和可维护性。
import typing as t

# 用于将一个包装函数的属性复制到另一个函数中，通常用于自定义装饰器。
from functools import update_wrapper

# 用于创建一个获取对象的某个索引或键的函数，通常与排序和映射操作一起使用。
from operator import itemgetter

# 用于创建命令行界面（CLI）的 Python 库。
# 它提供了一种简单而强大的方式来定义命令行参数、命令和命令组。
import click
# Click 中用于表示参数来源的枚举类。
from click.core import ParameterSource

# 负责启动本地开发服务器，以便运行提供的 WSGI 应用程序。
from werkzeug import run_simple
# 用于检查是否正在使用重新加载器运行应用程序。
from werkzeug.serving import is_running_from_reloader
# 根据字符串形式的导入路径动态导入模块或对象。
from werkzeug.utils import import_string

# Flask 应用程序上下文中的全局变量，表示当前运行的应用程序实例。
from .globals import current_app

# 用于获取调试标志和加载环境变量。
from .helpers import get_debug_flag
from .helpers import get_load_dotenv

# 在类型提示代码块中使用的类型不会导致实际的导入，以避免循环导入问题。
if t.TYPE_CHECKING:
    from .app import Flask

# 在 Click 库中，click.UsageError 是一个表示用户使用错误的异常类。
# 通过继承它，可以定义应用程序加载失败时引发的特定类型的异常。
class NoAppException(click.UsageError):
    """Raised if an application cannot be found or loaded."""

# 在给定的模块中找到一个 Flask 应用程序实例，如果找不到或存在歧义，就会引发异常。
def find_best_app(module):
    """Given a module instance this tries to find the best possible
    application in the module or raises an exception.
    """

    # 引入了 Flask 类，使得在后续代码中可以直接使用 Flask 而不需要写完整的包路径。
    from . import Flask

    # 尝试从给定的模块中查找 Flask 应用实例。
    # Search for the most common names first.
    for attr_name in ("app", "application"):
        # getattr 是 Python 内置函数，用于从对象中获取指定属性的值。
        # 从给定的模块 module 中获取属性名为 attr_name 的属性值，如果属性不存在，则返回 None。
        app = getattr(module, attr_name, None)

        # 检查变量 app 是否是 Flask 类的实例。如果是，就返回该实例，意味着找到了 Flask 应用对象。
        if isinstance(app, Flask):
            return app

    # 它通过遍历模块中的所有属性值，找到那些是 Flask 类的实例的对象，并将它们存储在 matches 列表中。
    # Otherwise find the only object that is a Flask instance.
    matches = [v for v in module.__dict__.values() if isinstance(v, Flask)]

    # 首先检查是否有一个（且只有一个）Flask 实例。如果找到一个，它将作为最佳匹配返回。
    # 如果找到多个 Flask 实例，则会引发异常，指示检测到模块中的多个 Flask 应用，
    # 需要通过指定正确的名称来解决。
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise NoAppException(
            "Detected multiple Flask applications in module"
            f" '{module.__name__}'. Use '{module.__name__}:name'"
            " to specify the correct one."
        )

    
    # Search for app factory functions.
    for attr_name in ("create_app", "make_app"):

        # getattr 是 Python 内置函数，用于从对象中获取指定属性的值。
        # 从给定的模块 module 中获取属性名为 attr_name 的属性值，如果属性不存在，则返回 None。
        app_factory = getattr(module, attr_name, None)

        # 从模块中的工厂函数中找到并返回一个有效的 Flask 实例，或者在找不到有效实例时引发异常。
        # 检查 app_factory 是否是一个函数。这是通过 inspect 模块中的 isfunction 函数实现的。
        if inspect.isfunction(app_factory):
            try:
                # 尝试调用 app_factory 函数，将结果赋值给 app。
                app = app_factory()

                # if isinstance(app, Flask):：检查 app 是否是 Flask 类的实例。
                if isinstance(app, Flask):
                    # 如果调用成功且返回的对象是 Flask 实例，将其返回。
                    return app
            # 捕获可能发生的 TypeError 异常，并将异常对象赋值给变量 e。
            except TypeError as e:
                # 检查是否能够判断出 TypeError 是因为函数调用失败而不是由于其他原因。
                # 如果是因为调用失败，执行以下代码块。
                if not _called_with_wrong_args(app_factory):
                    raise

                # 在检测到模块中存在工厂函数，但是尝试调用它时出现了 TypeError 异常
                #（即没有传递所需的参数），于是抛出 NoAppException 异常。
                # from e：在异常链中引入原始异常，以保留原始的异常信息。
                raise NoAppException(
                    f"Detected factory '{attr_name}' in module '{module.__name__}',"
                    " but could not call it without arguments. Use"
                    f" '{module.__name__}:{attr_name}(args)'"
                    " to specify arguments."
                ) from e

    # 当在模块中找不到有效的 Flask 应用或工厂函数时，抛出 NoAppException 异常。
    raise NoAppException(
        "Failed to find Flask application or factory in module"
        f" '{module.__name__}'. Use '{module.__name__}:name'"
        " to specify one."
    )


# 检查调用一个函数是否因为调用失败而引发了 TypeError 异常，
# 还是因为工厂函数内部的某些原因引发了错误。
def _called_with_wrong_args(f):
    """Check whether calling a function raised a ``TypeError`` because
    the call failed or because something in the factory raised the
    error.

    :param f: The function that was called.
    :return: ``True`` if the call failed.
    """
    # sys.exc_info() 函数返回当前线程的异常信息。它返回一个包含三个值的元组：
    # sys.exc_info()[0] 返回异常类型。
    # sys.exc_info()[1] 返回异常对象。
    # sys.exc_info()[2] 返回 traceback 对象。
    tb = sys.exc_info()[2]

    try:
        # 通过迭代 traceback 对象的链表，检查每个帧（frame）是否与函数的代码对象相匹配。
        while tb is not None:
            # 比较当前迭代的 traceback 节点的帧代码对象是否与函数的代码对象匹配。
            # 如果匹配，说明在函数中成功调用了。
            if tb.tb_frame.f_code is f.__code__:
                # In the function, it was called successfully.
                # 如果找到匹配的帧，说明函数成功调用，返回 False。
                return False

            # 如果当前迭代的 traceback 节点没有匹配的帧，移动到链表中的下一个节点。
            tb = tb.tb_next

        # Didn't reach the function.
        # 如果遍历整个 traceback 链表都没有找到匹配的帧，说明函数没有成功调用，返回 True。
        return True
    finally:
        # Delete tb to break a circular reference.
        # https://docs.python.org/2/library/sys.html#sys.exc_info
        # 删除 traceback 对象，以打破可能存在的循环引用。这是为了确保在函数调用结束后及时释放资源。
        del tb


# 根据输入的字符串名称，在给定的模块中查找或调用相应的 Flask 应用程序，并返回找到的应用程序实例。
def find_app_by_string(module, app_name):
    """Check if the given string is a variable name or a function. Call
    a function to get the app instance, or return the variable directly.
    """
    #检查给定字符串是否为变量名或函数调用。调用函数以获取应用程序实例，或直接返回变量。
    from . import Flask

    # Parse app_name as a single expression to determine if it's a valid
    # attribute name or function call.
    # 解析 app_name 作为单个表达式，以确定它是否是有效的属性名或函数调用。
    try:
        # 尝试解析给定的字符串表达式为 AST 表达式，mode="eval" 表示这是一个表达式。
        expr = ast.parse(app_name.strip(), mode="eval").body
    # 如果解析失败，会抛出 SyntaxError 异常。
    except SyntaxError:
        # 在发生 SyntaxError 异常时，会捕获该异常，并使用 raise NoAppException(...) 
        # 语句抛出一个 NoAppException 异常，其中包含相应的错误信息，说明解析失败的原因是
        # 给定的字符串无法解析为属性名或函数调用。
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        # 表示异常的原因是由于语法错误，而不是其他异常，因此异常链中不包含原始的异常信息。
        ) from None

    # 检查 expr 是否是 AST（抽象语法树）中的 Name 类型。
    if isinstance(expr, ast.Name):
        # 如果 expr 是 ast.Name 类型的实例，说明 app_name 是一个简单的变量名，而不是一个函数调用。
        # 在这种情况下，将 name 设置为变量名，并将 args 和 kwargs 初始化为空列表和空字典。
        name = expr.id
        args = []
        kwargs = {}
    # 检查 expr 是否是 AST 中的 Call 类型。如果是 Call 类型，说明 app_name 是一个函数调用。
    elif isinstance(expr, ast.Call):
        # Ensure the function name is an attribute name only.
        # 检查函数调用中的函数名是否是一个简单的变量名。如果不是 ast.Name 类型，
        # 说明函数名不符合要求，抛出 NoAppException 异常。
        if not isinstance(expr.func, ast.Name):
            raise NoAppException(
                f"Function reference must be a simple name: {app_name!r}."
            )

        name = expr.func.id

        # Parse the positional and keyword arguments as literals.
        # # 解析位置参数和关键字参数为字面值。
        try:
            args = [ast.literal_eval(arg) for arg in expr.args]
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in expr.keywords}
        except ValueError:
            # literal_eval gives cryptic error messages, show a generic
            # message with the full expression instead.
            # literal_eval 提供了晦涩的错误消息，因此显示一个带有完整表达式的通用消息。
            raise NoAppException(
                f"Failed to parse arguments as literal values: {app_name!r}."
            ) from None
    else:
        # 如果既不是 Name 类型也不是 Call 类型，抛出 NoAppException 异常。
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        )

    try:
        # 尝试获取模块中的属性。
        attr = getattr(module, name)
    except AttributeError as e:
        # 如果属性不存在，抛出 NoAppException 异常。
        raise NoAppException(
            f"Failed to find attribute {name!r} in {module.__name__!r}."
        ) from e

    # If the attribute is a function, call it with any args and kwargs
    # to get the real application.
    # 如果属性是函数，调用它以获取真实的应用程序。
    if inspect.isfunction(attr):
        try:
            app = attr(*args, **kwargs)
        except TypeError as e:
            if not _called_with_wrong_args(attr):
                raise

            raise NoAppException(
                f"The factory {app_name!r} in module"
                f" {module.__name__!r} could not be called with the"
                " specified arguments."
            ) from e
    else:
        # 如果属性不是函数，直接将属性赋值给 app。
        app = attr

    # 如果 app 是 Flask 类型的实例，返回 app。
    if isinstance(app, Flask):
        return app

    # 如果 app 不是 Flask 类型的实例，抛出 NoAppException 异常。
    raise NoAppException(
        "A valid Flask application was not obtained from"
        f" '{module.__name__}:{app_name}'."
    )

# 给定一个文件名，尝试计算Python路径，将其添加到搜索路径并返回实际的模块名。
def prepare_import(path: str) -> str:
    """Given a filename this will try to calculate the python path, add it
    to the search path and return the actual module name that is expected.
    """

    # # 获取文件的真实路径
    path = os.path.realpath(path)

    # os.path.splitext 函数分割文件路径，将文件名和文件扩展名分开。
    fname, ext = os.path.splitext(path)
    
    # 如果文件是.py文件，则使用去掉扩展名的路径
    if ext == ".py":
        path = fname

    # # 如果文件名是__init__，则使用其所在目录的路径
    if os.path.basename(path) == "__init__":
        path = os.path.dirname(path)

    module_name = []

    # move up until outside package structure (no __init__.py)
    # # 逐层向上移动，直到超出包结构（没有__init__.py文件）
    while True:
        # 分割并返回一个包含两个元素的元组，第一个元素是目录部分，第二个元素是文件/目录名部分。
        path, name = os.path.split(path)
        module_name.append(name)

        # 检查当前目录是否包含 __init__.py 文件，os.path.join 用于构建完整的路径。
        if not os.path.exists(os.path.join(path, "__init__.py")):
            break

    # # 如果搜索路径的第一个元素不是目标路径，将其插入到搜索路径的最前面
    if sys.path[0] != path:
        sys.path.insert(0, path)

    # # 返回模块名，通过"."连接并反转列表
    return ".".join(module_name[::-1])

# @overload: 这是一个装饰器，表示下面的函数签名是一个函数的声明，而不是实际的实现。
@t.overload
def locate_app(
    module_name: str, app_name: str | None, raise_if_not_found: t.Literal[True] = True
# 函数返回一个 Flask 类型的对象。
) -> Flask:
    # ... 表示占位符。
    ...

@t.overload
def locate_app(
    # 这里使用 ... 表示这个参数在声明中是占位符，具体的默认值等可能在下面的实现中给出。
    module_name: str, app_name: str | None, raise_if_not_found: t.Literal[False] = ...
    # 函数返回一个 Flask 类型的对象或者 None。
) -> Flask | None:
    ...

# 根据给定的参数和逻辑，尝试导入指定的模块，然后根据条件返回相应的 Flask 应用程序实例或者 None。
def locate_app(
    module_name: str, app_name: str | None, raise_if_not_found: bool = True
) -> Flask | None:
    try:
        # 使用 __import__ 函数尝试导入指定的模块。
        __import__(module_name)
    except ImportError:
        # Reraise the ImportError if it occurred within the imported module.
        # Determine this by checking whether the trace has a depth > 1.
        # 判断异常是否发生在导入的模块内部，通过检查堆栈深度是否大于 1。如果是，重新引发 ImportError。
        if sys.exc_info()[2].tb_next:  # type: ignore[union-attr]
            raise NoAppException(
                f"While importing {module_name!r}, an ImportError was"
                f" raised:\n\n{traceback.format_exc()}"
            ) from None
        # 如果没有在导入的模块内部发生异常，而且 raise_if_not_found 为 True，
        # 则抛出 NoAppException 异常，表示无法导入指定的模块。
        elif raise_if_not_found:
            raise NoAppException(f"Could not import {module_name!r}.") from None
        # 如果没有在导入的模块内部发生异常，而且 raise_if_not_found 为 False，
        # 则返回 None，表示导入失败但不引发异常。
        else:
            return None

    # 获取导入的模块对象。
    module = sys.modules[module_name]

    if app_name is None:
        return find_best_app(module)
    else:
        return find_app_by_string(module, app_name)


# 在一个命令行程序中定义了一个 --version 选项，当使用这个选项时，
# 会打印出程序依赖的 Python、Flask 和 Werkzeug 的版本信息。
def get_version(ctx: click.Context, param: click.Parameter, value: t.Any) -> None:
    # 这里检查是否提供了 --version 标志。如果没有提供或者是在 "resilient parsing" 模式下
    #（这通常用于自动补全或类似的功能，不处理实际的命令逻辑），函数就不执行任何操作并返回。
    if not value or ctx.resilient_parsing:
        return

    flask_version = importlib.metadata.version("flask")
    werkzeug_version = importlib.metadata.version("werkzeug")

    # 使用 Click 的 echo 函数打印版本信息。这个函数比标准的 print 更适合用在命令行程序中，
    # 因为它可以处理一些复杂的输出情况，如颜色输出和重定向。
    click.echo(
        f"Python {platform.python_version()}\n"
        f"Flask {flask_version}\n"
        f"Werkzeug {werkzeug_version}",
        color=ctx.color,
    )
    ctx.exit()


version_option = click.Option(
    ["--version"],
    help="Show the Flask version.",
    expose_value=False,
    callback=get_version,
    is_flag=True,
    is_eager=True,
)


# 为 Flask 应用和 Click 命令行工具之间的交互提供了一个灵活的桥梁。
# 通过允许动态地指定 Flask 应用的导入路径或创建函数，它支持更加动态和灵活的应用程序初始化方式。
# Flask CLI 用于存储和访问应用加载信息的对象。
class ScriptInfo:
    """Helper object to deal with Flask applications.  This is usually not
    necessary to interface with as it's used internally in the dispatching
    to click.  In future versions of Flask this object will most likely play
    a bigger role.  Typically it's created automatically by the
    :class:`FlaskGroup` but you can also manually create it and pass it
    onwards as click object.
    """

    def __init__(
        self,
        # 用于指定 Flask 应用程序的导入路径。这允许 ScriptInfo 在需要时动态加载 Flask 应用。
        app_import_path: str | None = None,
        # 接收 ScriptInfo 作为参数并返回 Flask 应用的实例。这提供了一种灵活的方式来创建 Flask 应用。
        create_app: t.Callable[..., Flask] | None = None,
        # 指示是否应该根据环境变量自动设置 Flask 应用的调试标志。
        set_debug_flag: bool = True,
    ) -> None:
        #: Optionally the import path for the Flask application.
        # 存储 Flask 应用导入路径的属性。
        self.app_import_path = app_import_path
        #: Optionally a function that is passed the script info to create
        #: the instance of the application.
        # 存储用于创建 Flask 应用实例的回调函数的属性。
        self.create_app = create_app
        #: A dictionary with arbitrary data that can be associated with
        #: this script info.
        # 用于关联与此 ScriptInfo 实例相关的任意数据。这为存储和传递额外信息提供了便利。
        self.data: dict[t.Any, t.Any] = {}
        # 存储一个布尔值，指示是否设置调试标志的属性。
        self.set_debug_flag = set_debug_flag
        # 加载的 Flask 应用实例。
        self._loaded_app: Flask | None = None

    # 加载 Flask 应用程序（如果还没有加载），并返回它。
    # 如果这个方法被多次调用，它只会返回已经加载的应用程序实例。
    def load_app(self) -> Flask:
        """Loads the Flask app (if not yet loaded) and returns it.  Calling
        this multiple times will just result in the already loaded app to
        be returned.
        """

        # 检查 _loaded_app 属性是否已经有了 Flask 应用的实例。
        # 如果有，就直接返回这个实例，不再进行加载。
        if self._loaded_app is not None:
            return self._loaded_app

        # 如果提供了 create_app 函数（即不为 None），则调用这个函数尝试创建Flask应用实例。
        if self.create_app is not None:
            app: Flask | None = self.create_app()
        else:
            # 如果没有提供 create_app 函数，但提供了应用的导入路径（app_import_path），
            # 方法会尝试解析这个路径并加载应用。路径可以包含一个冒号分隔的模块路径和应用名称，
            # 如果只有模块路径，则尝试在该模块中定位应用。
            if self.app_import_path:
                path, name = (
                    # 使用正则表达式 re.split 分割路径和应用名
                    re.split(r":(?![\\/])", self.app_import_path, maxsplit=1) + [None]
                )[:2]
                # 然后通过 prepare_import 函数和 locate_app 函数尝试定位和加载应用。
                import_name = prepare_import(path)
                app = locate_app(import_name, name)
            else:
                # 如果没有提供导入路径，方法会尝试在当前目录下的wsgi.py或app.py文件中查找Flask应用。
                for path in ("wsgi.py", "app.py"):
                    import_name = prepare_import(path)
                    app = locate_app(import_name, None, raise_if_not_found=False)

                    if app is not None:
                        break
        # 如果上述步骤都无法加载或创建Flask应用实例，则抛出NoAppException异常，
        # 提示无法定位Flask应用。
        if app is None:
            raise NoAppException(
                "Could not locate a Flask application. Use the"
                " 'flask --app' option, 'FLASK_APP' environment"
                " variable, or a 'wsgi.py' or 'app.py' file in the"
                " current directory."
            )
        # 如果设置了 set_debug_flag 为 True，则通过 get_debug_flag 函数获取调试标志，
        # 并设置给加载的 Flask 应用。
        if self.set_debug_flag:
            # Update the app's debug flag through the descriptor so that
            # other values repopulate as well.
            app.debug = get_debug_flag()

        # 将加载或创建的 Flask 应用实例保存到 _loaded_app 属性中，并返回这个实例。
        self._loaded_app = app
        return app

# click.make_pass_decorator 是 Click 库的一个功能，用于创建一个装饰器，
# 该装饰器在命令行接口（CLI）命令的函数中自动传递定义的对象。
# 在这个例子中，它用于创建一个装饰器 pass_script_info，
# 这个装饰器确保 ScriptInfo 类的一个实例会被传递到使用它的命令函数中。
# ScriptInfo：这是要传递的对象的类。
# ensure=True：这个参数指定如果当前上下文中不存在 ScriptInfo 的实例，Click 将会自动创建一个实例。
# 这样，当定义 Flask 应用的 CLI 命令时，可以使用 @pass_script_info 装饰器
# 来自动获得一个 ScriptInfo 实例，而无需在每个命令中手动创建或传递它。
pass_script_info = click.make_pass_decorator(ScriptInfo, ensure=True)

# 定义了一个名为 F 的类型变量，它被限定为任何形式的可调用对象，其参数和返回类型是任意的。
F = t.TypeVar("F", bound=t.Callable[..., t.Any])


# 定义了一个装饰器函数 with_appcontext，它用于确保被装饰的回调（callback）函数总是在
# Flask 应用的上下文中执行。这对于编写需要访问 Flask 应用或其配置的自定义命令非常有用。
# 参数：f: F 表示这个装饰器可以接受任意的可调用对象作为参数，这得益于之前定义的类型变量 F。
def with_appcontext(f: F) -> F:
    """Wraps a callback so that it's guaranteed to be executed with the
    script's application context.

    Custom commands (and their options) registered under ``app.cli`` or
    ``blueprint.cli`` will always have an app context available, this
    decorator is not required in that case.

    .. versionchanged:: 2.2
        The app context is active for subcommands as well as the
        decorated callback. The app context is always available to
        ``app.cli`` command and parameter callbacks.
    """

    # 使用 @click.pass_context 装饰器来传递 Click 的命令行上下文对象。
    # 这允许装饰器内的函数访问当前命令行调用的上下文。
    @click.pass_context
    def decorator(ctx: click.Context, /, *args: t.Any, **kwargs: t.Any) -> t.Any:
        # 在调用被装饰的函数之前，装饰器会检查 Flask 的 current_app 是否存在。
        # 如果不存在，它会通过从 Click 的上下文中获取 ScriptInfo 实例并
        # 调用 load_app 方法来加载 Flask 应用，并随后激活该应用的上下文。
        if not current_app:
            app = ctx.ensure_object(ScriptInfo).load_app()
            ctx.with_resource(app.app_context())

        # 使用 ctx.invoke 方法调用原始函数 f，传递任何位置参数和关键字参数。
        # 这样做可以保持调用的原始性质，并且允许通过装饰器透传参数。
        return ctx.invoke(f, *args, **kwargs)

    # 更新装饰器函数的元数据，使之匹配原始函数 f。
    # 这一步骤是为了确保装饰后的函数在外部看起来仍然像原始函数，包括函数名称、文档字符串等。
    return update_wrapper(decorator, f)  # type: ignore[return-value]


# AppGroup 类是对 Click 的 Group 类的扩展，专门用于 Flask 应用程序。
# 它修改了 command 和 group 方法的行为，使得通过这个类注册的命令和子命令组
# 自动使用 with_appcontext 装饰器，从而确保所有的命令都在 Flask 应用上下文中执行。
class AppGroup(click.Group):
    """This works similar to a regular click :class:`~click.Group` but it
    changes the behavior of the :meth:`command` decorator so that it
    automatically wraps the functions in :func:`with_appcontext`.

    Not to be confused with :class:`FlaskGroup`.
    """

    # 几乎和 Click 的 Group.command 方法一样，但是它有一个关键的区别：它会自动将回调函数用
    # with_appcontext 装饰器包装起来，除非通过设置 with_appcontext=False 明确禁用这个行为。
    def command(  # type: ignore[override]
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], click.Command]:
        """This works exactly like the method of the same name on a regular
        :class:`click.Group` but it wraps callbacks in :func:`with_appcontext`
        unless it's disabled by passing ``with_appcontext=False``.
        """
        # 变量决定了是否应该应用 with_appcontext 装饰器。
        wrap_for_ctx = kwargs.pop("with_appcontext", True)

        def decorator(f: t.Callable[..., t.Any]) -> click.Command:
            if wrap_for_ctx:
                # 在将函数 f 包装后，它调用父类的 command 方法来注册包装后的命令。
                f = with_appcontext(f)
            return super(AppGroup, self).command(*args, **kwargs)(f)  # type: ignore[no-any-return]

        return decorator

    # group 方法也被修改以自动设置子命令组类为 AppGroup。
    def group(  # type: ignore[override]
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], click.Group]:
        """This works exactly like the method of the same name on a regular
        :class:`click.Group` but it defaults the group class to
        :class:`AppGroup`.
        """
        kwargs.setdefault("cls", AppGroup)
        return super().group(*args, **kwargs)  # type: ignore[no-any-return]


# 用作 Click 选项的回调函数，目的是根据提供的值设置 Flask 应用的导入路径。
# ctx：Click 的上下文对象，用于存储和传递命令行命令执行期间的状态。
# param：触发这个回调函数的 Click 选项对象。
# value：命令行中指定的选项值，即 Flask 应用的导入路径。
def _set_app(ctx: click.Context, param: click.Option, value: str | None) -> str | None:
    if value is None:
        return None

    # 使用 ctx.ensure_object(ScriptInfo) 确保有一个 ScriptInfo 的实例，
    # 并将其与当前的 Click 上下文关联。
    info = ctx.ensure_object(ScriptInfo)
    info.app_import_path = value
    return value


# 一个定义为 Click 选项的对象，用于在命令行中指定 Flask 应用或工厂函数的导入路径。
# This option is eager so the app will be available if --help is given.
# --help is also eager, so --app must be before it in the param list.
# no_args_is_help bypasses eager processing, so this option must be
# processed manually in that case to ensure FLASK_APP gets picked up.
_app_option = click.Option(
    # 允许用户在命令行中通过 -A 或 --app 选项指定 Flask 应用的导入路径。
    ["-A", "--app"],
    metavar="IMPORT",
    help=(
        "The Flask application or factory function to load, in the form 'module:name'."
        " Module can be a dotted import or file path. Name is not required if it is"
        " 'app', 'application', 'create_app', or 'make_app', and can be 'name(args)' to"
        " pass arguments."
    ),
    is_eager=True,
    expose_value=False,
    callback=_set_app,
)


# 作为一个回调函数用于处理当 --debug 或 --no-debug 选项被指定在命令行中时的逻辑。
def _set_debug(ctx: click.Context, param: click.Option, value: bool) -> bool | None:
    # If the flag isn't provided, it will default to False. Don't use
    # that, let debug be set by env in that case.
    # 检查这个选项值是如何被设置的。
    source = ctx.get_parameter_source(param.name)  # type: ignore[arg-type]

    # 如果这个选项的值来自默认设置或默认映射（即用户没有在命令行中明确指定这个选项），
    # 函数将不做任何操作并返回 None。
    if source is not None and source in (
        ParameterSource.DEFAULT,
        ParameterSource.DEFAULT_MAP,
    ):
        return None

    # 如果用户确实在命令行中指定了 --debug 或 --no-debug，函数则根据用户的选择通过设置
    # 环境变量 FLASK_DEBUG 为 "1" 或 "0" 来启用或禁用调试模式。
    # 这种方式允许在 Flask 应用的早期启动阶段，比如工厂函数中，就可以访问到调试模式的设置。
    # Set with env var instead of ScriptInfo.load so that it can be
    # accessed early during a factory function.
    os.environ["FLASK_DEBUG"] = "1" if value else "0"
    return value


# 这个回调函数被关联到 --debug/--no-debug 选项，使得它能够在解析命令行参数时被自动调用。
_debug_option = click.Option(
    ["--debug/--no-debug"],
    help="Set debug mode.",
    expose_value=False,
    callback=_set_debug,
)


# 定义了一个 Click 选项回调函数 _env_file_callback 和一个与之关联的命令行选项 _env_file_option。
# 这个功能允许用户通过命令行指定一个环境变量文件，从而在 Flask 应用启动前加载这些环境变量。
def _env_file_callback(
    ctx: click.Context, param: click.Option, value: str | None
) -> str | None:
    if value is None:
        return None

    import importlib

    try:
        importlib.import_module("dotenv")
    except ImportError:
        raise click.BadParameter(
            "python-dotenv must be installed to load an env file.",
            ctx=ctx,
            param=param,
        ) from None

    # Don't check FLASK_SKIP_DOTENV, that only disables automatically
    # loading .env and .flaskenv files.
    load_dotenv(value)
    return value


# This option is eager so env vars are loaded as early as possible to be
# used by other options.
_env_file_option = click.Option(
    ["-e", "--env-file"],
    # 指定了选项值应该是一个存在的文件路径，不应该是一个目录。
    type=click.Path(exists=True, dir_okay=False),
    # 提供了关于这个选项的帮助信息，说明了它的作用和 python-dotenv 的依赖要求。
    help="Load environment variables from this file. python-dotenv must be installed.",
    # 这个选项被标记为急切的，意味着一旦解析到这个选项，它的回调函数会立即执行。
    # 这是为了确保环境变量尽可能早地被加载，以便它们能够被后续的选项或应用配置使用。
    is_eager=True,
    expose_value=False,
    callback=_env_file_callback,
)


# 它是 AppGroup 类的一个特殊子类，用于支持从配置的 Flask 应用中加载更多命令。
class FlaskGroup(AppGroup):
    """Special subclass of the :class:`AppGroup` group that supports
    loading more commands from the configured Flask app.  Normally a
    developer does not have to interface with this class but there are
    some very advanced use cases for which it makes sense to create an
    instance of this. see :ref:`custom-scripts`.

    :param add_default_commands: if this is True then the default run and
        shell commands will be added.
    :param add_version_option: adds the ``--version`` option.
    :param create_app: an optional callback that is passed the script info and
        returns the loaded app.
    :param load_dotenv: Load the nearest :file:`.env` and :file:`.flaskenv`
        files to set environment variables. Will also change the working
        directory to the directory containing the first file found.
    :param set_debug_flag: Set the app's debug flag.

    .. versionchanged:: 2.2
        Added the ``-A/--app``, ``--debug/--no-debug``, ``-e/--env-file`` options.

    .. versionchanged:: 2.2
        An app context is pushed when running ``app.cli`` commands, so
        ``@with_appcontext`` is no longer required for those commands.

    .. versionchanged:: 1.0
        If installed, python-dotenv will be used to load environment variables
        from :file:`.env` and :file:`.flaskenv` files.
    """

    # FlaskGroup 类的构造函数，用于初始化一个 FlaskGroup 实例。
    def __init__(
        self,
        # 添加默认的 run 和 shell 命令。
        add_default_commands: bool = True,
        # 一个可选的回调函数，传入脚本信息，并返回加载的 app。
        create_app: t.Callable[..., Flask] | None = None,
        # 如果为 True，则添加 --version 选项。
        add_version_option: bool = True,
        # 如果为 True，则加载最近的 .env 和 .flaskenv 文件以设置环境变量，
        # 并更改工作目录到找到的第一个文件所在的目录。
        load_dotenv: bool = True,
        # 设置 app 的调试标志。
        set_debug_flag: bool = True,
        # 接收任何额外的关键字参数。
        **extra: t.Any,
    ) -> None:
        # 从 extra 字典中取出名为 "params" 的项。如果没有找到，就使用一个空列表作为默认值。
        # 然后，将其转换为列表，存储在局部变量 params 中。
        params = list(extra.pop("params", None) or ())
        # Processing is done with option callbacks instead of a group
        # callback. This allows users to make a custom group callback
        # without losing the behavior. --env-file must come first so
        # that it is eagerly evaluated before --app.
        # 将 _env_file_option、_app_option 和 _debug_option 这三个选项添加到 params 列表中。
        params.extend((_env_file_option, _app_option, _debug_option))

        # 如果 add_version_option 为 True，则将 version_option 添加到 params 列表中。
        if add_version_option:
            params.append(version_option)

        # 如果 extra 字典中没有 "context_settings" 键，则在 extra 中添加该键，并将其值设为空字典。
        if "context_settings" not in extra:
            extra["context_settings"] = {}

        # 在 extra 字典的 "context_settings" 键对应的字典中设置 "auto_envvar_prefix" 的默认值为 "FLASK"。
        extra["context_settings"].setdefault("auto_envvar_prefix", "FLASK")

        # 调用父类 AppGroup 的构造函数，并将 params 和任何额外的关键字参数传递给它。
        super().__init__(params=params, **extra)

        # 将构造函数接收的 create_app、load_dotenv 和 set_debug_flag 参数分别赋值给实例变量。
        self.create_app = create_app
        self.load_dotenv = load_dotenv
        self.set_debug_flag = set_debug_flag

        # 如果 add_default_commands 为 True，则向实例添加默认的 run、shell 和 routes 命令。
        if add_default_commands:
            self.add_command(run_command)
            self.add_command(shell_command)
            self.add_command(routes_command)

        # 初始化一个实例变量 _loaded_plugin_commands，并将其设为 False。
        # 这个变量可能用于跟踪插件命令是否已经被加载。
        self._loaded_plugin_commands = False


    # 为Flask应用加载插件命令。
     def _load_plugin_commands(self) -> None:
        # 检查 _loaded_plugin_commands 属性的值。如果这个值为 True，
        # 意味着插件命令已经加载过了，那么方法就直接返回，不再重复加载命令。
        if self._loaded_plugin_commands:
            return

        if sys.version_info >= (3, 10):
            from importlib import metadata
        else:
            # Use a backport on Python < 3.10. We technically have
            # importlib.metadata on 3.8+, but the API changed in 3.10,
            # so use the backport for consistency.
            import importlib_metadata as metadata

        # metadata.entry_points() 函数返回一个入口点集合，每个入口点代表了一个可加载的对象。
        # 对于每个入口点，使用 ep.load() 方法加载它表示的对象（通常是一个函数或类），
        # 然后调用 self.add_command() 方法将其添加为命令，命令的名称由 ep.name 提供。
        for ep in metadata.entry_points(group="flask.commands"):
            self.add_command(ep.load(), ep.name)

        # 将 _loaded_plugin_commands 属性设为 True，表示插件命令已经加载过了，避免将来的重复加载。
        self._loaded_plugin_commands = True


    # 用于在命令行接口 (CLI) 中查找命令。
    # ctx（click 库的 Context 对象，表示当前的命令行上下文）和 name（要查找的命令的名称）。
    # 方法返回 click.Command 对象或者在没有找到命令时返回 None。
    def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
        # 调用 _load_plugin_commands 方法来加载插件命令。
        # 这确保了在查找命令之前，所有的插件命令都已经被加载。
        self._load_plugin_commands()
        # Look up built-in and plugin commands, which should be
        # available even if the app fails to load.
        # 使用 super().get_command(ctx, name) 调用父类的 get_command 方法来查找内置和插件命令。
        # 如果找到了命令，rv 变量将包含该命令的引用。
        rv = super().get_command(ctx, name)

        # 如果在内置或插件命令中找到了指定的命令，方法将立即返回该命令。
        if rv is not None:
            return rv

        # 确保 ctx（上下文）中存在 ScriptInfo 对象，并将其赋值给变量 info。
        info = ctx.ensure_object(ScriptInfo)

        # 尝试使用 info.load_app() 方法加载 Flask 应用。如果应用无法加载
        #（通常是因为没有找到合适的 Flask 应用实例），会抛出 NoAppException 异常，并显示错误信息。
        # Look up commands provided by the app, showing an error and
        # continuing if the app couldn't be loaded.
        try:
            app = info.load_app()
        except NoAppException as e:
            click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")
            return None

        # Push an app context for the loaded app unless it is already
        # active somehow. This makes the context available to parameter
        # and command callbacks without needing @with_appcontext.
        # 如果当前没有激活的 Flask 应用上下文，或者当前激活的上下文不是我们刚加载的应用，
        # 那么使用 app.app_context() 创建一个新的应用上下文，并在 ctx 上下文中注册它。
        # 这使得命令和参数回调可以访问 Flask 应用的上下文而不需要使用 @with_appcontext 装饰器。
        if not current_app or current_app._get_current_object() is not app:  # type: ignore[attr-defined]
            ctx.with_resource(app.app_context())

        # 尝试在 Flask 应用提供的命令中查找指定的命令。如果找到了，返回该命令；否则，返回 None。
        return app.cli.get_command(ctx, name)


    # 定义在 Flask 应用的命令行接口中，用于列出所有可用的命令，
    # 包括内置命令、插件命令以及由 Flask 应用本身提供的命令。
    # 接收一个 click.Context 对象作为参数，并返回一个字符串列表，其中包含所有可用命令的名称。
    def list_commands(self, ctx: click.Context) -> list[str]:
        # 调用 _load_plugin_commands 方法来加载插件命令。
        # 这确保在列出命令之前，所有插件提供的命令都已加载。
        self._load_plugin_commands()
        # Start with the built-in and plugin commands.
        # 调用父类的 list_commands 方法来获取内置和插件命令的列表，
        # 并将这些命令名称存储在一个集合 rv 中，以去除重复项。
        rv = set(super().list_commands(ctx))
        # 确保上下文 ctx 中存在 ScriptInfo 对象，并将其赋给变量 info。
        # ScriptInfo 是 Flask CLI 中用来加载和存储应用相关信息的对象。
        info = ctx.ensure_object(ScriptInfo)

        # Add commands provided by the app, showing an error and
        # continuing if the app couldn't be loaded.
        # 尝试加载 Flask 应用并调用其 CLI 接口的 list_commands 方法来获取应用提供的命令列表，
        # 然后将这些命令添加到 rv 集合中。如果应用无法加载（抛出 NoAppException），
        # 则显示错误信息但不中断执行。
        try:
            rv.update(info.load_app().cli.list_commands(ctx))
        except NoAppException as e:
            # When an app couldn't be loaded, show the error message
            # without the traceback.
            click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")
        # 如果在加载应用或获取命令时发生了其他任何异常，捕获这个异常并显示完整的 traceback，帮助调试问题。
        except Exception:
            # When any other errors occurred during loading, show the
            # full traceback.
            click.secho(f"{traceback.format_exc()}\n", err=True, fg="red")

        # 将 rv 集合转换成列表，并对其进行排序以保证命令列表的顺序性，最后返回这个列表。
        return sorted(rv)

    # Flask CLI (命令行界面) 中的一部分，用于创建一个命令行上下文 (click.Context)。
    # 这个上下文对象在执行命令时提供了许多有用的信息和功能。
    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: click.Context | None = None,
        **extra: t.Any,
    ) -> click.Context:
        # Set a flag to tell app.run to become a no-op. If app.run was
        # not in a __name__ == __main__ guard, it would start the server
        # when importing, blocking whatever command is being called.
        # 设置环境变量 FLASK_RUN_FROM_CLI 为 "true"。这个标志告诉 Flask 应用在通过 CLI 启动时，
        # 即使应用的 run 方法没有被放在 if __name__ == "__main__" 守护下，也不会启动 Flask 开发服务器。
        # 这避免了在导入 Flask 应用时意外启动服务器，从而阻塞正在调用的命令。
        os.environ["FLASK_RUN_FROM_CLI"] = "true"

        # Attempt to load .env and .flask env files. The --env-file
        # option can cause another file to be loaded.
        if get_load_dotenv(self.load_dotenv):
            load_dotenv()

        # 如果在 extra 关键字参数或类的 context_settings 属性中没有指定 "obj"，
        # 则创建一个 ScriptInfo 实例并将其赋给 extra["obj"]。
        # ScriptInfo 是一个封装了 Flask 应用创建和其他设置的对象。
        # 这里，它被初始化了 create_app 和 set_debug_flag，这两个属性也是在类的构造函数中设置的。
        if "obj" not in extra and "obj" not in self.context_settings:
            extra["obj"] = ScriptInfo(
                create_app=self.create_app, set_debug_flag=self.set_debug_flag
            )

        # 调用父类的 make_context 方法，并传入所有接收到的参数和 extra 关键字参数。
        # 这个调用将创建并返回一个配置好的 click.Context 实例。
        return super().make_context(info_name, args, parent=parent, **extra)


    # Flask 应用的命令行接口（CLI）的一部分，用于解析传递给命令的参数。
    # 它接受一个 click.Context 对象和一个字符串列表 args 作为参数。
    # 这个方法的目的是解析这些参数，并返回解析后的参数列表。
    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        # 首先检查是否没有提供任何参数（args 列表为空），并且类属性 no_args_is_help 被设置为 True。
        # 如果这两个条件都满足，表示当没有提供任何参数时，应该显示帮助信息。
        if not args and self.no_args_is_help:
            # Attempt to load --env-file and --app early in case they
            # were given as env vars. Otherwise no_args_is_help will not
            # see commands from app.cli.
            # 通过调用 handle_parse_result 方法（传递空的参数和字典）来尝试提前处理这些选项，
            # 确保相关的环境变量或配置能够被正确地识别和应用。
            _env_file_option.handle_parse_result(ctx, {}, [])
            _app_option.handle_parse_result(ctx, {}, [])

        # 根据命令行中提供的参数和定义的命令行选项规则来解析参数。
        return super().parse_args(ctx, args)


# 用于检查一个文件路径是否是另一个路径的祖先。
# 这可以用于确定在文件系统中，一个目录是否包含另一个目录或文件。
# 这个函数在处理文件路径和目录结构时非常有用，特别是在需要确认文件或目录间的层级关系时。
def _path_is_ancestor(path: str, other: str) -> bool:
    """Take ``other`` and remove the length of ``path`` from it. Then join it
    to ``path``. If it is the original value, ``path`` is an ancestor of
    ``other``."""
    # other[len(path):]从other字符串中移除与path长度相同的前缀部分。
    # 通过 lstrip(os.sep) 移除结果字符串前面的任何路径分隔符。
    # os.path.join(path, ...) 将处理后的路径片段添加回 path 前面。
    # 如果处理和重组后的 other 路径与原始的 other 路径完全相同，
    # 那么意味着 path 确实是 other 的一个祖先路径，函数返回 True。
    return os.path.join(path, other[len(path) :].lstrip(os.sep)) == other


# 用于加载环境变量从 .env 或 .flaskenv 文件，它按照一定的顺序尝试读取这些文件，以设置环境变量。
# path 是一个可选参数，指定了一个具体的文件路径来加载，而不是按照默认的搜索顺序来查找。
# 它可以是字符串类型，或者是符合 os.PathLike 协议的对象。如果不提供 path，
# 函数会按照顺序查找 .env 和 .flaskenv 文件。
# 通过这个函数，开发者可以方便地管理和加载应用的配置，而无需硬编码在应用代码中，使配置更灵活、易于管理。
def load_dotenv(path: str | os.PathLike[str] | None = None) -> bool:
    """Load "dotenv" files in order of precedence to set environment variables.

    If an env var is already set it is not overwritten, so earlier files in the
    list are preferred over later files.

    This is a no-op if `python-dotenv`_ is not installed.

    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme

    :param path: Load the file at this location instead of searching.
    :return: ``True`` if a file was loaded.

    .. versionchanged:: 2.0
        The current directory is not changed to the location of the
        loaded file.

    .. versionchanged:: 2.0
        When loading the env files, set the default encoding to UTF-8.

    .. versionchanged:: 1.1.0
        Returns ``False`` when python-dotenv is not installed, or when
        the given path isn't a file.

    .. versionadded:: 1.0
    """
    try:
        # 首先尝试导入 dotenv 模块。
        import dotenv
    # 如果导入失败（ImportError），则表示 python-dotenv 库未安装。
    except ImportError:
        # 如果存在 .env 或 .flaskenv 文件，但 python-dotenv 未安装，会打印提示信息，
        # 建议安装 python-dotenv，并返回 False。
        if path or os.path.isfile(".env") or os.path.isfile(".flaskenv"):
            click.secho(
                " * Tip: There are .env or .flaskenv files present."
                ' Do "pip install python-dotenv" to use them.',
                fg="yellow",
                err=True,
            )

        return False

    # 如果 path 参数被指定且该路径指向的文件存在，函数会尝试仅加载这个文件，
    # 并立即返回结果。如果文件不存在，则返回 False。
    # Always return after attempting to load a given path, don't load
    # the default files.
    if path is not None:
        if os.path.isfile(path):
            return dotenv.load_dotenv(path, encoding="utf-8")

        return False

    loaded = False

    # 如果没有指定 path，函数会按顺序查找 .env 和 .flaskenv 文件。
    # 对于找到的每个文件，使用 UTF-8 编码加载它。
    # 如果至少加载了一个文件，loaded 变量会被设置为 True。
    for name in (".env", ".flaskenv"):
        path = dotenv.find_dotenv(name, usecwd=True)

        if not path:
            continue

        dotenv.load_dotenv(path, encoding="utf-8")
        loaded = True

    return loaded  # True if at least one file was located and loaded.


# 启动 Flask 服务器时显示启动信息。这些信息帮助开发者了解正在运行的应用和其调试状态。
def show_server_banner(debug: bool, app_import_path: str | None) -> None:
    """Show extra startup messages the first time the server is run,
    ignoring the reloader.
    """
    # 这行检查当前 Flask 应用是否由 Werkzeug 的 reloader 启动。
    # 如果是，函数立即返回，不显示任何启动信息。这是因为 reloader 会在代码改动时重启服务器，
    # 但我们只在第一次启动服务器时显示启动信息，避免在每次自动重启时都重复显示。
    if is_running_from_reloader():
        return

    # 使用 click.echo 打印出正在服务的 Flask 应用的名称。
    if app_import_path is not None:
        click.echo(f" * Serving Flask app '{app_import_path}'")

    # 打印出调试模式的状态。
    if debug is not None:
        click.echo(f" * Debug mode: {'on' if debug else 'off'}")


# 专门用于处理 Flask 应用中 --cert 命令行选项的参数。
# 通过自定义的转换逻辑，为 Flask 应用提供了灵活的 SSL 证书配置方式，
# 支持从文件、临时生成或程序导入的 SSL 上下文中选择。
class CertParamType(click.ParamType):
    """Click option type for the ``--cert`` option. Allows either an
    existing file, the string ``'adhoc'``, or an import for a
    :class:`~ssl.SSLContext` object.
    """

    name = "path"

    # 在类的初始化方法中，创建了一个 click.Path 实例，配置为只接受已存在的文件路径（不接受目录），
    # 并自动解析路径。这个 click.Path 实例用于后续验证文件路径参数。
    def __init__(self) -> None:
        self.path_type = click.Path(exists=True, dir_okay=False, resolve_path=True)

    # convert 方法，用于将命令行参数的值转换成期望的格式。
    def convert(
        self, value: t.Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> t.Any:
        try:
            import ssl
        except ImportError:
            # 提示用户该功能需要 Python 编译时支持 SSL。
            raise click.BadParameter(
                'Using "--cert" requires Python to be compiled with SSL support.',
                ctx,
                param,
            ) from None

        try:
            # 尝试使用前面创建的 click.Path 实例来验证和处理 value。
            return self.path_type(value, param, ctx)
        except click.BadParameter:
            # 将 value 转换为小写字符串，以便处理 'adhoc' 选项或 SSL 上下文对象的导入路径。
            value = click.STRING(value, param, ctx).lower()

            if value == "adhoc":
                try:
                    import cryptography  # noqa: F401
                except ImportError:
                    raise click.BadParameter(
                        "Using ad-hoc certificates requires the cryptography library.",
                        ctx,
                        param,
                    ) from None

                return value

            # 如果 value 不是 'adhoc'，尝试将其视为一个导入路径，并使用 import_string 函数尝试导入。
            obj = import_string(value, silent=True)

            # 如果成功导入，并且导入的对象是 ssl.SSLContext 类型，则返回这个对象。
            if isinstance(obj, ssl.SSLContext):
                return obj

            raise


# 用于验证 --key 命令行选项的值，并根据情况修改 --cert 参数的值，
# 确保 --key 和 --cert 选项的一致性和正确性。
# ctx 是 Click 上下文对象，param 是 Click 参数对象，value 是命令行选项传递的值。
def _validate_key(ctx: click.Context, param: click.Parameter, value: t.Any) -> t.Any:
    """The ``--key`` option must be specified when ``--cert`` is a file.
    Modifies the ``cert`` param to be a ``(cert, key)`` pair if needed.
    """
    # 获取 ctx 中 cert 参数的值。
    cert = ctx.params.get("cert")
    # 检查是否为临时证书 ("adhoc")。
    is_adhoc = cert == "adhoc"

    # 是否为 ssl.SSLContext 对象。如果未导入 ssl 模块（即 Python 没有 SSL 支持），
    # 将 is_context 设为 False。
    try:
        import ssl
    except ImportError:
        is_context = False
    else:
        is_context = isinstance(cert, ssl.SSLContext)

    # 如果 --key 选项的值不是 None，表示用户在命令行中提供了一个 --key 参数值。
    if value is not None:
        # 如果 --cert 是临时证书 ("adhoc")，则不允许使用 --key 选项，抛出异常。
        if is_adhoc:
            raise click.BadParameter(
                'When "--cert" is "adhoc", "--key" is not used.', ctx, param
            )

        # 如果 --cert 是一个 ssl.SSLContext 对象，则不允许使用 --key 选项，抛出异常。
        if is_context:
            raise click.BadParameter(
                'When "--cert" is an SSLContext object, "--key" is not used.',
                ctx,
                param,
            )

        # 如果没有提供 --cert 选项，也不允许提供 --key 选项，因此抛出异常。
        if not cert:
            raise click.BadParameter('"--cert" must also be specified.', ctx, param)

        # 如果以上验证都通过，则将 cert 参数修改为一个元组 (cert, key)。
        ctx.params["cert"] = cert, value

    # 如果 --key 选项的值为 None，即用户没有在命令行中提供 --key 参数值。
    else:
        # 如果提供了 --cert 参数，但没有提供 --key 参数，且 --cert 不是临时证书也不是
        # ssl.SSLContext 对象，则抛出异常，提示用户需要提供 --key 参数。
        if cert and not (is_adhoc or is_context):
            raise click.BadParameter('Required when using "--cert".', ctx, param)

    # 返回验证后的参数值。
    return value


# 允许接受由操作系统路径分隔符分隔的多个路径，并将它们转换为 Click 的路径类型。
class SeparatedPathType(click.Path):
    """Click option type that accepts a list of values separated by the
    OS's path separator (``:``, ``;`` on Windows). Each value is
    validated as a :class:`click.Path` type.
    """

    def convert(
        # value 是命令行中提供的参数值，param 是 Click 参数对象，ctx 是 Click 上下文对象。
        self, value: t.Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> t.Any:
        # 调用 split_envvar_value 方法，将输入的字符串值根据操作系统的路径分隔符进行分割，
        # 得到一个列表 items，其中包含分隔后的各个值。
        items = self.split_envvar_value(value)
        # can't call no-arg super() inside list comprehension until Python 3.12
        # 由于在 Python 中不能在列表推导式中调用无参数的 super()，因此将 super().convert 方法
        # 赋值给一个局部变量 super_convert，以在后面的列表推导式中使用。
        super_convert = super().convert
        # 使用列表推导式遍历 items 列表中的每个值，对每个值使用 super_convert 方法
        # （即 click.Path 类的 convert 方法）进行转换，并将转换后的值组成一个新的列表返回。
        return [super_convert(item, param, ctx) for item in items]














