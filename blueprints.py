# 它从 Python 3.7 开始引入，用于提供更好的类型提示功能。
from __future__ import annotations

import os
# typing 模块是 Python 3.5 及更高版本引入的一个标准库模块，
# 用于支持类型提示和类型注解，以提高代码的可读性和可维护性。
import typing as t
# datetime基本日期和时间类型
# timedelta表示两个 date 对象或 time 对象，或者datetime对象之间的时间间隔，精确到微秒。
from datetime import timedelta

# 用于获取当前应用对象的全局变量。current_app 在应用上下文中表示当前的 Flask 应用。
from .globals import current_app
from .helpers import send_from_directory
from .sansio.blueprints import Blueprint as SansioBlueprint
from .sansio.blueprints import BlueprintSetupState as BlueprintSetupState  # noqa

# 这段代码的目的是解决循环导入的问题。通常，Response 类可能在 wrappers 模块中定义，
# 而 wrappers 模块可能也导入了当前模块。为了避免这样的循环导入，只有在类型检查时才导入 
# Response 类。在运行时，它不会导致实际的导入，因此不会引入额外的运行时开销。
if t.TYPE_CHECKING:  # pragma: no cover
    from .wrappers import Response

# Blueprint 继承自 SansioBlueprint，并且扩展了一些方法。
class Blueprint(SansioBlueprint):
    # 在发送文件时设置缓存的最大寿命（max_age）。缓存控制是通过 HTTP 头来实现的，
    # 它告诉浏览器在多长时间内可以使用缓存的文件，而不需要重新请求服务器。
    # 这可以提高 Web 应用程序的性能和加载速度。
    def get_send_file_max_age(self, filename: str | None) -> int | None:
        """Used by :func:`send_file` to determine the ``max_age`` cache
        value for a given file path if it wasn't passed.

        By default, this returns :data:`SEND_FILE_MAX_AGE_DEFAULT` from
        the configuration of :data:`~flask.current_app`. This defaults
        to ``None``, which tells the browser to use conditional requests
        instead of a timed cache, which is usually preferable.

        Note this is a duplicate of the same method in the Flask
        class.

        .. versionchanged:: 2.0
            The default configuration is ``None`` instead of 12 hours.

        .. versionadded:: 0.9
        """
        value = current_app.config["SEND_FILE_MAX_AGE_DEFAULT"]

        if value is None:
            return None

        if isinstance(value, timedelta):
            return int(value.total_seconds())

        return value

    # 用于从 static_folder 目录中提供静态文件的视图函数。
    def send_static_file(self, filename: str) -> Response:
        """The view function used to serve files from
        :attr:`static_folder`. A route is automatically registered for
        this view at :attr:`static_url_path` if :attr:`static_folder` is
        set.

        Note this is a duplicate of the same method in the Flask
        class.

        .. versionadded:: 0.5

        """
        if not self.has_static_folder:
            raise RuntimeError("'static_folder' must be set to serve static_files.")

        # send_file only knows to call get_send_file_max_age on the app,
        # call it here so it works for blueprints too.
        max_age = self.get_send_file_max_age(filename)
        return send_from_directory(
            t.cast(str, self.static_folder), filename, max_age=max_age
        )

    # 打开相对于类的root_path的资源文件以进行读取，root_path包含了应用程序的核心代码和静态资源，
    # 在应用程序的开发和部署过程中不会频繁变动。
    # t.IO[t.AnyStr]表示一个可以进行输入/输出操作的对象，可以是字符串或字节串，具体取决于上下文。
    def open_resource(self, resource: str, mode: str = "rb") -> t.IO[t.AnyStr]:
        """Open a resource file relative to :attr:`root_path` for
        reading.

        For example, if the file ``schema.sql`` is next to the file
        ``app.py`` where the ``Flask`` app is defined, it can be opened
        with:

        .. code-block:: python

            with app.open_resource("schema.sql") as f:
                conn.executescript(f.read())

        :param resource: Path to the resource relative to
            :attr:`root_path`.
        :param mode: Open the file in this mode. Only reading is
            supported, valid values are "r" (or "rt") and "rb".

        Note this is a duplicate of the same method in the Flask
        class.

        """
        if mode not in {"r", "rt", "rb"}:
            raise ValueError("Resources can only be opened for reading.")

        return open(os.path.join(self.root_path, resource), mode)