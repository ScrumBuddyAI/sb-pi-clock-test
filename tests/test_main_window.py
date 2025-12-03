"""Tests for the MainWindow UI component.

These tests validate that the MainWindow can be instantiated and
configured correctly in headless environments without raising exceptions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


class TestMainWindowInstantiation:
    """Tests for MainWindow instantiation and basic configuration."""

    def test_main_window_can_be_instantiated(self, qapp: QApplication) -> None:
        """Test that MainWindow can be instantiated without errors.

        This verifies the basic construction of the window including
        window flags, layout setup, and styling application.
        """
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        assert window is not None
        window.close()

    def test_main_window_has_placeholder_label(self, qapp: QApplication) -> None:
        """Test that MainWindow has the expected placeholder label.

        The placeholder label should contain 'DeskClock' text and be
        accessible via the placeholder_label attribute.
        """
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        assert window.placeholder_label is not None
        assert "DeskClock" in window.placeholder_label.text()
        window.close()

    def test_main_window_has_correct_title(self, qapp: QApplication) -> None:
        """Test that MainWindow has the expected window title."""
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        assert window.windowTitle() == "DeskClock"
        window.close()

    def test_main_window_has_central_widget(self, qapp: QApplication) -> None:
        """Test that MainWindow has a central widget configured."""
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        assert window.centralWidget() is not None
        window.close()


class TestMainWindowCleanup:
    """Tests for MainWindow cleanup and shutdown behavior."""

    def test_main_window_closes_without_error(self, qapp: QApplication) -> None:
        """Test that MainWindow can be closed without raising exceptions."""
        from deskclock.ui.main_window import MainWindow

        window = MainWindow()
        window.show()
        # Closing should not raise any exceptions
        window.close()

    def test_multiple_windows_can_be_created_and_closed(
        self, qapp: QApplication
    ) -> None:
        """Test that multiple MainWindow instances can be created and closed.

        This validates that window creation and cleanup is properly
        managed and doesn't leave resources in an inconsistent state.
        """
        from deskclock.ui.main_window import MainWindow

        windows = [MainWindow() for _ in range(3)]
        for window in windows:
            window.show()
        for window in windows:
            window.close()
