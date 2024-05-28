# 可以在注释中使用类和类型定义，而不必担心这些类和类型是否在当前作用域内。
from __future__ import annotations

# 以别名t导入typing模块，该模块用于支持类型提示，有助于静态类型检查和文档化代码。
import typing as t

# 导入 BaseLoader 类，这个类是 Jinja2 模板引擎中的一个基础加载器类。
from jinja2.loaders import BaseLoader
# 导入 RequestRedirect 异常，这个异常在请求需要重定向时使用。
from werkzeug.routing import RequestRedirect

# 导入 Blueprint 类，这个类用于定义和管理 Flask 蓝图（Blueprints），
# 蓝图是一种组织代码的方式，可以让你将应用分解为更小的可复用模块。
from .blueprints import Blueprint
# 导入 request_ctx，这个对象用于全局跟踪请求上下文。
from .globals import request_ctx
# 导入 App 类，这个类可能是一个不依赖于输入输出的应用类，通常用于测试或其他场景下。
from .sansio.app import App

# 仅在类型检查时执行（例如使用 mypy 进行静态类型检查时）。
# 在运行时，这些导入不会实际执行，从而避免了不必要的依赖。
if t.TYPE_CHECKING:
    from .sansio.scaffold import Scaffold
    from .wrappers import Request


# 一个自定义异常类，用于处理意外的 Unicode 或二进制数据，
# 通过继承 AssertionError 和 UnicodeError 提供更好的错误报告和语义。
# 它可以用于各种数据验证和清理操作中，帮助开发者快速识别和处理数据格式问题。
class UnexpectedUnicodeError(AssertionError, UnicodeError):
    """Raised in places where we want some better error reporting for
    unexpected unicode or binary data.
    """

# 自定义异常类，用于在调试时处理 request.files 中的键错误。
# 它继承了 KeyError 和 AssertionError，提供了详细的错误信息，
# 帮助开发者更好地理解和解决文件上传相关的问题。
class DebugFilesKeyError(KeyError, AssertionError):
    """Raised from request.files during debugging.  The idea is that it can
    provide a better error message than just a generic KeyError/BadRequest.
    """

    # request 是当前的请求对象。key 是尝试访问但不存在的文件键。
    def __init__(self, request: Request, key: str) -> None:
        form_matches = request.form.getlist(key)
        # 从请求的表单数据中获取与 key 匹配的所有值，存储在 form_matches 列表中。
        buf = [
            # 解释请求的 files 字典中不存在键 key。
            # 指出请求的 MIME 类型 request.mimetype 不是 multipart/form-data，
            # 这意味着没有传输文件内容。
            # 提供修复建议，指出应该在表单中使用 enctype="multipart/form-data"。
            f"You tried to access the file {key!r} in the request.files"
            " dictionary but it does not exist. The mimetype for the"
            f" request is {request.mimetype!r} instead of"
            " 'multipart/form-data' which means that no file contents"
            " were transmitted. To fix this error you should provide"
            ' enctype="multipart/form-data" in your form.'
        ]
        # 如果表单数据中存在与 key 匹配的值，则添加额外的信息到 buf 中，
        # 指出浏览器提交了一些文件名，并显示这些文件名。
        if form_matches:
            names = ", ".join(repr(x) for x in form_matches)
            buf.append(
                "\n\nThe browser instead transmitted some file names. "
                f"This was submitted: {names}"
            )
        # 将缓冲区 buf 中的所有字符串连接起来，形成最终的错误消息，并存储在实例变量 self.msg 中。
        self.msg = "".join(buf)

    # 当尝试将异常对象转换为字符串时返回 self.msg，即返回完整的错误消息。
    def __str__(self) -> str:
        return self.msg

































