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


# 用于在调试模式下处理可能导致请求方法或请求体丢失的路由重定向情况。
# 通过提供详细的错误信息和建议，这个异常类帮助开发者更好地理解和解决表单数据丢失的问题。
# AssertionError 是当断言语句失败时抛出的异常。使用它作为基类意味着这个异常主要用于调试和开发阶段。
class FormDataRoutingRedirect(AssertionError):
    """This exception is raised in debug mode if a routing redirect
    would cause the browser to drop the method or body. This happens
    when method is not GET, HEAD or OPTIONS and the status code is not
    307 or 308.
    """

    def __init__(self, request: Request) -> None:
        # 从请求对象中获取路由异常 exc，并断言它是 RequestRedirect 类型。
        exc = request.routing_exception
        assert isinstance(exc, RequestRedirect)
        # 创建一个消息缓冲区 buf，包含请求的 URL 和重定向的目标 URL。
        buf = [
            f"A request was sent to '{request.url}', but routing issued"
            f" a redirect to the canonical URL '{exc.new_url}'."
        ]

        # 如果重定向的目标 URL 与请求的基础 URL 加上尾随斜杠匹配，则添加相关解释到消息缓冲区。
        if f"{request.base_url}/" == exc.new_url.partition("?")[0]:
            buf.append(
                " The URL was defined with a trailing slash. Flask"
                " will redirect to the URL with a trailing slash if it"
                " was accessed without one."
            )

        # 添加建议部分，说明应发送请求到规范 URL，或使用 307 或 308 状态码进行路由重定向，
        # 以避免浏览器丢失表单数据。
        buf.append(
            " Send requests to the canonical URL, or use 307 or 308 for"
            " routing redirects. Otherwise, browsers will drop form"
            " data.\n\n"
            "This exception is only raised in debug mode."
        )
        # 调用父类 AssertionError 的初始化方法，将构建的错误消息传递给父类。
        super().__init__("".join(buf))


# 通过修改 request.files 对象的行为，增强了错误处理的能力。
# 当试图访问 request.files 中不存在的键时，它会检查该键是否存在于 request.form 中，
# 如果存在，则抛出一个自定义的 DebugFilesKeyError，提供更详细的错误信息。
def attach_enctype_error_multidict(request: Request) -> None:
    """Patch ``request.files.__getitem__`` to raise a descriptive error
    about ``enctype=multipart/form-data``.

    :param request: The request to patch.
    :meta private:
    """
    # 保存 request.files 的当前类，以便在新类中继承它的行为。
    oldcls = request.files.__class__

    # 定义一个新的类 newcls，继承自 oldcls。
    class newcls(oldcls):  # type: ignore[valid-type, misc]
        # 重写 __getitem__ 方法，当尝试访问 request.files 中的键时执行。
        def __getitem__(self, key: str) -> t.Any:
            # 尝试使用父类的方法访问键 key。
            try:
                return super().__getitem__(key)
            # 如果捕获到 KeyError 异常，并且该键不在 request.form 中，重新抛出异常。
            except KeyError as e:
                if key not in request.form:
                    raise

                # 如果该键在 request.form 中，抛出自定义的 DebugFilesKeyError 异常，
                # 并附加原始异常的回溯信息。
                raise DebugFilesKeyError(request, key).with_traceback(
                    e.__traceback__
                ) from None

    # 复制旧类的 __name__ 和 __module__ 属性到新类，以保持类的名称和模块信息一致。
    newcls.__name__ = oldcls.__name__
    newcls.__module__ = oldcls.__module__
    # 将 request.files 的类替换为新定义的类 newcls。
    request.files.__class__ = newcls


# 遍历 BaseLoader 对象的属性，并生成描述其类型和公开属性的字符串。
# 它跳过私有属性和复杂类型的属性，只处理字符串、数值和布尔值，以及由字符串组成的元组或列表。
# loader：一个 BaseLoader 对象，表示 Jinja2 模板引擎的加载器。
# 返回一个字符串迭代器，逐行生成加载器的信息。
def _dump_loader_info(loader: BaseLoader) -> t.Iterator[str]:
    # 生成一行字符串，描述加载器对象的类及其所在的模块。
    yield f"class: {type(loader).__module__}.{type(loader).__name__}"
    # 遍历 loader 对象的属性字典 (__dict__)，并按键排序。key 表示属性名，value 表示属性值。
    for key, value in sorted(loader.__dict__.items()):
        # 如果属性名以下划线 _ 开头，跳过该属性。这通常表示私有属性，不需要包含在转储信息中。
        if key.startswith("_"):
            continue
        # 如果属性值是元组或列表，检查其元素是否全是字符串。
        if isinstance(value, (tuple, list)):
            # 如果不是，跳过该属性。
            if not all(isinstance(x, str) for x in value):
                continue
            # 生成属性名，并对其每个元素生成一行带缩进的字符串。
            yield f"{key}:"
            for item in value:
                yield f"  - {item}"
            continue
        # 如果属性值不是字符串、整数、浮点数或布尔值，则跳过该属性。
        elif not isinstance(value, (str, int, float, bool)):
            continue
        # 对于基本类型的属性，生成一行字符串，包含属性名和属性值（使用 !r 以获得值的正式表示形式）。
        yield f"{key}: {value!r}"


# 通过详细记录每次加载模板的尝试，帮助开发者理解为什么模板加载失败或成功。
# 它提供了有关加载器、源对象和匹配结果的详细信息，并在必要时提供额外的提示。
# 这些信息对于调试和解决模板加载问题非常有用。
def explain_template_loading_attempts(
    app: App,
    # 要加载的模板的名称。
    template: str,
    # 一个包含所有加载模板尝试的信息的列表。每个尝试包含一个加载器（BaseLoader）、
    # 一个源对象（Scaffold，可以是 App 或 Blueprint），以及一个三元组（如果没有找到匹配，则为 None）。
    attempts: list[
        tuple[
            BaseLoader,
            Scaffold,
            tuple[str, str | None, t.Callable[[], bool] | None] | None,
        ]
    ],
) -> None:
    """This should help developers understand what failed"""
    # 初始化信息列表 info，包含一个模板定位的起始信息。
    info = [f"Locating template {template!r}:"]
    # 初始化 total_found 计数器，用于记录找到的模板数量。
    total_found = 0
    blueprint = None
    # 检查当前请求上下文中是否有蓝图，如果有则获取蓝图名称。
    if request_ctx and request_ctx.request.blueprint is not None:
        blueprint = request_ctx.request.blueprint

    # 遍历每个加载尝试，获取加载器、源对象和三元组。
    for idx, (loader, srcobj, triple) in enumerate(attempts):
        # 如果是 App 对象，显示应用信息。
        if isinstance(srcobj, App):
            src_info = f"application {srcobj.import_name!r}"
        # 如果是 Blueprint 对象，显示蓝图信息。
        elif isinstance(srcobj, Blueprint):
            src_info = f"blueprint {srcobj.name!r} ({srcobj.import_name})"
        # 否则，显示源对象的字符串表示。
        else:
            src_info = repr(srcobj)

        # 记录当前加载器的类型信息。
        info.append(f"{idx + 1:5}: trying loader of {src_info}")

        # 使用 _dump_loader_info 函数生成加载器的详细信息。
        for line in _dump_loader_info(loader):
            info.append(f"       {line}")

        # 如果三元组为 None，记录没有匹配的信息。
        if triple is None:
            detail = "no match"
        # 否则，记录找到的模板信息并增加计数器。
        else:
            detail = f"found ({triple[1] or '<string>'!r})"
            total_found += 1
        info.append(f"       -> {detail}")

    # 根据找到的模板数量，记录错误或警告信息：
    seems_fishy = False
    # 如果没有找到模板，记录错误信息。
    if total_found == 0:
        info.append("Error: the template could not be found.")
        seems_fishy = True
    # 如果找到多个匹配的模板，记录警告信息。
    elif total_found > 1:
        info.append("Warning: multiple loaders returned a match for the template.")
        seems_fishy = True

    # 如果当前请求来自蓝图，并且有错误或警告信息，提供额外的提示，
    # 指出模板可能放置在错误的文件夹中，并提供链接以获取更多信息。
    if blueprint is not None and seems_fishy:
        info.append(
            "  The template was looked up from an endpoint that belongs"
            f" to the blueprint {blueprint!r}."
        )
        info.append("  Maybe you did not place a template in the right folder?")
        info.append("  See https://flask.palletsprojects.com/blueprints/#templates")

    # 将生成的所有信息记录到应用的日志中。
    app.logger.info("\n".join(info))

