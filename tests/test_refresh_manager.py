"""
Tests for RefreshManager - validates refresh time controls
"""

import pytest
from datetime import datetime, time, timedelta
from pathlib import Path
import tempfile
import json

from moka_news.refresh_manager import RefreshManager


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_refresh_manager_initialization(temp_config_dir):
    """Test that RefreshManager initializes correctly"""
    manager = RefreshManager(temp_config_dir)
    
    assert manager.config_dir == temp_config_dir
    assert len(manager.allowed_refresh_times) == 2
    assert manager.allowed_refresh_times[0] == time(8, 0)
    assert manager.allowed_refresh_times[1] == time(20, 0)
    assert manager.auto_refresh_window == 60


def test_get_allowed_refresh_times(temp_config_dir):
    """Test getting allowed refresh times"""
    manager = RefreshManager(temp_config_dir)
    times = manager.get_allowed_refresh_times()
    
    assert len(times) == 2
    assert time(8, 0) in times
    assert time(20, 0) in times


def test_is_within_allowed_time_morning(temp_config_dir):
    """Test that morning time (8:00 AM) is allowed"""
    manager = RefreshManager(temp_config_dir)
    
    # Test exactly at 8:00 AM
    check_time = datetime(2026, 2, 15, 8, 0, 0)
    is_allowed, message = manager.is_within_allowed_time(check_time)
    
    assert is_allowed is True
    assert message is None


def test_is_within_allowed_time_evening(temp_config_dir):
    """Test that evening time (8:00 PM) is allowed"""
    manager = RefreshManager(temp_config_dir)
    
    # Test exactly at 8:00 PM
    check_time = datetime(2026, 2, 15, 20, 0, 0)
    is_allowed, message = manager.is_within_allowed_time(check_time)
    
    assert is_allowed is True
    assert message is None


def test_is_within_allowed_time_before_morning(temp_config_dir):
    """Test that time before morning window is allowed"""
    manager = RefreshManager(temp_config_dir)
    
    # Test at 7:40 AM (within 30 min window before 8 AM)
    check_time = datetime(2026, 2, 15, 7, 40, 0)
    is_allowed, message = manager.is_within_allowed_time(check_time)
    
    assert is_allowed is True
    assert message is None


def test_is_within_allowed_time_after_morning(temp_config_dir):
    """Test that time after morning window is allowed"""
    manager = RefreshManager(temp_config_dir)
    
    # Test at 8:20 AM (within 30 min window after 8 AM)
    check_time = datetime(2026, 2, 15, 8, 20, 0)
    is_allowed, message = manager.is_within_allowed_time(check_time)
    
    assert is_allowed is True
    assert message is None


def test_is_within_allowed_time_outside_window(temp_config_dir):
    """Test that time outside allowed windows is not allowed"""
    manager = RefreshManager(temp_config_dir)
    
    # Test at 2:00 PM (outside both windows)
    check_time = datetime(2026, 2, 15, 14, 0, 0)
    is_allowed, message = manager.is_within_allowed_time(check_time)
    
    assert is_allowed is False
    assert message is not None
    assert "Manual refresh is only allowed during scheduled times" in message
    assert "08:00" in message
    assert "20:00" in message


def test_is_within_allowed_time_midnight(temp_config_dir):
    """Test that midnight is not allowed"""
    manager = RefreshManager(temp_config_dir)
    
    # Test at midnight
    check_time = datetime(2026, 2, 15, 0, 0, 0)
    is_allowed, message = manager.is_within_allowed_time(check_time)
    
    assert is_allowed is False
    assert message is not None


def test_log_refresh_creates_file(temp_config_dir):
    """Test that logging a refresh creates the log file"""
    manager = RefreshManager(temp_config_dir)
    
    # Log a refresh
    timestamp = datetime(2026, 2, 15, 8, 0, 0)
    manager.log_refresh(timestamp, auto=True)
    
    # Check that file was created
    assert manager.refresh_log_file.exists()
    
    # Check content
    with open(manager.refresh_log_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 1
    assert data[0]['auto'] is True
    assert data[0]['timestamp'] == timestamp.isoformat()


def test_log_refresh_multiple_entries(temp_config_dir):
    """Test logging multiple refreshes"""
    manager = RefreshManager(temp_config_dir)
    
    # Log multiple refreshes
    manager.log_refresh(datetime(2026, 2, 15, 8, 0, 0), auto=True)
    manager.log_refresh(datetime(2026, 2, 15, 20, 0, 0), auto=True)
    manager.log_refresh(datetime(2026, 2, 15, 14, 0, 0), auto=False)
    
    # Check content
    with open(manager.refresh_log_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 3


def test_get_today_refresh_count(temp_config_dir):
    """Test counting refreshes for today"""
    manager = RefreshManager(temp_config_dir)
    
    today = datetime(2026, 2, 15, 12, 0, 0)
    
    # Log some refreshes
    manager.log_refresh(datetime(2026, 2, 15, 8, 0, 0), auto=True)
    manager.log_refresh(datetime(2026, 2, 15, 20, 0, 0), auto=True)
    manager.log_refresh(datetime(2026, 2, 14, 8, 0, 0), auto=True)  # Yesterday
    
    count = manager.get_today_refresh_count(today)
    
    assert count == 2  # Only today's refreshes


def test_get_today_refresh_count_empty(temp_config_dir):
    """Test counting refreshes when none exist"""
    manager = RefreshManager(temp_config_dir)
    
    count = manager.get_today_refresh_count()
    
    assert count == 0


def test_log_refresh_cleanup_old_entries(temp_config_dir):
    """Test that old log entries are cleaned up"""
    manager = RefreshManager(temp_config_dir)
    
    # Log a very old refresh (35 days ago)
    old_date = datetime.now() - timedelta(days=35)
    manager.log_refresh(old_date, auto=True)
    
    # Log a recent refresh
    manager.log_refresh(datetime.now(), auto=True)
    
    # Check that old entry was removed
    with open(manager.refresh_log_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 1  # Only recent entry remains


def test_get_next_refresh_time_morning(temp_config_dir):
    """Test getting next refresh time before morning"""
    manager = RefreshManager(temp_config_dir)
    
    # At 6:00 AM, next refresh should be 8:00 AM today
    current = datetime(2026, 2, 15, 6, 0, 0)
    next_refresh = manager._get_next_refresh_time(current)
    
    assert next_refresh.hour == 8
    assert next_refresh.minute == 0
    assert next_refresh.date() == current.date()


def test_get_next_refresh_time_evening(temp_config_dir):
    """Test getting next refresh time between morning and evening"""
    manager = RefreshManager(temp_config_dir)
    
    # At 2:00 PM, next refresh should be 8:00 PM today
    current = datetime(2026, 2, 15, 14, 0, 0)
    next_refresh = manager._get_next_refresh_time(current)
    
    assert next_refresh.hour == 20
    assert next_refresh.minute == 0
    assert next_refresh.date() == current.date()


def test_get_next_refresh_time_tomorrow(temp_config_dir):
    """Test getting next refresh time after evening"""
    manager = RefreshManager(temp_config_dir)
    
    # At 11:00 PM, next refresh should be 8:00 AM tomorrow
    current = datetime(2026, 2, 15, 23, 0, 0)
    next_refresh = manager._get_next_refresh_time(current)
    
    assert next_refresh.hour == 8
    assert next_refresh.minute == 0
    assert next_refresh.date() == current.date() + timedelta(days=1)


def test_hours_until_calculation(temp_config_dir):
    """Test calculating hours until next refresh"""
    manager = RefreshManager(temp_config_dir)
    
    from_time = datetime(2026, 2, 15, 6, 0, 0)
    to_time = datetime(2026, 2, 15, 8, 0, 0)
    
    hours = manager._hours_until(from_time, to_time)
    
    assert hours == 2.0
