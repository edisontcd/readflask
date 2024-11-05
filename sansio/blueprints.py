from __future__ import annotations

import os
import typing as t
# 一个字典子类，提供默认值功能。
from collections import defaultdict
# 用于更新装饰器的元数据，使其与被装饰的函数一致。
from functools import update_wrapper

from .. import typing as ft
from .scaffold import _endpoint_from_view_func
from .scaffold import _sentinel
from .scaffold import Scaffold
from .scaffold import setupmethod

# 这个块中的代码只在类型检查时有效，通常用于避免运行时导入。
if t.TYPE_CHECKING:  # pragma: no cover
    from .app import App

# 示一个接受 BlueprintSetupState 类型参数并返回 None 的可调用对象。
DeferredSetupFunction = t.Callable[["BlueprintSetupState"], None]
# 绑定到 ft.AfterRequestCallable 类型，表示可以接受任何类型的请求处理函数。
T_after_request = t.TypeVar("T_after_request", bound=ft.AfterRequestCallable[t.Any])
# 表示一个在请求之前调用的函数类型。
T_before_request = t.TypeVar("T_before_request", bound=ft.BeforeRequestCallable)
# 表示一个处理错误的函数类型。
T_error_handler = t.TypeVar("T_error_handler", bound=ft.ErrorHandlerCallable)
# 表示一个在请求结束时调用的函数类型。
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
# 表示一个用于处理模板上下文的函数类型。
T_template_context_processor = t.TypeVar(
    "T_template_context_processor", bound=ft.TemplateContextProcessorCallable
)
# 表示一个模板过滤器的函数类型。
T_template_filter = t.TypeVar("T_template_filter", bound=ft.TemplateFilterCallable)
# 表示一个全局模板变量的函数类型。
T_template_global = t.TypeVar("T_template_global", bound=ft.TemplateGlobalCallable)
# 表示一个用于模板测试的函数类型。
T_template_test = t.TypeVar("T_template_test", bound=ft.TemplateTestCallable)
# 表示一个用于 URL 默认值的函数类型。
T_url_defaults = t.TypeVar("T_url_defaults", bound=ft.URLDefaultCallable)
# 表示一个用于 URL 值预处理的函数类型。
T_url_value_preprocessor = t.TypeVar(
    "T_url_value_preprocessor", bound=ft.URLValuePreprocessorCallable
)


# 用于在将蓝图注册到 Flask 应用程序时临时存储相关状态。
class BlueprintSetupState:
    """Temporary holder object for registering a blueprint with the
    application.  An instance of this class is created by the
    :meth:`~flask.Blueprint.make_setup_state` method and later passed
    to all register callback functions.
    """

    # 构造函数。
    def __init__(
        self,
        blueprint: Blueprint,
        app: App,
        options: t.Any,
        # 布尔值，表示这是否是第一次注册该蓝图。
        first_registration: bool,
    ) -> None:
        # 将传入的应用程序引用赋值给实例属性 app。
        #: a reference to the current application
        self.app = app

        # 将传入的蓝图对象赋值给实例属性 blueprint。
        #: a reference to the blueprint that created this setup state.
        self.blueprint = blueprint

        #: a dictionary with all options that were passed to the
        #: :meth:`~flask.Flask.register_blueprint` method.
        # 将传入的选项字典赋值给实例属性 options。
        self.options = options

        # 将 first_registration 参数赋值给实例属性，表示蓝图是否首次注册。
        #: as blueprints can be registered multiple times with the
        #: application and not everything wants to be registered
        #: multiple times on it, this attribute can be used to figure
        #: out if the blueprint was registered in the past already.
        self.first_registration = first_registration

        # 尝试从 options 中获取子域名，如果未提供，则使用蓝图的默认子域名。
        subdomain = self.options.get("subdomain")
        if subdomain is None:
            subdomain = self.blueprint.subdomain

        # 将最终的子域名赋值给实例属性 subdomain。
        #: The subdomain that the blueprint should be active for, ``None``
        #: otherwise.
        self.subdomain = subdomain

        # 尝试从 options 中获取 URL 前缀，如果未提供，则使用蓝图的默认前缀。
        url_prefix = self.options.get("url_prefix")
        if url_prefix is None:
            url_prefix = self.blueprint.url_prefix
        #: The prefix that should be used for all URLs defined on the
        #: blueprint.
        # 将最终的 URL 前缀赋值给实例属性 url_prefix。
        self.url_prefix = url_prefix

        # 从 options 中获取蓝图的名称和名称前缀，如果未提供，则使用蓝图的默认值。
        self.name = self.options.get("name", blueprint.name)
        self.name_prefix = self.options.get("name_prefix", "")

        # 初始化一个字典 url_defaults，将蓝图的 URL 默认值复制到该字典中，
        # 并合并从 options 中提供的任何额外默认值。
        #: A dictionary with URL defaults that is added to each and every
        #: URL that was defined with the blueprint.
        self.url_defaults = dict(self.blueprint.url_values_defaults)
        self.url_defaults.update(self.options.get("url_defaults", ()))

    # 用于注册一个 URL 规则。
    def add_url_rule(
        self,
        # 要注册的 URL 规则字符串。
        rule: str,
        # 可选的端点名称。
        endpoint: str | None = None,
        # 关联的视图函数。
        view_func: ft.RouteCallable | None = None,
        **options: t.Any,
    ) -> None:
        """A helper method to register a rule (and optionally a view function)
        to the application.  The endpoint is automatically prefixed with the
        blueprint's name.
        """
        # 如果设置了 URL 前缀，则根据前缀和规则构建完整的 URL 规则。确保前缀和规则的斜杠正确处理。
        if self.url_prefix is not None:
            if rule:
                rule = "/".join((self.url_prefix.rstrip("/"), rule.lstrip("/")))
            else:
                rule = self.url_prefix
        # 确保在 options 中包含子域名选项，如果未提供，则使用当前实例的子域名。
        options.setdefault("subdomain", self.subdomain)
        # 如果未提供端点名称，则通过视图函数生成端点名称。
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)  # type: ignore
        # 初始化默认值，合并 options 中的任何额外默认值。
        defaults = self.url_defaults
        if "defaults" in options:
            defaults = dict(defaults, **options.pop("defaults"))

        # 通过应用程序的 add_url_rule 方法将构建的规则和相关参数注册到 Flask 应用中，
        # 端点名称会被自动加上蓝图的前缀。
        self.app.add_url_rule(
            rule,
            f"{self.name_prefix}.{self.name}.{endpoint}".lstrip("."),
            view_func,
            defaults=defaults,
            **options,
        )


# 展示了蓝图如何在 Flask 应用中组织路由、视图函数和其他功能，
# 使得开发者可以更清晰地管理和模块化他们的代码。
class Blueprint(Scaffold):
    """Represents a blueprint, a collection of routes and other
    app-related functions that can be registered on a real application
    later.

    A blueprint is an object that allows defining application functions
    without requiring an application object ahead of time. It uses the
    same decorators as :class:`~flask.Flask`, but defers the need for an
    application by recording them for later registration.

    Decorating a function with a blueprint creates a deferred function
    that is called with :class:`~flask.blueprints.BlueprintSetupState`
    when the blueprint is registered on an application.

    See :doc:`/blueprints` for more information.

    :param name: The name of the blueprint. Will be prepended to each
        endpoint name.
    :param import_name: The name of the blueprint package, usually
        ``__name__``. This helps locate the ``root_path`` for the
        blueprint.
    :param static_folder: A folder with static files that should be
        served by the blueprint's static route. The path is relative to
        the blueprint's root path. Blueprint static files are disabled
        by default.
    :param static_url_path: The url to serve static files from.
        Defaults to ``static_folder``. If the blueprint does not have
        a ``url_prefix``, the app's static route will take precedence,
        and the blueprint's static files won't be accessible.
    :param template_folder: A folder with templates that should be added
        to the app's template search path. The path is relative to the
        blueprint's root path. Blueprint templates are disabled by
        default. Blueprint templates have a lower precedence than those
        in the app's templates folder.
    :param url_prefix: A path to prepend to all of the blueprint's URLs,
        to make them distinct from the rest of the app's routes.
    :param subdomain: A subdomain that blueprint routes will match on by
        default.
    :param url_defaults: A dict of default values that blueprint routes
        will receive by default.
    :param root_path: By default, the blueprint will automatically set
        this based on ``import_name``. In certain situations this
        automatic detection can fail, so the path can be specified
        manually instead.

    .. versionchanged:: 1.1.0
        Blueprints have a ``cli`` group to register nested CLI commands.
        The ``cli_group`` parameter controls the name of the group under
        the ``flask`` command.

    .. versionadded:: 0.7
    """

    # 这是一个类属性，用于跟踪蓝图是否已经被注册过。
    _got_registered_once = False

    # 
    def __init__(
        self,
        # 蓝图的名称。
        name: str,
        # 蓝图所在包的名称，通常是 __name__。
        import_name: str,
        # 用于设置静态文件夹。
        static_folder: str | os.PathLike[str] | None = None,
        static_url_path: str | None = None,
        # 模板文件夹。
        template_folder: str | os.PathLike[str] | None = None,
        # URL 前缀。
        url_prefix: str | None = None,
        subdomain: str | None = None,
        # URL 默认值
        url_defaults: dict[str, t.Any] | None = None,
        root_path: str | None = None,
        cli_group: str | None = _sentinel,  # type: ignore[assignment]
    ):
        # 用于初始化父类（Scaffold），并传递特定的参数。
        super().__init__(
            # 蓝图包的名称（通常设置为 __name__）。它帮助 Flask 定位与蓝图相关的资源。
            import_name=import_name,
            # 指定存放蓝图静态文件（如 CSS、JS、图片）的文件夹。该路径是相对于蓝图根路径的。
            static_folder=static_folder,
            # 定义从中提供静态文件的 URL 路径。如果未指定，它默认为 static_folder 路径。
            static_url_path=static_url_path,
            # 指示该蓝图特定的模板存放位置。
            template_folder=template_folder,
            # 这是蓝图根目录的绝对路径。
            root_path=root_path,
        )

        # 检查名称是否为空，若为空则抛出错误。
        if not name:
            raise ValueError("'name' may not be empty.")

        # 检查名称中是否包含点号，若有则抛出错误。
        if "." in name:
            raise ValueError("'name' may not contain a dot '.' character.")

        # 初始化蓝图的各个属性。
        self.name = name
        self.url_prefix = url_prefix
        self.subdomain = subdomain
        self.deferred_functions: list[DeferredSetupFunction] = []

        # 如果未提供 URL 默认值，则初始化为空字典。
        if url_defaults is None:
            url_defaults = {}

        # 用于存储蓝图路由的默认值。
        self.url_values_defaults = url_defaults
        # 用于定义与该蓝图关联的命令行接口（CLI）组的名称。
        self.cli_group = cli_group
        # 该列表用于存储注册到该蓝图下的其他蓝图及其选项。
        self._blueprints: list[tuple[Blueprint, dict[str, t.Any]]] = []

    # 用于检查蓝图的设置是否已经完成。
    def _check_setup_finished(self, f_name: str) -> None:
        if self._got_registered_once:
            raise AssertionError(
                f"The setup method '{f_name}' can no longer be called on the blueprint"
                f" '{self.name}'. It has already been registered at least once, any"
                " changes will not be applied consistently.\n"
                "Make sure all imports, decorators, functions, etc. needed to set up"
                " the blueprint are done before registering it."
            )

    # 用于注册在蓝图注册到应用程序时要执行的回调函数。
    # 装饰器，标识该方法是用于蓝图设置的，可以在蓝图注册之前被调用。
    @setupmethod
    # 注册一个函数，当蓝图被注册到应用程序时会被调用。
    def record(self, func: DeferredSetupFunction) -> None:
        """Registers a function that is called when the blueprint is
        registered on the application.  This function is called with the
        state as argument as returned by the :meth:`make_setup_state`
        method.
        """
        # 将传入的函数 func 添加到 self.deferred_functions 列表中，以便在注册时调用。
        self.deferred_functions.append(func)

    @setupmethod
    # 类似于 record 方法，但它确保传入的函数只在蓝图第一次注册时被调用。
    # 如果蓝图第二次注册，该函数将不会被调用。
    def record_once(self, func: DeferredSetupFunction) -> None:
        """Works like :meth:`record` but wraps the function in another
        function that will ensure the function is only called once.  If the
        blueprint is registered a second time on the application, the
        function passed is not called.
        """

        # 
        def wrapper(state: BlueprintSetupState) -> None:
            # 只有在第一次注册时才调用传入的函数 func。
            if state.first_registration:
                func(state)

        # 使用 update_wrapper 更新 wrapper 的属性，并将其注册到 deferred_functions 列表中。
        self.record(update_wrapper(wrapper, func))

    # 创建一个 BlueprintSetupState 实例，并将其用于蓝图的注册回调函数。
    # 在蓝图注册时准备必要的状态信息，确保在注册过程中可以访问到蓝图本身、
    # 应用程序上下文以及其他配置选项。
    def make_setup_state(
        self, app: App, options: dict[str, t.Any], first_registration: bool = False
    ) -> BlueprintSetupState:
        """Creates an instance of :meth:`~flask.blueprints.BlueprintSetupState`
        object that is later passed to the register callback functions.
        Subclasses can override this to return a subclass of the setup state.
        """
        return BlueprintSetupState(self, app, options, first_registration)

    # 用于在当前蓝图上注册一个子蓝图。
    # 开发者可以更灵活地组织路由和视图，同时使用选项覆盖默认设置来满足特定需求。
    @setupmethod
    def register_blueprint(self, blueprint: Blueprint, **options: t.Any) -> None:
        """Register a :class:`~flask.Blueprint` on this blueprint. Keyword
        arguments passed to this method will override the defaults set
        on the blueprint.

        .. versionchanged:: 2.0.1
            The ``name`` option can be used to change the (pre-dotted)
            name the blueprint is registered with. This allows the same
            blueprint to be registered multiple times with unique names
            for ``url_for``.

        .. versionadded:: 2.0
        """
        if blueprint is self:
            raise ValueError("Cannot register a blueprint on itself")
        self._blueprints.append((blueprint, options))

    # 用于将当前蓝图注册到 Flask 应用中，并且处理一些与蓝图相关的配置、URL 路由、CLI 命令等。
    # 它在 Flask.register_blueprint 方法中被调用。
    def register(self, app: App, options: dict[str, t.Any]) -> None:
        """Called by :meth:`Flask.register_blueprint` to register all
        views and callbacks registered on the blueprint with the
        application. Creates a :class:`.BlueprintSetupState` and calls
        each :meth:`record` callback with it.

        :param app: The application this blueprint is being registered
            with.
        :param options: Keyword arguments forwarded from
            :meth:`~Flask.register_blueprint`.

        .. versionchanged:: 2.3
            Nested blueprints now correctly apply subdomains.

        .. versionchanged:: 2.1
            Registering the same blueprint with the same name multiple
            times is an error.

        .. versionchanged:: 2.0.1
            Nested blueprints are registered with their dotted name.
            This allows different blueprints with the same name to be
            nested at different locations.

        .. versionchanged:: 2.0.1
            The ``name`` option can be used to change the (pre-dotted)
            name the blueprint is registered with. This allows the same
            blueprint to be registered multiple times with unique names
            for ``url_for``.
        """
        # name_prefix 是从 options 获取的，而 self_name 是蓝图本身的名称。
        # 最终形成的 name 是蓝图的完整注册名称。
        name_prefix = options.get("name_prefix", "")
        self_name = options.get("name", self.name)
        name = f"{name_prefix}.{self_name}".lstrip(".")

        # 如果蓝图的名称已经在应用中注册，抛出 ValueError 异常，提示蓝图名称冲突。
        if name in app.blueprints:
            bp_desc = "this" if app.blueprints[name] is self else "a different"
            existing_at = f" '{name}'" if self_name != name else ""

            raise ValueError(
                f"The name '{self_name}' is already registered for"
                f" {bp_desc} blueprint{existing_at}. Use 'name=' to"
                f" provide a unique name."
            )

        # 表示蓝图是否是第一次注册到应用。
        first_bp_registration = not any(bp is self for bp in app.blueprints.values())
        # 表示蓝图的名称是否是第一次注册。
        first_name_registration = name not in app.blueprints

        # 将蓝图添加到应用的 blueprints 字典中。
        app.blueprints[name] = self
        # 标记为已注册。
        self._got_registered_once = True
        state = self.make_setup_state(app, options, first_bp_registration)

        # 如果蓝图具有静态文件夹，则为静态文件夹创建 URL 规则，允许 Flask 应用访问该蓝图的静态资源。
        if self.has_static_folder:
            state.add_url_rule(
                f"{self.static_url_path}/<path:filename>",
                view_func=self.send_static_file,  # type: ignore[attr-defined]
                endpoint="static",
            )

        # 如果蓝图是第一次注册，或者第一次注册该名称的蓝图，
        # 则会合并父蓝图的函数（例如视图函数和路由规则）。
        # Merge blueprint data into parent.
        if first_bp_registration or first_name_registration:
            self._merge_blueprint_funcs(app, name)

        # 执行所有延迟注册的回调函数，确保它们在蓝图注册后被正确执行。
        for deferred in self.deferred_functions:
            deferred(state)

        # 如果蓝图定义了 CLI 命令，则根据配置的 cli_group 将其注册到 Flask 应用的 CLI 中。
        cli_resolved_group = options.get("cli_group", self.cli_group)

        if self.cli.commands:
            if cli_resolved_group is None:
                app.cli.commands.update(self.cli.commands)
            elif cli_resolved_group is _sentinel:
                self.cli.name = name
                app.cli.add_command(self.cli)
            else:
                self.cli.name = cli_resolved_group
                app.cli.add_command(self.cli)

        # 遍历当前蓝图的所有嵌套蓝图（即子蓝图），并为每个子蓝图配置 URL 前缀、子域等信息，
        # 最终递归调用 register 方法注册它们。
        for blueprint, bp_options in self._blueprints:
            bp_options = bp_options.copy()
            bp_url_prefix = bp_options.get("url_prefix")
            bp_subdomain = bp_options.get("subdomain")

            if bp_subdomain is None:
                bp_subdomain = blueprint.subdomain

            if state.subdomain is not None and bp_subdomain is not None:
                bp_options["subdomain"] = bp_subdomain + "." + state.subdomain
            elif bp_subdomain is not None:
                bp_options["subdomain"] = bp_subdomain
            elif state.subdomain is not None:
                bp_options["subdomain"] = state.subdomain

            if bp_url_prefix is None:
                bp_url_prefix = blueprint.url_prefix

            if state.url_prefix is not None and bp_url_prefix is not None:
                bp_options["url_prefix"] = (
                    state.url_prefix.rstrip("/") + "/" + bp_url_prefix.lstrip("/")
                )
            elif bp_url_prefix is not None:
                bp_options["url_prefix"] = bp_url_prefix
            elif state.url_prefix is not None:
                bp_options["url_prefix"] = state.url_prefix

            bp_options["name_prefix"] = name
            blueprint.register(app, bp_options)


    # 将当前蓝图的各种设置（如错误处理、视图函数、请求钩子等）合并到 Flask 应用中。
    # self 是蓝图实例，app 是应用实例，name 是当前蓝图的名称。
    def _merge_blueprint_funcs(self, app: App, name: str) -> None:
        # 将蓝图的某些字典（如请求钩子、上下文处理器等）合并到应用中。
        def extend(
            # 蓝图中的字典，包含需要合并的值。键是 AppOrBlueprintKey，值是列表类型的函数。
            bp_dict: dict[ft.AppOrBlueprintKey, list[t.Any]],
            # 应用中的目标字典，蓝图的值将被添加到这个字典中。
            parent_dict: dict[ft.AppOrBlueprintKey, list[t.Any]],
        ) -> None:
            # 遍历蓝图字典中的每个键值对。
            for key, values in bp_dict.items():
                # 如果 key 为 None（即空值），则将 key 设置为蓝图的 name。
                # 如果 key 不为 None，则给它加上蓝图的名称前缀 name，
                # 形成如 blueprint_name.some_key 的结构。
                key = name if key is None else f"{name}.{key}"
                # 将蓝图中的 values（通常是函数或回调）添加到应用中的 parent_dict 中，合并到目标字典。
                parent_dict[key].extend(values)

        # 遍历蓝图的错误处理器字典 error_handler_spec。
        # 其中 key 是错误码（如 404），value 是与之对应的处理函数。
        for key, value in self.error_handler_spec.items():
            # 如果 key 是 None，则将其设置为蓝图的名称；否则，给 key 添加蓝图名称作为前缀，
            # 形成如 blueprint_name.404 的结构。
            key = name if key is None else f"{name}.{key}"
            # 将原有的错误处理器 value 转换为 defaultdict，确保如果没有指定处理函数时，
            # 字典会返回一个空的字典。
            value = defaultdict(
                dict,
                {
                    code: {exc_class: func for exc_class, func in code_values.items()}
                    for code, code_values in value.items()
                },
            )
            # 将修改后的错误处理器字典 value 注册到应用的 error_handler_spec 中，
            # 确保应用能够正确处理错误。
            app.error_handler_spec[key] = value

        # 遍历蓝图的 view_functions 字典，其中 endpoint 是路由的名称，func 是对应的视图函数。
        for endpoint, func in self.view_functions.items():
            # 将蓝图中的视图函数添加到应用的 view_functions 字典中。
            app.view_functions[endpoint] = func

        # 蓝图中注册的 before_request 钩子。
        extend(self.before_request_funcs, app.before_request_funcs)
        # 蓝图中注册的 after_request 钩子。
        extend(self.after_request_funcs, app.after_request_funcs)
        # 蓝图中注册的 teardown_request 钩子。
        extend(
            self.teardown_request_funcs,
            app.teardown_request_funcs,
        )
        # 蓝图中注册的 URL 默认函数。
        extend(self.url_default_functions, app.url_default_functions)
        # 蓝图中注册的 URL 值预处理函数。
        extend(self.url_value_preprocessors, app.url_value_preprocessors)
        # 蓝图中注册的模板上下文处理器。
        extend(self.template_context_processors, app.template_context_processors)

    @setupmethod
    def add_url_rule(
        self,
        rule: str,
        endpoint: str | None = None,
        view_func: ft.RouteCallable | None = None,
        provide_automatic_options: bool | None = None,
        **options: t.Any,
    ) -> None:
        """Register a URL rule with the blueprint. See :meth:`.Flask.add_url_rule` for
        full documentation.

        The URL rule is prefixed with the blueprint's URL prefix. The endpoint name,
        used with :func:`url_for`, is prefixed with the blueprint's name.
        """
        if endpoint and "." in endpoint:
            raise ValueError("'endpoint' may not contain a dot '.' character.")

        if view_func and hasattr(view_func, "__name__") and "." in view_func.__name__:
            raise ValueError("'view_func' name may not contain a dot '.' character.")

        self.record(
            lambda s: s.add_url_rule(
                rule,
                endpoint,
                view_func,
                provide_automatic_options=provide_automatic_options,
                **options,
            )
        )

    @setupmethod
    def app_template_filter(
        self, name: str | None = None
    ) -> t.Callable[[T_template_filter], T_template_filter]:
        """Register a template filter, available in any template rendered by the
        application. Equivalent to :meth:`.Flask.template_filter`.

        :param name: the optional name of the filter, otherwise the
                     function name will be used.
        """

        def decorator(f: T_template_filter) -> T_template_filter:
            self.add_app_template_filter(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_filter(
        self, f: ft.TemplateFilterCallable, name: str | None = None
    ) -> None:
        """Register a template filter, available in any template rendered by the
        application. Works like the :meth:`app_template_filter` decorator. Equivalent to
        :meth:`.Flask.add_template_filter`.

        :param name: the optional name of the filter, otherwise the
                     function name will be used.
        """

        def register_template(state: BlueprintSetupState) -> None:
            state.app.jinja_env.filters[name or f.__name__] = f

        self.record_once(register_template)

    @setupmethod
    def app_template_test(
        self, name: str | None = None
    ) -> t.Callable[[T_template_test], T_template_test]:
        """Register a template test, available in any template rendered by the
        application. Equivalent to :meth:`.Flask.template_test`.

        .. versionadded:: 0.10

        :param name: the optional name of the test, otherwise the
                     function name will be used.
        """

        def decorator(f: T_template_test) -> T_template_test:
            self.add_app_template_test(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_test(
        self, f: ft.TemplateTestCallable, name: str | None = None
    ) -> None:
        """Register a template test, available in any template rendered by the
        application. Works like the :meth:`app_template_test` decorator. Equivalent to
        :meth:`.Flask.add_template_test`.

        .. versionadded:: 0.10

        :param name: the optional name of the test, otherwise the
                     function name will be used.
        """

        def register_template(state: BlueprintSetupState) -> None:
            state.app.jinja_env.tests[name or f.__name__] = f

        self.record_once(register_template)

    @setupmethod
    def app_template_global(
        self, name: str | None = None
    ) -> t.Callable[[T_template_global], T_template_global]:
        """Register a template global, available in any template rendered by the
        application. Equivalent to :meth:`.Flask.template_global`.

        .. versionadded:: 0.10

        :param name: the optional name of the global, otherwise the
                     function name will be used.
        """

        def decorator(f: T_template_global) -> T_template_global:
            self.add_app_template_global(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_global(
        self, f: ft.TemplateGlobalCallable, name: str | None = None
    ) -> None:
        """Register a template global, available in any template rendered by the
        application. Works like the :meth:`app_template_global` decorator. Equivalent to
        :meth:`.Flask.add_template_global`.

        .. versionadded:: 0.10

        :param name: the optional name of the global, otherwise the
                     function name will be used.
        """

        def register_template(state: BlueprintSetupState) -> None:
            state.app.jinja_env.globals[name or f.__name__] = f

        self.record_once(register_template)

    @setupmethod
    def before_app_request(self, f: T_before_request) -> T_before_request:
        """Like :meth:`before_request`, but before every request, not only those handled
        by the blueprint. Equivalent to :meth:`.Flask.before_request`.
        """
        self.record_once(
            lambda s: s.app.before_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def after_app_request(self, f: T_after_request) -> T_after_request:
        """Like :meth:`after_request`, but after every request, not only those handled
        by the blueprint. Equivalent to :meth:`.Flask.after_request`.
        """
        self.record_once(
            lambda s: s.app.after_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def teardown_app_request(self, f: T_teardown) -> T_teardown:
        """Like :meth:`teardown_request`, but after every request, not only those
        handled by the blueprint. Equivalent to :meth:`.Flask.teardown_request`.
        """
        self.record_once(
            lambda s: s.app.teardown_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_context_processor(
        self, f: T_template_context_processor
    ) -> T_template_context_processor:
        """Like :meth:`context_processor`, but for templates rendered by every view, not
        only by the blueprint. Equivalent to :meth:`.Flask.context_processor`.
        """
        self.record_once(
            lambda s: s.app.template_context_processors.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_errorhandler(
        self, code: type[Exception] | int
    ) -> t.Callable[[T_error_handler], T_error_handler]:
        """Like :meth:`errorhandler`, but for every request, not only those handled by
        the blueprint. Equivalent to :meth:`.Flask.errorhandler`.
        """

        def decorator(f: T_error_handler) -> T_error_handler:
            def from_blueprint(state: BlueprintSetupState) -> None:
                state.app.errorhandler(code)(f)

            self.record_once(from_blueprint)
            return f

        return decorator

    @setupmethod
    def app_url_value_preprocessor(
        self, f: T_url_value_preprocessor
    ) -> T_url_value_preprocessor:
        """Like :meth:`url_value_preprocessor`, but for every request, not only those
        handled by the blueprint. Equivalent to :meth:`.Flask.url_value_preprocessor`.
        """
        self.record_once(
            lambda s: s.app.url_value_preprocessors.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_url_defaults(self, f: T_url_defaults) -> T_url_defaults:
        """Like :meth:`url_defaults`, but for every request, not only those handled by
        the blueprint. Equivalent to :meth:`.Flask.url_defaults`.
        """
        self.record_once(
            lambda s: s.app.url_default_functions.setdefault(None, []).append(f)
        )
        return f


