"""
Refresh Manager - Manages refresh times and validation
Controls when users can refresh feeds (morning and evening only)
"""

from datetime import datetime, time, timedelta
from pathlib import Path
import json
from typing import Optional, List, Tuple


class RefreshManager:
    """Manages refresh times and validates refresh attempts"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the Refresh Manager

        Args:
            config_dir: Path to config directory (defaults to ~/.config/moka-news)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".config" / "moka-news"

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.refresh_log_file = self.config_dir / "refresh_log.json"

        # Default refresh times: 8:00 AM and 8:00 PM
        self.allowed_refresh_times = [
            time(8, 0),  # Morning
            time(20, 0),  # Evening
        ]

        # Time window around allowed times (in minutes)
        # Refresh is automatic within this window
        self.auto_refresh_window = 60  # 60 minutes

    def get_allowed_refresh_times(self) -> List[time]:
        """
        Get list of allowed refresh times

        Returns:
            List of time objects for allowed refresh times
        """
        return self.allowed_refresh_times.copy()

    def is_within_allowed_time(
        self, check_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if current time is within allowed refresh window

        Args:
            check_time: Time to check (defaults to now)

        Returns:
            Tuple of (is_allowed, reason_message)
        """
        if check_time is None:
            check_time = datetime.now()

        current_time = check_time.time()

        for allowed_time in self.allowed_refresh_times:
            # Check if within auto-refresh window
            window_start = self._subtract_minutes(
                allowed_time, self.auto_refresh_window // 2
            )
            window_end = self._add_minutes(allowed_time, self.auto_refresh_window // 2)

            if self._is_time_between(current_time, window_start, window_end):
                return True, None

        # Not within allowed time - generate helpful message
        next_refresh = self._get_next_refresh_time(check_time)
        hours_until = self._hours_until(check_time, next_refresh)

        message = (
            f"Manual refresh is only allowed during scheduled times:\n"
            f"• Morning: {self.allowed_refresh_times[0].strftime('%H:%M')}\n"
            f"• Evening: {self.allowed_refresh_times[1].strftime('%H:%M')}\n\n"
            f"Next scheduled refresh: {next_refresh.strftime('%H:%M')} "
            f"({hours_until:.1f} hours from now)"
        )

        return False, message

    def get_today_refresh_count(self, check_time: Optional[datetime] = None) -> int:
        """
        Get number of refreshes performed today

        Args:
            check_time: Time to check (defaults to now)

        Returns:
            Number of refreshes today
        """
        if check_time is None:
            check_time = datetime.now()

        today = check_time.date()
        refresh_log = self._load_refresh_log()

        count = 0
        for entry in refresh_log:
            refresh_date = datetime.fromisoformat(entry["timestamp"]).date()
            if refresh_date == today:
                count += 1

        return count

    def log_refresh(self, timestamp: Optional[datetime] = None, auto: bool = False):
        """
        Log a refresh attempt

        Args:
            timestamp: Time of refresh (defaults to now)
            auto: Whether this was an automatic refresh
        """
        if timestamp is None:
            timestamp = datetime.now()

        refresh_log = self._load_refresh_log()

        # Keep only last 30 days of logs
        cutoff = timestamp - timedelta(days=30)
        refresh_log = [
            entry
            for entry in refresh_log
            if datetime.fromisoformat(entry["timestamp"]) > cutoff
        ]

        # Add new entry
        refresh_log.append({"timestamp": timestamp.isoformat(), "auto": auto})

        self._save_refresh_log(refresh_log)

    def _load_refresh_log(self) -> List[dict]:
        """Load refresh log from file"""
        if not self.refresh_log_file.exists():
            return []

        try:
            with open(self.refresh_log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_refresh_log(self, log: List[dict]):
        """Save refresh log to file"""
        try:
            with open(self.refresh_log_file, "w", encoding="utf-8") as f:
                json.dump(log, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save refresh log: {e}")

    def _subtract_minutes(self, t: time, minutes: int) -> time:
        """Subtract minutes from a time object"""
        dt = datetime.combine(datetime.today(), t)
        dt = dt - timedelta(minutes=minutes)
        return dt.time()

    def _add_minutes(self, t: time, minutes: int) -> time:
        """Add minutes to a time object"""
        dt = datetime.combine(datetime.today(), t)
        dt = dt + timedelta(minutes=minutes)
        return dt.time()

    def _is_time_between(self, current: time, start: time, end: time) -> bool:
        """Check if current time is between start and end times"""
        if start <= end:
            return start <= current <= end
        else:
            # Handle case where time range crosses midnight
            return current >= start or current <= end

    def _get_next_refresh_time(self, from_time: datetime) -> datetime:
        """Get the next scheduled refresh time"""
        current_time = from_time.time()

        # Check each allowed time today
        for allowed_time in self.allowed_refresh_times:
            if current_time < allowed_time:
                return from_time.replace(
                    hour=allowed_time.hour,
                    minute=allowed_time.minute,
                    second=0,
                    microsecond=0,
                )

        # All times have passed today, return first time tomorrow
        tomorrow = from_time + timedelta(days=1)
        first_time = self.allowed_refresh_times[0]
        return tomorrow.replace(
            hour=first_time.hour, minute=first_time.minute, second=0, microsecond=0
        )

    def _hours_until(self, from_time: datetime, to_time: datetime) -> float:
        """Calculate hours between two times"""
        delta = to_time - from_time
        return delta.total_seconds() / 3600
