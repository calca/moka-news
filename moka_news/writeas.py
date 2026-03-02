"""Backward-compatible shim — the canonical module is ``moka_news.publisher._writeas``.

All symbols are re-exported so that existing ``from moka_news.writeas import ...``
statements continue to work.
"""

import warnings as _warnings

_warnings.warn(
    "moka_news.writeas is deprecated — use moka_news.publisher._writeas instead.",
    DeprecationWarning,
    stacklevel=2,
)

from moka_news.publisher._writeas import (  # noqa: F401, E402
    WRITEAS_API_BASE,
    WriteAsPublisher,
    WriteAsPublisherError,
)
