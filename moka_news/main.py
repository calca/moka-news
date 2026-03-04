"""MoKa News command-line entrypoint."""

import sys

from dotenv import load_dotenv

from moka_news.application.use_cases.daemon_service import (
    run_daemon_service,
    spawn_daemon_worker,
)
from moka_news.application.use_cases.fetch_articles import fetch_and_brew
from moka_news.application.use_cases.generate_editorial import build_editorial_context
from moka_news.application.use_cases.launch_tui import launch_cup
from moka_news.cli import (
    build_parser,
    handle_feed_management_commands,
    resolve_feed_urls,
    should_skip_first_run_setup,
)
from moka_news.cli.first_run_setup import is_first_run, run_first_run_setup
from moka_news.infrastructure.config import create_sample_config, load_config
from moka_news.infrastructure.storage import DownloadTracker, OPMLManager
from moka_news.logger import get_logger, setup_logger
from moka_news.paths import LOGS_DIR

logger = get_logger(__name__)


def _setup_main_logger(debug: bool) -> None:
    """Configure application logger."""
    import logging as _logging
    from datetime import datetime as _dt

    logs_dir = LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"moka-news-{_dt.now().strftime('%Y-%m-%d')}.log"

    if debug:
        setup_logger(
            "moka_news",
            level=_logging.DEBUG,
            log_file=str(log_file),
            file_level=_logging.DEBUG,
        )
        logger.info("\n%s", "=" * 60)
        logger.info("🔍 DEBUG MODE ENABLED")
        logger.info("📝 Logging to: %s", log_file)
        logger.info("🕐 Session started at: %s", _dt.now().strftime("%H:%M:%S"))
        logger.info("%s", "=" * 60)
        print(f"🔍 DEBUG MODE ENABLED - Logs appended to: {log_file}", file=sys.stderr)
        return

    setup_logger(
        "moka_news",
        level=_logging.INFO,
        log_file=str(log_file),
        file_level=_logging.INFO,
    )
    logger.debug("Log file: %s", log_file)


def main() -> None:
    """Main entry point for MoKa News."""
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    if args.daemon and not args.daemon_worker:
        if should_skip_first_run_setup(args):
            print(
                "⚠️  `--daemon` cannot be combined with setup/feed-management commands."
            )
            return

        if is_first_run() and not should_skip_first_run_setup(args):
            print(
                "⚠️  Daemon mode requires an existing configuration.\n"
                "   Run `moka-news` once to complete the setup wizard first."
            )
            return

        daemon_pid = spawn_daemon_worker(sys.argv[1:])
        print(f"✓ MoKa News daemon started (PID: {daemon_pid})")
        print(f"  Logs directory: {LOGS_DIR}")
        return

    _setup_main_logger(args.debug)

    opml_manager = OPMLManager(args.opml)

    if is_first_run() and not should_skip_first_run_setup(args):
        if args.daemon_worker:
            logger.error("Cannot run daemon worker on first run without configuration")
            return
        run_first_run_setup(opml_manager)
        return

    if handle_feed_management_commands(args, opml_manager):
        return

    if args.create_config:
        create_sample_config()
        return

    config = load_config(args.config)
    ai_provider = args.ai if args.ai else config["ai"]["provider"]

    if args.daemon_worker:
        run_daemon_service(args, config, ai_provider, opml_manager)
        return

    feed_urls = resolve_feed_urls(args, opml_manager, config)

    print("☕ Brewing your morning news...")

    download_tracker = DownloadTracker()
    articles, last_update = fetch_and_brew(
        feed_urls,
        config,
        ai_provider,
        download_tracker,
    )

    if not articles:
        print("No new articles found - launching TUI to access past editorials...")
    else:
        print(f"✓ Found {len(articles)} articles")

    if articles:
        print("📝 Generating morning editorial...")
    else:
        print("📝 No new articles for editorial - checking for previous editorial...")

    editorial_generator, editorial_content, editorial_path = build_editorial_context(
        config,
        args,
        ai_provider,
        articles,
    )

    print("☕ Serving your news...\n")
    launch_cup(
        args,
        articles,
        last_update,
        feed_urls,
        config,
        ai_provider,
        download_tracker,
        editorial_generator,
        editorial_content,
        editorial_path,
    )


if __name__ == "__main__":
    main()
