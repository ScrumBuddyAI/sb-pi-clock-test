"""Application orchestration layer for DeskClock.

This package contains the application lifecycle management, bootstrap logic,
and coordination between UI components and domain services.
"""

from deskclock.app.app import run

__all__ = ["run"]
