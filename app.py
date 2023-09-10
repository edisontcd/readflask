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