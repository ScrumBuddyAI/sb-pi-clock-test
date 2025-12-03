"""Tests for the DigitalClockWidget UI component.

These tests validate that the DigitalClockWidget can be instantiated,
configured, and updated correctly in headless environments.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


class TestDigitalClockWidgetInstantiation:
    """Tests for DigitalClockWidget instantiation and configuration."""

    def test_widget_can_be_instantiated(self, qapp: QApplication) -> None:
        """Test that DigitalClockWidget can be created without errors."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        assert widget is not None

    def test_widget_with_custom_font_size(self, qapp: QApplication) -> None:
        """Test that widget accepts custom font size parameter."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget(font_size=150)
        assert widget.font_size == 150

    def test_widget_with_show_seconds_enabled(self, qapp: QApplication) -> None:
        """Test that widget accepts show_seconds parameter."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget(show_seconds=True)
        assert widget.show_seconds is True

    def test_widget_default_font_size(self, qapp: QApplication) -> None:
        """Test that widget has expected default font size."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        # Default is 200px for desk-distance viewing
        assert widget.font_size == 200

    def test_widget_default_show_seconds_is_false(self, qapp: QApplication) -> None:
        """Test that show_seconds defaults to False."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        assert widget.show_seconds is False

    def test_widget_with_all_parameters(self, qapp: QApplication) -> None:
        """Test widget creation with all parameters specified."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget(font_size=180, show_seconds=True)
        assert widget.font_size == 180
        assert widget.show_seconds is True


class TestDigitalClockWidgetUpdateTime:
    """Tests for the update_time method."""

    def test_update_time_changes_displayed_text(self, qapp: QApplication) -> None:
        """Test that update_time changes the displayed text."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        widget.update_time("14:35")
        assert widget.current_text == "14:35"

    def test_update_time_with_seconds(self, qapp: QApplication) -> None:
        """Test that update_time can display time with seconds."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        widget.update_time("14:35:42")
        assert widget.current_text == "14:35:42"

    def test_update_time_can_be_called_multiple_times(
        self, qapp: QApplication
    ) -> None:
        """Test that update_time can be called repeatedly without issues."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        times = ["00:00", "12:00", "23:59", "09:05"]
        for time_text in times:
            widget.update_time(time_text)
            assert widget.current_text == time_text

    def test_update_time_with_empty_string(self, qapp: QApplication) -> None:
        """Test that update_time handles empty string."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        widget.update_time("")
        assert widget.current_text == ""

    def test_current_text_initially_empty(self, qapp: QApplication) -> None:
        """Test that current_text is empty before any update."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        assert widget.current_text == ""


class TestDigitalClockWidgetIntegration:
    """Integration tests for DigitalClockWidget."""

    def test_widget_can_be_shown(self, qapp: QApplication) -> None:
        """Test that widget can be shown without errors."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widget = DigitalClockWidget()
        widget.show()
        widget.close()

    def test_multiple_widgets_can_be_created(self, qapp: QApplication) -> None:
        """Test that multiple widget instances can coexist."""
        from deskclock.ui.digital_clock_widget import DigitalClockWidget

        widgets = [DigitalClockWidget() for _ in range(3)]
        for i, widget in enumerate(widgets):
            widget.update_time(f"{i:02d}:00")

        # Verify each widget has its own state
        assert widgets[0].current_text == "00:00"
        assert widgets[1].current_text == "01:00"
        assert widgets[2].current_text == "02:00"

    def test_widget_import_from_package(self, qapp: QApplication) -> None:
        """Test that widget can be imported from the ui package."""
        from deskclock.ui import DigitalClockWidget

        widget = DigitalClockWidget()
        assert widget is not None
