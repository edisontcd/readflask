# 它从 Python 3.7 开始引入，用于提供更好的类型提示功能。
from __future__ import annotations

# Python 标准库中的一个模块，用于访问有关安装的包和模块元数据的信息。
import importlib.metadata

# typing 模块是 Python 3.5 及更高版本引入的一个标准库模块，
# 用于支持类型提示和类型注解，以提高代码的可读性和可维护性。
import typing as t

# contextlib 模块是 Python 标准库中的一个模块，用于支持上下文管理器的创建和使用。
# contextmanager 类是一个装饰器，用于定义一个生成器函数，该生成器函数可以生成上下文管理器。
from contextlib import contextmanager
# ExitStack 类是一个上下文管理器，它用于管理多个上下文管理器。
from contextlib import ExitStack

# copy 函数用于创建对象的浅拷贝。当修改原始列表的嵌套列表时，浅拷贝后的列表也会受到影响。
from copy import copy

# types定义了一些工具函数，用于协助动态创建新的类型。
# TracebackType 是 Python 的内置类型之一，用于表示异常的回溯信息（traceback）。
from types import TracebackType

# urlsplit 函数用于解析 URL（Uniform Resource Locator）字符串，
# 并将其拆分为不同的组成部分，如协议、域名、路径、查询参数和片段等。
from urllib.parse import urlsplit

# 用于测试和模拟 HTTP 请求和响应，以便测试 Web 应用程序的行为和功能。
import werkzeug.test

# CliRunner 类的主要作用是模拟命令行应用程序的运行，并允许你以编程方式发送命令、
# 模拟用户输入以及捕获应用程序的输出，从而进行单元测试和集成测试。
from click.testing import CliRunner

# Client 类的主要作用是允许你以编程方式构建 HTTP 请求，发送它们到你的 Web 应用程序，
# 然后检查和处理应用程序的响应。
from werkzeug.test import Client

# Request允许你轻松地访问请求的各个部分，并从中提取数据以处理和响应客户端请求。
from werkzeug.wrappers import Request as BaseRequest

from .cli import ScriptInfo
from .sessions import SessionMixin

if t.TYPE_CHECKING:  # pragma: no cover
    from werkzeug.test import TestResponse

    from .app import Flask









    
