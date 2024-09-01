from __future__ import annotations

import json as _json
import typing as t

from ..globals import current_app
from .provider import _default

if t.TYPE_CHECKING:  # pragma: no cover
    from ..wrappers import Response