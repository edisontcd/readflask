from __future__ import annotations

import typing as t

# 这些类和函数用于模板渲染。
from jinja2 import BaseLoader
from jinja2 import Environment as BaseEnvironment
from jinja2 import Template
from jinja2 import TemplateNotFound

# 用于管理应用和请求上下文的全局变量。
from .globals import _cv_app
from .globals import _cv_request
from .globals import current_app
from .globals import request

#用于处理流式响应的帮助函数。
from .helpers import stream_with_context

# 用于在模板渲染前后触发事件。
from .signals import before_render_template
from .signals import template_rendered

# 这部分代码仅在类型检查时执行，不会在运行时执行。
if t.TYPE_CHECKING:  # pragma: no cover
    from .app import Flask
    from .sansio.app import App
    from .sansio.scaffold import Scaffold


# 默认的模板上下文处理器。
# 它将 request、session 和 g 注入到模板上下文中。
# 通过这种方式，可以在模板中方便地访问和使用请求、会话和全局数据。
def _default_template_ctx_processor() -> dict[str, t.Any]:
    """Default template context processor.  Injects `request`,
    `session` and `g`.
    """
    # 获取当前的应用上下文。如果没有活动的应用上下文，则返回 None。
    appctx = _cv_app.get(None)
    # 获取当前的请求上下文。如果没有活动的请求上下文，则返回 None。
    reqctx = _cv_request.get(None)
    # 初始化一个空字典，用于存储将要注入到模板上下文中的变量。
    rv: dict[str, t.Any] = {}
    # 如果存在活动的应用上下文，则将 g 注入到返回值字典中。
    # g 是一个特殊对象，用于在请求过程中存储和共享数据。
    if appctx is not None:
        rv["g"] = appctx.g
    # 如果存在活动的请求上下文，则将 request 和 session 注入到返回值字典中。
    # request 是当前的请求对象，包含有关当前 HTTP 请求的信息。
    # session 是当前会话对象，允许在多个请求之间存储用户数据。
    if reqctx is not None:
        rv["request"] = reqctx.request
        rv["session"] = reqctx.session
    # 返回包含 g、request 和 session 的字典。
    return rv


# 扩展了基本的 Jinja2 环境，使得它可以更好地与 Flask 的蓝图（Blueprint）一起工作。
class Environment(BaseEnvironment):
    """Works like a regular Jinja2 environment but has some additional
    knowledge of how Flask's blueprint works so that it can prepend the
    name of the blueprint to referenced templates if necessary.
    """

    # 用于初始化 Environment 类的实例。
    # app: App：这是一个 Flask 应用的实例，用于配置和操作 Jinja2 环境。扩展了基本的 Jinja2 环境，使得它可以更好地与 Flask 的蓝图（Blueprint）一起工作。
    def __init__(self, app: App, **options: t.Any) -> None:
        # 检查是否在 options 参数中提供了 loader，如果没有，
        # 则使用 app.create_global_jinja_loader() 方法创建一个全局的 Jinja2 加载器。
        if "loader" not in options:
            options["loader"] = app.create_global_jinja_loader()
        # 初始化基类 BaseEnvironment。
        BaseEnvironment.__init__(self, **options)
        # 将 app 实例保存在 self.app 属性中，以便在类的其他方法中使用。
        self.app = app


# 扩展了 Jinja2 的 BaseLoader，使其能够从 Flask 应用及其蓝图中加载模板。
class DispatchingJinjaLoader(BaseLoader):
    """A loader that looks for templates in the application and all
    the blueprint folders.
    """

    # 构造方法。
    def __init__(self, app: App) -> None:
        self.app = app

    # 获取模板源代码的方法。
    def get_source(
        # environment：类型为 BaseEnvironment，表示 Jinja2 环境。
        # template：类型为 str，表示模板的名称。
        self, environment: BaseEnvironment, template: str
    # 返回一个元组，包含模板的源代码、模板的路径和一个布尔值函数。
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        # 根据是否配置 EXPLAIN_TEMPLATE_LOADING，选择调用不同方法。
        if self.app.config["EXPLAIN_TEMPLATE_LOADING"]:
            return self._get_source_explained(environment, template)
        return self._get_source_fast(environment, template)

    # 用于详细解释模板加载过程中的每次尝试，并记录这些尝试以便调试。
    # 详细记录加载过程，便于调试和问题诊断，适用于开发和调试阶段。
    def _get_source_explained(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        # 用于记录每次尝试加载模板的结果。
        attempts = []
        # 用于存储每次尝试加载模板的返回值。
        rv: tuple[str, str | None, t.Callable[[], bool] | None] | None
        # 用于存储第一次成功加载模板的返回值。
        trv: None | (tuple[str, str | None, t.Callable[[], bool] | None]) = None

        # 使用 _iter_loaders 方法遍历所有可能的加载器。
        for srcobj, loader in self._iter_loaders(template):
            try:
                # 如果成功加载，并且 trv 尚未设置，则将其设置为当前返回值 rv。
                rv = loader.get_source(environment, template)
                if trv is None:
                    trv = rv
            # 如果加载失败，捕获 TemplateNotFound 异常，并将 rv 设置为 None。
            except TemplateNotFound:
                rv = None
            # 将每次尝试的结果（包括加载器、源对象和返回值）添加到 attempts 列表中。
            attempts.append((loader, srcobj, rv))

        from .debughelpers import explain_template_loading_attempts

        explain_template_loading_attempts(self.app, template, attempts)

        # 如果 trv 不为 None，表示至少有一次成功加载模板，返回 trv。
        if trv is not None:
            return trv
        # 如果 trv 为 None，表示所有尝试都失败了，抛出 TemplateNotFound 异常。
        raise TemplateNotFound(template)

    # 快速加载模板，并在模板加载失败时提供友好的错误处理。
    # 不记录详细信息，适用于生产环境。
    def _get_source_fast(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        # 使用 _iter_loaders 方法遍历所有可能的加载器。
        for _srcobj, loader in self._iter_loaders(template):
            try:
                # 如果成功加载模板，则立即返回模板的源代码、模板路径和布尔值函数。
                return loader.get_source(environment, template)
            # 如果加载失败并抛出 TemplateNotFound 异常，则继续尝试下一个加载器。
            except TemplateNotFound:
                continue
        # 如果所有加载器都未能成功加载模板，则抛出 TemplateNotFound 异常。
        raise TemplateNotFound(template)

    # 通过生成器模式遍历所有可能的模板加载器，包括应用级加载器和所有蓝图级加载器。
    # 返回一个迭代器，其元素是一个元组，包含 Scaffold 和 BaseLoader。
    def _iter_loaders(self, template: str) -> t.Iterator[tuple[Scaffold, BaseLoader]]:
        # 获取应用级的 Jinja 加载器（self.app.jinja_loader）。
        loader = self.app.jinja_loader
        # 如果加载器存在，则将应用实例和加载器作为元组 yield。
        if loader is not None:
            yield self.app, loader

        # 对于每个蓝图，获取其 Jinja 加载器（blueprint.jinja_loader）。
        for blueprint in self.app.iter_blueprints():
            loader = blueprint.jinja_loader
            # 如果加载器存在，则将蓝图实例和加载器作为元组 yield。
            if loader is not None:
                yield blueprint, loader

    # 列出应用及其所有蓝图中的所有模板。
    def list_templates(self) -> list[str]:
        # 创建一个空的 set 对象，用于存储模板名称。
        result = set()
        # 获取应用级的 Jinja 加载器。
        loader = self.app.jinja_loader
        # 如果加载器存在，则调用其 list_templates 方法，获取所有模板名称，
        # 并将其添加到 result 集合中。
        if loader is not None:
            result.update(loader.list_templates())

        # 遍历应用中的所有蓝图。
        for blueprint in self.app.iter_blueprints():
            # 对于每个蓝图，获取其 Jinja 加载器。
            loader = blueprint.jinja_loader
            # 如果加载器存在，则调用其 list_templates 方法，获取所有模板名称，
            # 并将其逐个添加到 result 集合中。
            if loader is not None:
                for template in loader.list_templates():
                    result.add(template)

        # 将结果集合转换为列表并返回。
        return list(result)


# 用于渲染模板，并在渲染之前和之后发送相应的信号。
# context：类型为 dict[str, t.Any]，表示用于渲染模板的上下文数据。
# 返回值类型：返回渲染后的字符串。
def _render(app: Flask, template: Template, context: dict[str, t.Any]) -> str:
    # 调用 Flask 应用的 update_template_context 方法，更新模板上下文。
    # 这个方法通常会向上下文中添加一些全局变量，比如 request、session 和 g。
    app.update_template_context(context)
    # 发送 before_render_template 信号。在模板渲染之前触发，用于执行一些预处理操作。
    # 传递的参数包括 Flask 应用实例、模板实例和上下文数据。
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    # 调用模板实例的 render 方法，使用上下文数据渲染模板。
    rv = template.render(context)
    # 发送 template_rendered 信号。在模板渲染之后触发，用于执行一些后处理操作。
    template_rendered.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    return 


# Flask 中用于渲染模板的关键方法。它通过获取当前应用实例，根据传入的模板名称
# 或模板对象（或列表）获取模板，并调用 _render 方法渲染模板，最终返回渲染后的字符串。
def render_template(
    # template_name_or_list：类型为 str、Template 或者它们的列表，
    # 表示要渲染的模板名称或模板对象。如果传入的是列表，则渲染第一个存在的模板。
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
) -> str:
    """Render a template by name with the given context.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.
    """
    # 获取当前的 Flask 应用实例。
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    # 调用应用实例的 Jinja 环境的 get_or_select_template 方法，
    # 根据传入的模板名称或模板对象（或列表）获取模板。
    # 如果传入的是列表，则返回第一个存在的模板。
    template = app.jinja_env.get_or_select_template(template_name_or_list)
    return _render(app, template, context)

# 比较 render_template 和 render_template_string
# render_template：从文件或模板对象加载模板。常用于静态模板文件。
# render_template_string：从字符串加载模板。常用于动态生成的模板内容。

# 用于从字符串渲染模板的关键方法。它通过获取当前应用实例，根据传入的模板源代码字符串
# 创建模板对象，并调用 _render 方法渲染模板，最终返回渲染后的字符串。
# 这个方法使得开发者可以方便地从字符串渲染模板，特别适用于动态生成的模板内容。
# source：类型为 str，表示模板的源代码字符串。
# context：上下文数据，将作为模板中的变量使用。
def render_template_string(source: str, **context: t.Any) -> str:
    """Render a template from the given source string with the given
    context.

    :param source: The source code of the template to render.
    :param context: The variables to make available in the template.
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    # 调用应用实例的 Jinja 环境的 from_string 方法，根据传入的模板源代码字符串创建模板对象。
    template = app.jinja_env.from_string(source)
    return _render(app, template, context)


# 用于流式渲染模板，即逐步生成模板内容并将其发送给客户端，而不是一次性渲染整个模板。
# 这对于处理大数据量或长时间生成的内容非常有用，因为它可以在生成内容的同时将其传输给客户端，
# 而无需等待整个内容生成完成。
def _stream(
    # app：类型为 Flask，表示 Flask 应用实例。
    # template：类型为 Template，表示 Jinja2 模板实例。
    # context：类型为 dict[str, t.Any]，表示用于渲染模板的上下文数据。
    app: Flask, template: Template, context: dict[str, t.Any]
    # 返回值类型：返回一个字符串迭代器。
) -> t.Iterator[str]:
    # 调用 Flask 应用的 update_template_context 方法，更新模板上下文。
    # 这个方法通常会向上下文中添加一些全局变量，比如 request、session 和 g。
    app.update_template_context(context)
    # 发送 before_render_template 信号。在模板渲染之前触发，用于执行一些预处理操作。
    # 传递的参数包括 Flask 应用实例、模板实例和上下文数据。
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )

    # 定义内部生成器函数 generate，用于逐步生成模板内容。
    def generate() -> t.Iterator[str]:
        # 从模板的 generate 方法生成内容。
        yield from template.generate(context)
        # 生成完成后，发送 template_rendered 信号，用于执行一些后处理操作。
        template_rendered.send(
            app, _async_wrapper=app.ensure_sync, template=template, context=context
        )

    # 调用生成器函数 generate，获取生成器对象 rv。
    rv = generate()

    # 如果当前存在请求上下文（即正在处理 HTTP 请求），则使用 stream_with_context 方法包装生成器对象 rv。
    # If a request context is active, keep it while generating.
    if request:
        rv = stream_with_context(rv)

    # 返回生成器对象 rv。
    return rv


# 用于流式渲染模板，并返回一个字符串迭代器。
# stream_template 方法与 render_template 类似，但它生成的是一个字符串迭代器，
# 而不是一次性生成整个渲染后的字符串。这使得它非常适合在处理大数据量或长时间生成内容时，
# 逐步将生成的内容发送给客户端，提高响应的及时性和性能。
def stream_template(
    # 类型为 str、Template 或者它们的列表，表示要渲染的模板名称或模板对象。
    # 如果传入的是列表，则渲染第一个存在的模板。
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
    # 返回一个字符串迭代器。
) -> t.Iterator[str]:
    """Render a template by name with the given context as a stream.
    This returns an iterator of strings, which can be used as a
    streaming response from a view.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.

    .. versionadded:: 2.2
    """
    # 使用 current_app._get_current_object() 获取当前的 Flask 应用实例。
    # current_app 是一个代理对象，通过 _get_current_object() 方法获取实际的应用实例。
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    # 调用应用实例的 Jinja 环境的 get_or_select_template 方法，
    # 根据传入的模板名称或模板对象（或列表）获取模板。
    # 如果传入的是列表，则返回第一个存在的模板。
    template = app.jinja_env.get_or_select_template(template_name_or_list)
    # 调用 _stream 方法，传入应用实例、模板对象和上下文数据，返回一个生成模板内容的字符串迭代器。
    return _stream(app, template, context)


# 用于从给定的模板源代码字符串和上下文数据中生成模板，并返回一个字符串迭代器。
# 这可以用于在视图中生成流式响应，逐步将内容发送给客户端，而不是一次性生成和发送整个内容。
# 这个方法适用于处理大数据量或长时间生成的内容，特别是当模板内容是动态生成的字符串时。
def stream_template_string(source: str, **context: t.Any) -> t.Iterator[str]:
    """Render a template from the given source string with the given
    context as a stream. This returns an iterator of strings, which can
    be used as a streaming response from a view.

    :param source: The source code of the template to render.
    :param context: The variables to make available in the template.

    .. versionadded:: 2.2
    """
    # 获取当前的 Flask 应用实例。
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    # 调用应用实例的 Jinja 环境的 from_string 方法，根据传入的模板源代码字符串创建模板对象。
    template = app.jinja_env.from_string(source)
    # 调用 _stream 方法，传入应用实例、模板对象和上下文数据，返回一个生成模板内容的字符串迭代器。
    return _stream(app, template, context)

