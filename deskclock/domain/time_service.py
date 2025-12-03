"""Time service for current time retrieval and formatting.

This module provides a domain service for accessing the current time and
formatting it for display. It is intentionally independent of any UI
framework (PySide6/Qt) to maintain clean architecture separation.

The service can be injected into UI components, allowing for:
- Easy unit testing with mock time sources
- Future extension to support multiple time zones
- Consistent time formatting across the application

Example usage:
    service = TimeService()
    now = service.get_now()
    display_text = service.format_time(now)  # "14:35"
    with_seconds = service.format_time(now, show_seconds=True)  # "14:35:42"
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class TimeServiceProtocol(Protocol):
    """Protocol defining the interface for time services.

    This protocol enables dependency injection and testing by defining
    a structural type that any compatible time service must implement.
    Using Protocol (PEP 544) allows for structural subtyping without
    requiring explicit inheritance.

    Implementations must provide:
    - get_now(): Returns the current datetime
    - format_time(): Formats a datetime for display
    """

    def get_now(self) -> datetime:
        """Get the current datetime.

        Returns:
            The current local datetime.
        """
        ...

    def format_time(self, dt: datetime, *, show_seconds: bool = False) -> str:
        """Format a datetime for display.

        Args:
            dt: The datetime to format.
            show_seconds: If True, include seconds in the output.

        Returns:
            Formatted time string in 24-hour format.
        """
        ...


class TimeService:
    """Default implementation of the time service.

    Provides current time retrieval using the system clock and formats
    time in 24-hour format suitable for digital clock display.

    This implementation uses Python's standard datetime module and does
    not depend on any UI framework, making it suitable for use across
    all application layers.

    The format_time method produces strings optimized for digital clock
    display:
    - Default format: "HH:MM" (e.g., "14:35")
    - With seconds: "HH:MM:SS" (e.g., "14:35:42")

    Example:
        service = TimeService()
        now = service.get_now()
        print(service.format_time(now))  # "09:05"
        print(service.format_time(now, show_seconds=True))  # "09:05:23"
    """

    # Format strings for strftime
    # Using 24-hour format as specified in requirements
    _FORMAT_WITHOUT_SECONDS = "%H:%M"
    _FORMAT_WITH_SECONDS = "%H:%M:%S"

    def get_now(self) -> datetime:
        """Get the current local datetime.

        Returns the current datetime from the system clock. The returned
        datetime is naive (no timezone info) and represents local time.

        Future enhancements may add timezone support via configuration
        or method parameters.

        Returns:
            The current local datetime.
        """
        return datetime.now()

    def format_time(self, dt: datetime, *, show_seconds: bool = False) -> str:
        """Format a datetime as a 24-hour time string.

        Produces a formatted time string suitable for digital clock display.
        The format uses 24-hour notation with zero-padded hours and minutes.

        Args:
            dt: The datetime to format. Only the time component is used.
            show_seconds: If True, include seconds in the output (HH:MM:SS).
                Defaults to False, producing HH:MM format.

        Returns:
            Formatted time string. Examples:
            - show_seconds=False: "09:05", "14:35", "00:00"
            - show_seconds=True: "09:05:23", "14:35:00", "00:00:59"
        """
        format_string = (
            self._FORMAT_WITH_SECONDS if show_seconds else self._FORMAT_WITHOUT_SECONDS
        )
        return dt.strftime(format_string)
