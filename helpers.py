
# 启用未来的注解支持，使得类型注解更加灵活。
from __future__ import annotations

# importlib.util 和 os：用于动态加载配置文件或模块。
# datetime：用于处理时间戳或记录日志。
# lru_cache 和 update_wrapper：用于优化性能和装饰函数。
# werkzeug.utils 和 werkzeug.exceptions：用于处理 HTTP 重定向和错误响应。
# current_app 和 request：用于在视图函数中访问当前应用实例和请求对象。
# session：用于管理用户会话数据。
# message_flashed：用于发送和接收闪现消息信号。
# 用于导入和加载模块的工具。
import importlib.util
import os
import sys
# 用于类型注解。
import typing as t
from datetime import datetime
# 提供最近最少使用（LRU）缓存装饰器。
from functools import lru_cache
# 更新包装函数以更好地反映被包装的函数。
from functools import update_wrapper

# 导入 Werkzeug 实用工具模块。
import werkzeug.utils
# 用于终止请求并返回错误响应。
from werkzeug.exceptions import abort as _wz_abort
# 用于发起重定向响应。
from werkzeug.utils import redirect as _wz_redirect
# 用作基本响应类。
from werkzeug.wrappers import Response as BaseResponse

# 当前请求上下文变量。
from .globals import _cv_request
# 当前应用实例。
from .globals import current_app
# 当前请求对象。
from .globals import request
# 当前请求上下文。
from .globals import request_ctx
# 当前会话对象。
from .globals import session
# 消息闪现信号，用于在闪现消息时发出信号。
from .signals import message_flashed

# 仅在进行类型检查时执行此块中的导入，以避免在运行时引入不必要的依赖。
if t.TYPE_CHECKING:  # pragma: no cover
    from .wrappers import Response


# 用于获取应用是否应该启用调试模式。
# 获取是否应为应用启用调试模式，这由环境变量 FLASK_DEBUG 指定。默认值为 False。
def get_debug_flag() -> bool:
    """Get whether debug mode should be enabled for the app, indicated by the
    :envvar:`FLASK_DEBUG` environment variable. The default is ``False``.
    """
    # 从环境变量中获取 FLASK_DEBUG 的值。如果环境变量未设置，os.environ.get 会返回 None。
    val = os.environ.get("FLASK_DEBUG")
    # 如果 val 存在且不在 {"0", "false", "no"} 集合中，则返回 True，表示应启用调试模式。
    # 否则返回 False，表示不应启用调试模式。
    return bool(val and val.lower() not in {"0", "false", "no"})


# 用于确定是否加载默认的 .env 文件。
# 通过环境变量 FLASK_SKIP_DOTENV 来控制此行为，默认情况下是加载 .env 文件。
def get_load_dotenv(default: bool = True) -> bool:
    """Get whether the user has disabled loading default dotenv files by
    setting :envvar:`FLASK_SKIP_DOTENV`. The default is ``True``, load
    the files.

    :param default: What to return if the env var isn't set.
    """
    # 从环境变量中获取 FLASK_SKIP_DOTENV 的值。
    # 如果环境变量未设置，os.environ.get 会返回 None。
    val = os.environ.get("FLASK_SKIP_DOTENV")

    # 如果 val 为 None 或空字符串，返回 default 参数的值。
    if not val:
        return default

    # 如果环境变量 FLASK_SKIP_DOTENV 设置了值，将其转换为小写，
    # 并检查它是否在集合 ("0", "false", "no") 中。
    # 如果 val 在集合中，则返回 True，表示应加载 .env 文件。
    # 否则返回 False，表示不应加载 .env 文件。
    return val.lower() in ("0", "false", "no")













