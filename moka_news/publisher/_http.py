"""HTTP compatibility shim for optional requests dependency."""

try:
    import requests as _requests
except (
    ImportError
):  # pragma: no cover - exercised only in minimal envs without requests

    class _RequestsShim:
        """Shim used when requests is unavailable."""

        class RequestException(Exception):
            pass

        @staticmethod
        def post(*args, **kwargs):
            raise ModuleNotFoundError("No module named 'requests'")

    requests = _RequestsShim()
else:
    requests = _requests
