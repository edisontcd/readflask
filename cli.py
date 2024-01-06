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


















