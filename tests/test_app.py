"""Tests for the application orchestration layer.

These tests validate that the application bootstrap components work
correctly in headless environments without raising exceptions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


class TestApplicationBootstrap:
    """Tests for application bootstrap and window factory functions."""

    def test_create_default_window_returns_main_window(
        self, qapp: QApplication
    ) -> None:
        """Test that the default window factory creates a MainWindow.

        The _create_default_window function should return a properly
        configured MainWindow instance.
        """
        from deskclock.app.app import _create_default_window

        window = _create_default_window()
        assert window is not None
        window.close()

    def test_create_default_window_returns_window_with_title(
        self, qapp: QApplication
    ) -> None:
        """Test that the factory-created window has the expected title."""
        from deskclock.app.app import _create_default_window

        window = _create_default_window()
        assert window.windowTitle() == "DeskClock"
        window.close()

    def test_window_factory_creates_independent_instances(
        self, qapp: QApplication
    ) -> None:
        """Test that each factory call creates a new window instance.

        Multiple calls to _create_default_window should return distinct
        window objects, not the same instance.
        """
        from deskclock.app.app import _create_default_window

        window1 = _create_default_window()
        window2 = _create_default_window()
        assert window1 is not window2
        window1.close()
        window2.close()
