"""Application orchestration layer for DeskClock.

This package contains the application lifecycle management, bootstrap logic,
and coordination between UI components and domain services.
"""

from deskclock.app.app import run
from deskclock.app.clock_controller import DigitalClockController

__all__ = ["DigitalClockController", "run"]
