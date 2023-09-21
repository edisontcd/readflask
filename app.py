# 它从 Python 3.7 开始引入，用于提供更好的类型提示功能。
from __future__ import annotations

# os模块负责程序与操作系统的交互，提供了访问操作系统底层的接口。
import os

# sys模块负责程序与python解释器的交互，提供了一系列的函数和变量，
# 用于操控python的运行时环境。
import sys

# typing 模块是 Python 3.5 及更高版本引入的一个标准库模块，
# 用于支持类型提示和类型注解，以提高代码的可读性和可维护性。
import typing as t

# 弱引用的主要用途是实现保存大对象的高速缓存或映射，
# 但又不希望大对象仅仅因为它出现在高速缓存或映射中而保持存活。
import weakref

# 容器的抽象基类
from collections.abc import Iterator as _abc_Iterator

# datetime基本日期和时间类型
# timedelta表示两个 date 对象或 time 对象，或者 datetime 对象之间的时间间隔，精确到微秒。
from datetime import timedelta

# inspect4种主要的功能: 类型检查、获取源代码、检查类与函数、检查解释器的调用堆栈。
# iscoroutinefunction: 如果对象是协程函数（使用 async def 语法定义的函数），则返回 True。
from inspect import iscoroutinefunction

# 创建一个迭代器，它首先返回第一个可迭代对象中所有元素，接着返回下一个可迭代对象中所有元素，
# 直到耗尽所有可迭代对象中的元素。可将多个序列处理为单个序列。
from itertools import chain

# types定义了一些工具函数，用于协助动态创建新的类型。
# TracebackType 是 Python 的内置类型之一，用于表示异常的回溯信息（traceback）。
from types import TracebackType

# urllib.parse用于将统一资源定位符（URL）字符串拆分为不同部分（协议、网络位置、路径等），
# 或将各个部分组合回 URL 字符串。quote使用 %xx 转义符替换 string 中的特殊字符。
from urllib.parse import quote as _url_quote

# 创建命令行界面 (CLI) 应用程序的 Python 库
import click

# Python的WSGI规范的实用函数库
# 创建、修改和处理 HTTP 请求或响应的头部信息。
from werkzeug.datastructures import Headers
# 表示一个不可变的字典，即一旦创建，就无法更改其内容。
from werkzeug.datastructures import ImmutableDict
# 通常用于表示客户端请求中的键错误或缺失。
from werkzeug.exceptions import BadRequestKeyError
# 用于表示 HTTP 协议相关的异常情况，例如客户端错误（4xx 错误）
# 和服务器错误（5xx 错误）等。
from werkzeug.exceptions import HTTPException
# 用于表示服务器内部错误的情况。
from werkzeug.exceptions import InternalServerError
# 用于处理 URL 构建错误的情况。
from werkzeug.routing import BuildError
# 用于执行 URL 到视图函数的映射，以及从视图函数生成 URL。
# 它允许你动态地构建 URL 和路由请求，以便与 Web 应用程序的路由系统进行交互。
from werkzeug.routing import MapAdapter
# 用于表示请求需要重定向到另一个 URL 的情况。
from werkzeug.routing import RequestRedirect
# 用于表示与 URL 路由相关的异常情况。
from werkzeug.routing import RoutingException
# 定义 URL 路由规则。
from werkzeug.routing import Rule
# 监视脚本文件的更改，并在文件更改时自动重新启动应用程序，
# 以便开发人员可以在不停止服务器的情况下进行代码修改和调试。
from werkzeug.serving import is_running_from_reloader
# 构建 HTTP 响应对象。
from werkzeug.wrappers import Response as BaseResponse

# 命令行应用
from . import cli

# 为框架的 API 提供类型提示，以提高代码的可读性、可维护性，并支持类型检查工具的使用。
from . import typing as ft

# 实现保存上下文所需的对象
from .ctx import AppContext
from .ctx import RequestContext














