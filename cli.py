# 它从 Python 3.7 开始引入，用于提供更好的类型提示功能。
from __future__ import annotations

# Python 中的一个内置模块，用于处理抽象语法树（Abstract Syntax Trees）
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

    # 
    # Search for app factory functions.
    for attr_name in ("create_app", "make_app"):

        # getattr 是 Python 内置函数，用于从对象中获取指定属性的值。
        # 从给定的模块 module 中获取属性名为 attr_name 的属性值，如果属性不存在，则返回 None。
        app_factory = getattr(module, attr_name, None)

        # 从模块中的工厂函数中找到并返回一个有效的 Flask 实例，或者在找不到有效实例时引发异常。
        if inspect.isfunction(app_factory):
            try:
                app = app_factory()

                if isinstance(app, Flask):
                    return app
            except TypeError as e:
                if not _called_with_wrong_args(app_factory):
                    raise

                # 在检测到模块中存在工厂函数，但是尝试调用它时出现了 TypeError 异常
                #（即没有传递所需的参数），于是抛出 NoAppException 异常。
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
















