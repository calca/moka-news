"""
Additional tests for refresh and auto-refresh functionality
"""

from moka_news.cup import Cup
from datetime import datetime, time


def test_cup_with_last_update():
    """Test that Cup properly stores and formats last update time"""
    articles = []
    last_update = datetime(2026, 2, 13, 8, 0, 0)

    app = Cup(articles, last_update)

    assert app.last_update == last_update
    assert "13/02/2026" in app.sub_title
    assert "08:00:00" in app.sub_title
    assert "Last update:" in app.sub_title


def test_cup_with_refresh_callback():
    """Test that Cup accepts and stores refresh callback"""
    articles = []

    def mock_refresh():
        return [], datetime.now()

    app = Cup(articles, refresh_callback=mock_refresh)

    assert app.refresh_callback is not None
    assert callable(app.refresh_callback)


def test_cup_with_auto_refresh_time():
    """Test that Cup accepts and stores auto-refresh time"""
    articles = []
    auto_time = time(8, 0)

    app = Cup(articles, auto_refresh_time=auto_time)

    assert app.auto_refresh_time == auto_time


def test_cup_default_auto_refresh_time():
    """Test that Cup has default auto-refresh time of 8:00 AM"""
    app = Cup([])

    assert app.auto_refresh_time is not None
    assert app.auto_refresh_time.hour == 8
    assert app.auto_refresh_time.minute == 0


def test_format_subtitle_with_different_times():
    """Test subtitle formatting with various times"""
    # Morning time
    morning = datetime(2026, 2, 13, 8, 0, 0)
    app1 = Cup([], morning)
    assert "08:00:00" in app1.sub_title
    assert "13/02/2026" in app1.sub_title

    # Afternoon time
    afternoon = datetime(2026, 2, 13, 14, 30, 15)
    app2 = Cup([], afternoon)
    assert "14:30:15" in app2.sub_title
    assert "13/02/2026" in app2.sub_title

    # Evening time
    evening = datetime(2026, 12, 25, 20, 45, 30)
    app3 = Cup([], evening)
    assert "20:45:30" in app3.sub_title
    assert "25/12/2026" in app3.sub_title


def test_action_refresh_starts_background_refresh_without_dialog(monkeypatch):
    """Manual refresh should start immediately without opening dialogs."""
    app = Cup([], refresh_callback=lambda: ([], datetime.now()))

    calls = {"refresh": 0, "push_screen": 0}

    def fake_do_refresh():
        calls["refresh"] += 1

    def fake_push_screen(*_args, **_kwargs):
        calls["push_screen"] += 1

    monkeypatch.setattr(app, "_do_refresh", fake_do_refresh)
    monkeypatch.setattr(app, "push_screen", fake_push_screen)

    app.action_refresh()

    assert calls["refresh"] == 1
    assert calls["push_screen"] == 0


def test_action_refresh_is_ignored_when_already_running(monkeypatch):
    """Manual refresh should not start another worker while one is in progress."""
    app = Cup([], refresh_callback=lambda: ([], datetime.now()))
    app._manual_refresh_in_progress = True

    calls = {"refresh": 0}

    def fake_do_refresh():
        calls["refresh"] += 1

    monkeypatch.setattr(app, "_do_refresh", fake_do_refresh)

    app.action_refresh()

    assert calls["refresh"] == 0
