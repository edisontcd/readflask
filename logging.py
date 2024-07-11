from __future__ import annotations

import logging
import sys
import typing as t

from werkzeug.local import LocalProxy

from .globals import request

if t.TYPE_CHECKING:  # pragma: no cover
    from .sansio.app import App


# 根据当前上下文返回最合适的错误流。
# @LocalProxy 装饰器将 wsgi_errors_stream 函数包装成一个代理对象。
# 当访问该代理对象时，会动态调用 wsgi_errors_stream 函数。
@LocalProxy
def wsgi_errors_stream() -> t.TextIO: # 返回一个文本 I/O 流对象。
    # 为应用程序找到最合适的错误流。如果有活动的请求，则日志记录到 wsgi.errors，
    # 否则使用 sys.stderr。
    """Find the most appropriate error stream for the application. If a request
    is active, log to ``wsgi.errors``, otherwise use ``sys.stderr``.

    If you configure your own :class:`logging.StreamHandler`, you may want to
    use this for the stream. If you are using file or dict configuration and
    can't import this directly, you can refer to it as
    ``ext://flask.logging.wsgi_errors_stream``.
    """
    # 检查 request 对象是否存在。如果存在，则从请求环境中获取 wsgi.errors 错误流并返回。
    if request:
        return request.environ["wsgi.errors"]  # type: ignore[no-any-return]

    # 如果没有活动的请求，返回标准错误流 sys.stderr。
    return sys.stderr


# 检查日志记录器链中是否有处理器处理给定日志记录器的有效日志级别。
# 更灵活和方便地管理日志记录，确保日志消息被正确处理和记录。
def has_level_handler(logger: logging.Logger) -> bool:
    # 参数：logger，类型为 logging.Logger，表示要检查的日志记录器。
    """Check if there is a handler in the logging chain that will handle the
    given logger's :meth:`effective level <~logging.Logger.getEffectiveLevel>`.
    """
    # 获取给定日志记录器的有效日志级别。
    level = logger.getEffectiveLevel()
    # 初始化 current 为给定日志记录器。
    current = logger

    # 使用 while 循环遍历日志记录器链。
    while current:
        # 在当前日志记录器的处理器中检查是否存在处理器的日志级别小于或等于日志记录器的有效日志级别。
        if any(handler.level <= level for handler in current.handlers):
            return True

        # 如果日志记录器不进行传播，退出循环。
        if not current.propagate:
            break

        # 否则，移动到父日志记录器。
        current = current.parent  # type: ignore

    return False


#: Log messages to :func:`~flask.logging.wsgi_errors_stream` with the format
#: ``[%(asctime)s] %(levelname)s in %(module)s: %(message)s``.
# 它是一个 logging.StreamHandler，用于将日志消息记录到 wsgi_errors_stream。
default_handler = logging.StreamHandler(wsgi_errors_stream)  # type: ignore
# 设置日志格式。
default_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
)


# 用于获取和配置 Flask 应用的日志记录器。
def create_logger(app: App) -> logging.Logger: # 返回一个配置好的日志记录器。
    """Get the Flask app's logger and configure it if needed.

    # 日志记录器的名称将与应用的导入名称相同。
    The logger name will be the same as
    :attr:`app.import_name <flask.Flask.name>`.

    # 当 Flask 应用的调试模式启用时，如果日志记录器的级别未设置，
    # 则将其级别设置为 logging.DEBUG。
    When :attr:`~flask.Flask.debug` is enabled, set the logger level to
    :data:`logging.DEBUG` if it is not set.

    If there is no handler for the logger's effective level, add a
    :class:`~logging.StreamHandler` for
    :func:`~flask.logging.wsgi_errors_stream` with a basic format.
    """
    # 获取或创建一个名为应用导入名称的日志记录器。
    logger = logging.getLogger(app.name)

    # 检查应用的 debug 属性是否为 True，并且日志记录器的级别是否未设置（即 logger.level 为 0）。
    # 如果条件满足，将日志记录器的级别设置为 logging.DEBUG。
    if app.debug and not logger.level:
        logger.setLevel(logging.DEBUG)

    # 使用前面定义的 has_level_handler 函数检查日志记录器链中是否存在处理其有效级别的处理器。
    if not has_level_handler(logger):
        # 如果没有合适的处理器，添加一个默认的 StreamHandler，将日志记录到 wsgi_errors_stream。
        logger.addHandler(default_handler)

    # 返回配置好的日志记录器。
    return logger


