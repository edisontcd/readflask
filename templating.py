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












