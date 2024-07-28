from __future__ import annotations

# 从 blinker 库导入 Namespace 类，blinker 是一个支持信号的库。
from blinker import Namespace

# 创建一个新的 Namespace 实例，用于存放 Flask 本身提供的信号。
# 信号是一种在应用中不同部分之间传递消息的机制。
# 使用下划线前缀表示这是一个内部使用的命名空间。
# This namespace is only for signals provided by Flask itself.
_signals = Namespace()

# 当模板渲染完成时发出信号。
template_rendered = _signals.signal("template-rendered")
# 在渲染模板之前发出信号。
before_render_template = _signals.signal("before-render-template")
# 请求开始时发出信号。
request_started = _signals.signal("request-started")
# 请求完成时发出信号。
request_finished = _signals.signal("request-finished")
# 请求结束时（通常用于清理）发出信号。
request_tearing_down = _signals.signal("request-tearing-down")
# 处理请求时出现异常时发出信号。
got_request_exception = _signals.signal("got-request-exception")
# 应用上下文结束时发出信号。
appcontext_tearing_down = _signals.signal("appcontext-tearing-down")
# 应用上下文被推送时发出信号。
appcontext_pushed = _signals.signal("appcontext-pushed")
# 应用上下文被弹出时发出信号。
appcontext_popped = _signals.signal("appcontext-popped")
# 消息闪现时发出信号（通常用于在下一个请求中显示）。
message_flashed = _signals.signal("message-flashed")