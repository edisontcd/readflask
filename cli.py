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






















