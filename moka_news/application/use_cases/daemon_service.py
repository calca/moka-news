"""Helpers for running MoKa News as a detached background service."""

import argparse
import signal
import subprocess
import sys
from datetime import datetime, time, timedelta
from types import FrameType
from threading import Event
from typing import Any, Dict, List, Optional, Sequence

from moka_news.application.use_cases.fetch_articles import fetch_and_brew
from moka_news.application.use_cases.editorial_text import extract_editorial_title
from moka_news.application.use_cases.generate_editorial import build_editorial_context
from moka_news.application.use_cases.publish_editorial import publish_editorial_content
from moka_news.cli.commands import resolve_feed_urls
from moka_news.infrastructure.storage import DownloadTracker, OPMLManager
from moka_news.logger import get_logger
from moka_news.publisher import PublishManager, PublishResult, create_publish_providers

logger = get_logger(__name__)

_DEFAULT_DAEMON_REFRESH_TIME = time(8, 0)


def build_daemon_worker_argv(raw_argv: Sequence[str]) -> List[str]:
    """Build argv for the detached daemon worker process."""
    worker_args = [arg for arg in raw_argv if arg != "--daemon"]
    if "--daemon-worker" not in worker_args:
        worker_args.append("--daemon-worker")
    return worker_args


def spawn_daemon_worker(raw_argv: Sequence[str]) -> int:
    """Spawn a detached daemon worker and return its PID."""
    worker_args = build_daemon_worker_argv(raw_argv)
    command = [sys.executable, "-m", "moka_news.main", *worker_args]
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=True,
    )
    return process.pid


def parse_refresh_times(config: Dict[str, Any]) -> List[time]:
    """Parse refresh schedule from config, falling back to a safe default."""
    refresh_config = config.get("refresh", {})
    allowed_times = refresh_config.get("allowed_times", ["08:00"])

    parsed_times: List[time] = []
    for raw_value in allowed_times:
        try:
            if not isinstance(raw_value, str):
                raise TypeError("refresh time must be a string")
            hour, minute = raw_value.split(":")
            parsed_times.append(time(hour=int(hour), minute=int(minute)))
        except (TypeError, ValueError) as exc:
            logger.warning("Ignoring invalid refresh time %r: %s", raw_value, exc)

    if not parsed_times:
        parsed_times = [_DEFAULT_DAEMON_REFRESH_TIME]

    return sorted(parsed_times, key=lambda t: (t.hour, t.minute))


def get_next_run_time(now: datetime, refresh_times: Sequence[time]) -> datetime:
    """Return next execution datetime for a list of daily refresh slots."""
    if not refresh_times:
        refresh_times = (_DEFAULT_DAEMON_REFRESH_TIME,)

    for slot in refresh_times:
        candidate = now.replace(
            hour=slot.hour,
            minute=slot.minute,
            second=0,
            microsecond=0,
        )
        if candidate > now:
            return candidate

    first_slot = min(refresh_times, key=lambda t: (t.hour, t.minute))
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(
        hour=first_slot.hour,
        minute=first_slot.minute,
        second=0,
        microsecond=0,
    )


def publish_editorial_automatically(
    publish_manager: PublishManager,
    editorial_content: Optional[str],
    had_new_articles: bool,
    autosend: bool,
) -> List[PublishResult]:
    """Publish editorial content in daemon mode when providers are enabled."""
    if not autosend:
        logger.info("Skipping auto-publish: publish.autosend disabled")
        return []

    if not had_new_articles:
        logger.info("Skipping auto-publish: no new articles in this cycle")
        return []

    content = (editorial_content or "").strip()
    if not content:
        logger.warning("Skipping auto-publish: editorial content is empty")
        return []

    if not any(provider.enabled for provider in publish_manager.providers):
        logger.info("Skipping auto-publish: no enabled providers in config")
        return []

    title = extract_editorial_title(content)
    logger.info("Auto-publish starting for editorial: %s", title)
    results = publish_editorial_content(publish_manager, title, content)

    for result in results:
        if result.success:
            if result.url:
                logger.info(
                    "Auto-publish success: %s -> %s", result.provider, result.url
                )
            else:
                logger.info("Auto-publish success: %s", result.provider)
        else:
            logger.warning(
                "Auto-publish failed: %s -> %s",
                result.provider,
                result.error,
            )

    return results


def run_daemon_service(
    args: argparse.Namespace,
    config: Dict[str, Any],
    ai_provider: str,
    opml_manager: OPMLManager,
) -> None:
    """Run daemon loop that periodically fetches and generates editorials."""
    refresh_times = parse_refresh_times(config)
    publish_manager = PublishManager(create_publish_providers(config))
    publish_autosend = bool(config.get("publish", {}).get("autosend", False))
    schedule = ", ".join(slot.strftime("%H:%M") for slot in refresh_times)
    logger.info("Daemon service started. Refresh schedule: %s", schedule)

    shutdown_event = Event()

    def _on_shutdown(signum: int, _frame: Optional[FrameType]) -> None:
        logger.info("Received signal %s. Stopping daemon service...", signum)
        shutdown_event.set()

    signal.signal(signal.SIGINT, _on_shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _on_shutdown)

    download_tracker = DownloadTracker()

    while not shutdown_event.is_set():
        try:
            feed_urls = resolve_feed_urls(args, opml_manager, config)
            logger.info("Daemon cycle started for %d feed(s)", len(feed_urls))

            articles, _last_update = fetch_and_brew(
                feed_urls,
                config,
                ai_provider,
                download_tracker,
            )
            _generator, _content, editorial_path = build_editorial_context(
                config,
                args,
                ai_provider,
                articles,
            )
            publish_results = publish_editorial_automatically(
                publish_manager=publish_manager,
                editorial_content=_content,
                had_new_articles=bool(articles),
                autosend=publish_autosend,
            )

            if articles:
                logger.info(
                    "Daemon cycle completed: %d article(s), editorial=%s, publish_results=%d",
                    len(articles),
                    editorial_path,
                    len(publish_results),
                )
            elif editorial_path:
                logger.info(
                    "Daemon cycle completed with no new articles, loaded editorial=%s",
                    editorial_path,
                )
            else:
                logger.info("Daemon cycle completed with no articles and no editorials")
        except Exception:
            logger.exception("Daemon cycle failed with an unexpected error")

        if shutdown_event.is_set():
            break

        now = datetime.now()
        next_run = get_next_run_time(now, refresh_times)
        wait_seconds = max(1.0, (next_run - now).total_seconds())
        logger.info(
            "Next daemon cycle at %s (in %.0f seconds)",
            next_run.isoformat(timespec="seconds"),
            wait_seconds,
        )
        shutdown_event.wait(wait_seconds)

    logger.info("Daemon service stopped.")
