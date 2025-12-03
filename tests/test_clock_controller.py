"""Tests for the DigitalClockController.

These tests validate the controller's coordination between the time
service and the clock widget, including timer management and update
behavior.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


class MockTimeService:
    """Mock time service for testing controller behavior."""

    def __init__(self, fixed_time: datetime | None = None) -> None:
        """Initialize with an optional fixed time.

        Args:
            fixed_time: If provided, get_now() always returns this time.
                If None, returns a default test time.
        """
        self._fixed_time = fixed_time or datetime(2024, 6, 15, 14, 35, 42)
        self.get_now_call_count = 0
        self.format_time_call_count = 0

    def get_now(self) -> datetime:
        """Return the fixed test time."""
        self.get_now_call_count += 1
        return self._fixed_time

    def format_time(self, dt: datetime, *, show_seconds: bool = False) -> str:
        """Format time in test-friendly way."""
        self.format_time_call_count += 1
        if show_seconds:
            return dt.strftime("%H:%M:%S")
        return dt.strftime("%H:%M")


class TestDigitalClockControllerInstantiation:
    """Tests for controller instantiation."""

    def test_controller_can_be_instantiated(self, qapp: QApplication) -> None:
        """Test that controller can be created with required dependencies."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        assert controller is not None

    def test_controller_with_show_seconds(self, qapp: QApplication) -> None:
        """Test that controller accepts show_seconds parameter."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(
            time_service, widget, show_seconds=True
        )

        assert controller.show_seconds is True

    def test_controller_default_show_seconds_is_false(
        self, qapp: QApplication
    ) -> None:
        """Test that show_seconds defaults to False."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        assert controller.show_seconds is False

    def test_controller_not_running_initially(self, qapp: QApplication) -> None:
        """Test that controller is not running after instantiation."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        assert controller.is_running is False


class TestDigitalClockControllerStartStop:
    """Tests for controller start/stop behavior."""

    def test_start_makes_controller_running(self, qapp: QApplication) -> None:
        """Test that start() sets is_running to True."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        controller.start()
        assert controller.is_running is True
        controller.stop()

    def test_stop_makes_controller_not_running(self, qapp: QApplication) -> None:
        """Test that stop() sets is_running to False."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        controller.start()
        controller.stop()
        assert controller.is_running is False

    def test_start_is_idempotent(self, qapp: QApplication) -> None:
        """Test that calling start() multiple times is safe."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        controller.start()
        controller.start()  # Should not cause issues
        assert controller.is_running is True
        controller.stop()

    def test_stop_is_idempotent(self, qapp: QApplication) -> None:
        """Test that calling stop() when not running is safe."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        controller.stop()  # Should not cause issues when not running
        assert controller.is_running is False


class TestDigitalClockControllerUpdates:
    """Tests for controller update behavior."""

    def test_start_performs_immediate_update(self, qapp: QApplication) -> None:
        """Test that start() updates the widget immediately."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService(datetime(2024, 6, 15, 9, 5, 0))
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        controller.start()
        # Widget should show the formatted time immediately
        assert widget.current_text == "09:05"
        controller.stop()

    def test_start_with_seconds_shows_seconds(self, qapp: QApplication) -> None:
        """Test that start() with show_seconds formats correctly."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService(datetime(2024, 6, 15, 14, 35, 42))
        widget = DigitalClockWidget()
        controller = DigitalClockController(
            time_service, widget, show_seconds=True
        )

        controller.start()
        assert widget.current_text == "14:35:42"
        controller.stop()

    def test_start_calls_time_service(self, qapp: QApplication) -> None:
        """Test that start() calls the time service methods."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        controller.start()
        # Both get_now and format_time should have been called
        assert time_service.get_now_call_count >= 1
        assert time_service.format_time_call_count >= 1
        controller.stop()

    def test_controller_import_from_package(self, qapp: QApplication) -> None:
        """Test that controller can be imported from the app package."""
        from deskclock.app import DigitalClockController
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = MockTimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        assert controller is not None


class TestDigitalClockControllerIntegration:
    """Integration tests with real TimeService."""

    def test_integration_with_real_time_service(self, qapp: QApplication) -> None:
        """Test controller works with the actual TimeService."""
        from deskclock.app.clock_controller import DigitalClockController
        from deskclock.domain.time_service import TimeService
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = TimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)

        controller.start()

        # Widget should have some time displayed (HH:MM format)
        text = widget.current_text
        assert len(text) == 5  # "HH:MM"
        assert text[2] == ":"

        controller.stop()
