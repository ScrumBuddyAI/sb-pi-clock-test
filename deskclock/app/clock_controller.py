"""Controller for coordinating time display updates.

This module provides the DigitalClockController which bridges the domain
time service with the UI clock widget. It handles the timing mechanism
for periodic updates while keeping the update path minimal to avoid
flicker and excessive CPU usage on resource-constrained hardware.

The controller is part of the application orchestration layer, responsible
for coordinating between domain services and UI components without either
layer depending directly on the other's implementation details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer

if TYPE_CHECKING:
    from deskclock.domain.time_service import TimeServiceProtocol
    from deskclock.ui.digital_clock_widget import DigitalClockWidget

# Update interval in milliseconds (1 second)
_UPDATE_INTERVAL_MS = 1000


class DigitalClockController:
    """Controller coordinating time service updates to the clock widget.

    This controller implements a lightweight update mechanism that:
    - Uses a Qt timer to trigger updates once per second
    - Retrieves the current time from the injected time service
    - Formats the time according to configuration (with/without seconds)
    - Passes only the formatted text string to the widget

    The update path is intentionally minimal to avoid flicker and reduce
    CPU load on resource-constrained hardware like Raspberry Pi 4. Each
    tick only involves:
    1. Getting current datetime (one allocation)
    2. Formatting to string (one strftime call)
    3. Setting label text (one Qt property update)

    No widget reconstruction, layout changes, or full redraws occur during
    the update cycle.

    Example:
        from deskclock.domain.time_service import TimeService
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        time_service = TimeService()
        widget = DigitalClockWidget()
        controller = DigitalClockController(time_service, widget)
        controller.start()  # Begin automatic updates

    Attributes:
        is_running: Whether the controller is actively updating the widget.
    """

    def __init__(
        self,
        time_service: TimeServiceProtocol,
        clock_widget: DigitalClockWidget,
        *,
        show_seconds: bool = False,
    ) -> None:
        """Initialize the clock controller.

        Args:
            time_service: Service providing current time and formatting.
                Must implement the TimeServiceProtocol interface.
            clock_widget: The widget to update with formatted time.
            show_seconds: Whether to include seconds in the time display.
                Defaults to False, showing HH:MM format.
        """
        self._time_service = time_service
        self._clock_widget = clock_widget
        self._show_seconds = show_seconds

        # Create timer but don't start it yet
        self._timer = QTimer()
        self._timer.setInterval(_UPDATE_INTERVAL_MS)
        self._timer.timeout.connect(self._on_timer_tick)

    def start(self) -> None:
        """Start automatic time updates.

        Begins the periodic update cycle. The widget will be updated
        immediately and then once per second thereafter.

        If the controller is already running, this method has no effect.
        """
        if self._timer.isActive():
            return

        # Perform an immediate update so the display shows current time
        # without waiting for the first timer tick
        self._on_timer_tick()

        # Start the periodic timer
        self._timer.start()

    def stop(self) -> None:
        """Stop automatic time updates.

        Stops the periodic update cycle. The widget will retain its
        last displayed time until updates are restarted or the widget
        is manually updated.

        If the controller is not running, this method has no effect.
        """
        self._timer.stop()

    @property
    def is_running(self) -> bool:
        """Check if the controller is actively updating.

        Returns:
            True if the timer is active and updates are occurring,
            False otherwise.
        """
        return self._timer.isActive()

    @property
    def show_seconds(self) -> bool:
        """Get whether seconds are included in the time display.

        Returns:
            True if seconds are shown (HH:MM:SS), False for HH:MM format.
        """
        return self._show_seconds

    def _on_timer_tick(self) -> None:
        """Handle timer tick by updating the clock display.

        This method is called once per second by the Qt timer. It
        retrieves the current time, formats it, and updates the widget.

        The implementation is intentionally minimal to avoid unnecessary
        work on each tick:
        1. Get current datetime from time service
        2. Format datetime to display string
        3. Update widget text

        No widget reconstruction or layout changes occur.
        """
        # Get current time from the domain service
        now = self._time_service.get_now()

        # Format the time according to configuration
        display_text = self._time_service.format_time(
            now, show_seconds=self._show_seconds
        )

        # Update the widget with the formatted text
        # This only calls setText() internally - no widget reconstruction
        self._clock_widget.update_time(display_text)
