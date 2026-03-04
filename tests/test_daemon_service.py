"""Tests for daemon mode helpers."""

from datetime import datetime, time
from typing import Any, Dict

from moka_news.publisher import PublishManager, PublishProvider

from moka_news.application.use_cases.daemon_service import (
    build_daemon_worker_argv,
    get_next_run_time,
    parse_refresh_times,
    publish_editorial_automatically,
)
from moka_news.cli.parser import build_parser


class DummyPublishProvider(PublishProvider):
    """Minimal publish provider for daemon publishing tests."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.publish_calls = 0
        self.last_title = ""
        self.last_content = ""

    @property
    def name(self) -> str:
        return "dummy"

    def is_configured(self) -> bool:
        return True

    def publish(self, title: str, content: str) -> Dict[str, Any]:
        self.publish_calls += 1
        self.last_title = title
        self.last_content = content
        return {"provider": self.name, "url": "https://example.com/post"}


def test_parser_accepts_daemon_flags():
    """CLI parser should expose daemon options."""
    parser = build_parser()

    args = parser.parse_args(["--daemon"])
    assert args.daemon is True
    assert args.daemon_worker is False

    worker_args = parser.parse_args(["--daemon-worker"])
    assert worker_args.daemon is False
    assert worker_args.daemon_worker is True


def test_build_daemon_worker_argv_strips_daemon_flag():
    """Worker argv should replace --daemon with --daemon-worker."""
    argv = build_daemon_worker_argv(["--daemon", "--ai", "simple"])
    assert argv == ["--ai", "simple", "--daemon-worker"]


def test_build_daemon_worker_argv_avoids_duplicate_worker_flag():
    """Worker argv should not duplicate hidden worker flag."""
    argv = build_daemon_worker_argv(["--ai", "openai", "--daemon-worker"])
    assert argv == ["--ai", "openai", "--daemon-worker"]


def test_parse_refresh_times_sorts_valid_times():
    """Refresh slots should be parsed and sorted."""
    config = {"refresh": {"allowed_times": ["20:30", "08:00"]}}
    refresh_times = parse_refresh_times(config)
    assert refresh_times == [time(8, 0), time(20, 30)]


def test_parse_refresh_times_falls_back_on_invalid_values():
    """Invalid refresh slots should fall back to default schedule."""
    config = {"refresh": {"allowed_times": ["invalid", 123]}}
    refresh_times = parse_refresh_times(config)
    assert refresh_times == [time(8, 0)]


def test_get_next_run_time_for_today_slot():
    """Next run should use same day when a slot is still ahead."""
    now = datetime(2026, 2, 15, 7, 45, 0)
    refresh_times = [time(8, 0), time(20, 0)]
    next_run = get_next_run_time(now, refresh_times)
    assert next_run == datetime(2026, 2, 15, 8, 0, 0)


def test_get_next_run_time_rolls_to_next_day():
    """Next run should roll over when all today's slots are passed."""
    now = datetime(2026, 2, 15, 21, 15, 0)
    refresh_times = [time(8, 0), time(20, 0)]
    next_run = get_next_run_time(now, refresh_times)
    assert next_run == datetime(2026, 2, 16, 8, 0, 0)


def test_publish_editorial_automatically_publishes_when_enabled():
    """Daemon should auto-publish when new articles are available."""
    provider = DummyPublishProvider({"enabled": True})
    manager = PublishManager([provider])

    results = publish_editorial_automatically(
        publish_manager=manager,
        editorial_content="TITLE: Daily Briefing\n\nEditorial body",
        had_new_articles=True,
    )

    assert len(results) == 1
    assert results[0].success is True
    assert provider.publish_calls == 1
    assert provider.last_title == "Daily Briefing"


def test_publish_editorial_automatically_skips_without_new_articles():
    """Daemon should not re-publish old editorials when nothing new was fetched."""
    provider = DummyPublishProvider({"enabled": True})
    manager = PublishManager([provider])

    results = publish_editorial_automatically(
        publish_manager=manager,
        editorial_content="TITLE: Existing Editorial\n\nBody",
        had_new_articles=False,
    )

    assert results == []
    assert provider.publish_calls == 0


def test_publish_editorial_automatically_skips_without_enabled_providers():
    """Daemon should skip auto-publish when no providers are enabled."""
    provider = DummyPublishProvider({"enabled": False})
    manager = PublishManager([provider])

    results = publish_editorial_automatically(
        publish_manager=manager,
        editorial_content="TITLE: Editorial\n\nBody",
        had_new_articles=True,
    )

    assert results == []
    assert provider.publish_calls == 0
