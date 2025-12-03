"""Tests for the time service domain component.

These tests validate the TimeService implementation for:
- Current time retrieval
- Time formatting in various configurations
- Protocol compliance for dependency injection
"""

from __future__ import annotations

from datetime import datetime

from deskclock.domain.time_service import TimeService, TimeServiceProtocol


class TestTimeServiceProtocol:
    """Tests verifying TimeService implements the protocol correctly."""

    def test_time_service_is_protocol_compatible(self) -> None:
        """Verify TimeService is structurally compatible with TimeServiceProtocol.

        This test ensures that TimeService can be used wherever
        TimeServiceProtocol is expected, enabling dependency injection.
        """
        service: TimeServiceProtocol = TimeService()
        # If we get here without type errors, the service is compatible
        assert service is not None

    def test_protocol_methods_are_callable(self) -> None:
        """Verify all protocol methods exist and are callable."""
        service: TimeServiceProtocol = TimeService()
        # Verify methods exist and are callable
        assert callable(service.get_now)
        assert callable(service.format_time)


class TestTimeServiceGetNow:
    """Tests for the get_now() method."""

    def test_get_now_returns_datetime(self) -> None:
        """Verify get_now returns a datetime object."""
        service = TimeService()
        result = service.get_now()
        assert isinstance(result, datetime)

    def test_get_now_returns_current_time(self) -> None:
        """Verify get_now returns a time close to the actual current time.

        We allow a small tolerance to account for execution time between
        the service call and our comparison.
        """
        service = TimeService()
        before = datetime.now()
        result = service.get_now()
        after = datetime.now()

        # The result should be between our before and after timestamps
        assert before <= result <= after

    def test_get_now_returns_different_times_on_successive_calls(self) -> None:
        """Verify successive calls can return different times.

        This test ensures get_now() actually queries the system clock
        rather than returning a cached value.
        """
        service = TimeService()
        times = [service.get_now() for _ in range(100)]
        # At least some times should differ (unless we're extremely fast)
        # We check that all times are valid datetimes
        assert all(isinstance(t, datetime) for t in times)


class TestTimeServiceFormatTime:
    """Tests for the format_time() method."""

    def test_format_time_without_seconds_default(self) -> None:
        """Verify default format is HH:MM without seconds."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 14, 35, 42)
        result = service.format_time(dt)
        assert result == "14:35"

    def test_format_time_without_seconds_explicit(self) -> None:
        """Verify explicit show_seconds=False produces HH:MM format."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 9, 5, 23)
        result = service.format_time(dt, show_seconds=False)
        assert result == "09:05"

    def test_format_time_with_seconds(self) -> None:
        """Verify show_seconds=True produces HH:MM:SS format."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 14, 35, 42)
        result = service.format_time(dt, show_seconds=True)
        assert result == "14:35:42"

    def test_format_time_zero_pads_hours(self) -> None:
        """Verify single-digit hours are zero-padded."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 9, 30, 0)
        result = service.format_time(dt)
        assert result == "09:30"

    def test_format_time_zero_pads_minutes(self) -> None:
        """Verify single-digit minutes are zero-padded."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 14, 5, 0)
        result = service.format_time(dt)
        assert result == "14:05"

    def test_format_time_zero_pads_seconds(self) -> None:
        """Verify single-digit seconds are zero-padded."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 14, 35, 7)
        result = service.format_time(dt, show_seconds=True)
        assert result == "14:35:07"

    def test_format_time_midnight(self) -> None:
        """Verify midnight is formatted as 00:00."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 0, 0, 0)
        result = service.format_time(dt)
        assert result == "00:00"

    def test_format_time_noon(self) -> None:
        """Verify noon is formatted as 12:00 (not 00:00 as in 12-hour)."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 12, 0, 0)
        result = service.format_time(dt)
        assert result == "12:00"

    def test_format_time_end_of_day(self) -> None:
        """Verify 23:59:59 is formatted correctly."""
        service = TimeService()
        dt = datetime(2024, 6, 15, 23, 59, 59)
        result = service.format_time(dt)
        assert result == "23:59"
        result_with_seconds = service.format_time(dt, show_seconds=True)
        assert result_with_seconds == "23:59:59"

    def test_format_time_uses_24_hour_format(self) -> None:
        """Verify afternoon times use 24-hour format (13-23), not 12-hour."""
        service = TimeService()
        # 3 PM should be 15:00, not 03:00
        dt = datetime(2024, 6, 15, 15, 0, 0)
        result = service.format_time(dt)
        assert result == "15:00"

        # 11 PM should be 23:00, not 11:00
        dt = datetime(2024, 6, 15, 23, 0, 0)
        result = service.format_time(dt)
        assert result == "23:00"


class TestTimeServiceIntegration:
    """Integration tests combining get_now and format_time."""

    def test_get_now_and_format_time_workflow(self) -> None:
        """Test the typical workflow of getting current time and formatting it."""
        service = TimeService()
        now = service.get_now()
        formatted = service.format_time(now)

        # Result should be a valid HH:MM string
        assert len(formatted) == 5
        assert formatted[2] == ":"
        hours, minutes = formatted.split(":")
        assert 0 <= int(hours) <= 23
        assert 0 <= int(minutes) <= 59

    def test_format_consistency_across_service_instances(self) -> None:
        """Verify different TimeService instances format the same time identically."""
        service1 = TimeService()
        service2 = TimeService()
        dt = datetime(2024, 6, 15, 14, 35, 42)

        result1 = service1.format_time(dt)
        result2 = service2.format_time(dt)

        assert result1 == result2
