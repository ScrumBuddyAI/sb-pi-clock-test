"""User interface layer for DeskClock.

This package contains all PySide6/Qt widgets, layouts, and UI-specific
event handling. Domain logic and application orchestration are kept
separate from this layer.
"""

from deskclock.ui.main_window import MainWindow

__all__ = ["MainWindow"]
