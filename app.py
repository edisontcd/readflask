from __future__ import annotations

# os模块负责程序与操作系统的交互，提供了访问操作系统底层的接口。
import os

# sys模块负责程序与python解释器的交互，提供了一系列的函数和变量，
# 用于操控python的运行时环境。
import sys

# 对类型提示的支持
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

# types定义了一些工具函数，用于协助动态创建新的类型。Traceback异常处理.
from types import TracebackType

# urllib.parse用于将统一资源定位符（URL）字符串拆分为不同部分（协议、网络位置、路径等），
# 或将各个部分组合回 URL 字符串。quote使用 %xx 转义符替换 string 中的特殊字符。
from urllib.parse import quote as _url_quote

# 创建命令行界面 (CLI) 应用程序的 Python 库
import click

# Python的WSGI规范的实用函数库
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableDict
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError
from werkzeug.routing import BuildError
from werkzeug.routing import MapAdapter
from werkzeug.routing import RequestRedirect
from werkzeug.routing import RoutingException
from werkzeug.routing import Rule
from werkzeug.serving import is_running_from_reloader
from werkzeug.wrappers import Response as BaseResponse

# 命令行应用
from . import cli

# 为框架的 API 提供类型提示，以提高代码的可读性、可维护性，并支持类型检查工具的使用。
from . import typing as ft

# 实现保存上下文所需的对象
from .ctx import AppContext
from .ctx import RequestContext












