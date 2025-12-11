"""Brunelly Form Components.

This module provides form input components following the Brunelly design system.
Components include text inputs, select dropdowns, and form field wrappers
with integrated labels and validation.

Form components support:
- Labels and helper text
- Required field indicators
- Validation states (error, success)
- Inline error messages
- Accessibility attributes
"""

from enum import Enum, auto
from typing import Optional, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
)

from deskclock.ui.brunelly.theme import (
    ColorPalette,
    Spacing,
    BorderRadius,
    TypographyScale,
)


class ValidationState(Enum):
    """Validation state for form fields."""

    NONE = auto()
    VALID = auto()
    INVALID = auto()


class BrunellyTextInput(QLineEdit):
    """A styled text input following the Brunelly design system.

    Provides consistent styling with focus states, validation indicators,
    and placeholder text support.

    Signals:
        value_changed: Emitted when text changes, with new value.
        validation_changed: Emitted when validation state changes.

    Example:
        email_input = BrunellyTextInput(
            placeholder="Enter email address",
        )
        email_input.value_changed.connect(on_email_changed)
    """

    value_changed = Signal(str)
    validation_changed = Signal(ValidationState)

    def __init__(
        self,
        placeholder: str = "",
        initial_value: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the text input.

        Args:
            placeholder: Placeholder text shown when empty.
            initial_value: Initial text value.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._validation_state = ValidationState.NONE

        self.setPlaceholderText(placeholder)
        if initial_value:
            self.setText(initial_value)

        self._apply_styles()
        self._configure_accessibility()
        self._connect_signals()

    def _apply_styles(self) -> None:
        """Apply Brunelly input styles."""
        self._update_styles()

    def _update_styles(self) -> None:
        """Update styles based on validation state."""
        # Determine border color based on validation state
        if self._validation_state == ValidationState.INVALID:
            border_color = ColorPalette.ERROR_500
            focus_color = ColorPalette.ERROR_300
        elif self._validation_state == ValidationState.VALID:
            border_color = ColorPalette.SUCCESS_500
            focus_color = ColorPalette.SUCCESS_300
        else:
            border_color = ColorPalette.NEUTRAL_300
            focus_color = ColorPalette.PRIMARY_300

        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ColorPalette.NEUTRAL_0};
                color: {ColorPalette.NEUTRAL_900};
                border: 1px solid {border_color};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.INPUT_PADDING_V}px {Spacing.INPUT_PADDING_H}px;
                font-size: {TypographyScale.BODY.font_size}px;
                selection-background-color: {ColorPalette.PRIMARY_200};
            }}
            QLineEdit:hover {{
                border-color: {ColorPalette.NEUTRAL_400};
            }}
            QLineEdit:focus {{
                border-color: {focus_color};
                outline: none;
            }}
            QLineEdit:disabled {{
                background-color: {ColorPalette.NEUTRAL_100};
                color: {ColorPalette.NEUTRAL_500};
                border-color: {ColorPalette.NEUTRAL_200};
            }}
            QLineEdit::placeholder {{
                color: {ColorPalette.NEUTRAL_400};
            }}
        """)

    def _configure_accessibility(self) -> None:
        """Configure accessibility properties."""
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str) -> None:
        """Handle text change."""
        self.value_changed.emit(text)

    def set_validation_state(self, state: ValidationState) -> None:
        """Set the validation state.

        Args:
            state: New validation state.
        """
        if state != self._validation_state:
            self._validation_state = state
            self._update_styles()
            self.validation_changed.emit(state)

    def get_value(self) -> str:
        """Get the current text value.

        Returns:
            Current input text.
        """
        return self.text()

    def set_value(self, value: str) -> None:
        """Set the text value.

        Args:
            value: New text value.
        """
        self.setText(value)

    def clear_validation(self) -> None:
        """Clear the validation state."""
        self.set_validation_state(ValidationState.NONE)


class BrunellySelect(QComboBox):
    """A styled select dropdown following the Brunelly design system.

    Provides a dropdown with consistent styling and keyboard navigation.

    Signals:
        selection_changed: Emitted when selection changes, with new value.

    Example:
        role_select = BrunellySelect(
            options=[("admin", "Admin"), ("user", "User")],
            placeholder="Select role",
        )
        role_select.selection_changed.connect(on_role_changed)
    """

    selection_changed = Signal(str)

    def __init__(
        self,
        options: Optional[Sequence[tuple[str, str]]] = None,
        placeholder: str = "",
        initial_value: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the select.

        Args:
            options: List of (value, display_text) tuples.
            placeholder: Placeholder text shown when no selection.
            initial_value: Initial selected value.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._placeholder = placeholder

        if placeholder:
            self.addItem(placeholder, "")
            self.setCurrentIndex(0)

        if options:
            for value, text in options:
                self.addItem(text, value)

        if initial_value:
            self.set_value(initial_value)

        self._apply_styles()
        self._configure_accessibility()
        self._connect_signals()

    def _apply_styles(self) -> None:
        """Apply Brunelly select styles."""
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.NEUTRAL_0};
                color: {ColorPalette.NEUTRAL_900};
                border: 1px solid {ColorPalette.NEUTRAL_300};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.INPUT_PADDING_V}px {Spacing.INPUT_PADDING_H}px;
                padding-right: {Spacing.XL}px;
                font-size: {TypographyScale.BODY.font_size}px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border-color: {ColorPalette.NEUTRAL_400};
            }}
            QComboBox:focus {{
                border-color: {ColorPalette.PRIMARY_300};
                outline: none;
            }}
            QComboBox:disabled {{
                background-color: {ColorPalette.NEUTRAL_100};
                color: {ColorPalette.NEUTRAL_500};
                border-color: {ColorPalette.NEUTRAL_200};
            }}
            QComboBox::drop-down {{
                border: none;
                width: {Spacing.LG}px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {ColorPalette.NEUTRAL_0};
                border: 1px solid {ColorPalette.NEUTRAL_200};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.XS}px;
                selection-background-color: {ColorPalette.PRIMARY_50};
                selection-color: {ColorPalette.NEUTRAL_900};
            }}
            QComboBox QAbstractItemView::item {{
                padding: {Spacing.SM}px {Spacing.MD}px;
                min-height: 32px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {ColorPalette.NEUTRAL_100};
            }}
        """)

    def _configure_accessibility(self) -> None:
        """Configure accessibility properties."""
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.currentIndexChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, index: int) -> None:
        """Handle selection change."""
        value = self.itemData(index)
        if value:  # Ignore placeholder selection
            self.selection_changed.emit(str(value))

    def get_value(self) -> str:
        """Get the currently selected value.

        Returns:
            Selected value, or empty string if placeholder selected.
        """
        value = self.currentData()
        return str(value) if value else ""

    def set_value(self, value: str) -> None:
        """Set the selected value.

        Args:
            value: Value to select.
        """
        index = self.findData(value)
        if index >= 0:
            self.setCurrentIndex(index)

    def set_options(self, options: Sequence[tuple[str, str]]) -> None:
        """Replace all options.

        Args:
            options: List of (value, display_text) tuples.
        """
        current_value = self.get_value()
        self.clear()

        if self._placeholder:
            self.addItem(self._placeholder, "")

        for value, text in options:
            self.addItem(text, value)

        # Restore selection if possible
        if current_value:
            self.set_value(current_value)


class BrunellyFormField(QWidget):
    """A form field wrapper with label, input, and error message.

    Provides a consistent layout for form fields with:
    - Label with optional required indicator
    - Input component (text input or select)
    - Helper text
    - Inline error message

    Example:
        email_field = BrunellyFormField(
            label="Email",
            required=True,
            helper_text="We'll send an invitation to this address",
        )
        email_field.set_input(BrunellyTextInput(placeholder="email@example.com"))
    """

    def __init__(
        self,
        label: str = "",
        required: bool = False,
        helper_text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the form field.

        Args:
            label: Field label text.
            required: Whether the field is required.
            helper_text: Helper text shown below input.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._label_text = label
        self._required = required
        self._helper_text = helper_text
        self._input: Optional[QWidget] = None
        self._error_message = ""

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the form field layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.XS)

        # Label row
        if self._label_text:
            label_layout = QHBoxLayout()
            label_layout.setContentsMargins(0, 0, 0, 0)
            label_layout.setSpacing(Spacing.XS)

            self._label = QLabel(self._label_text)
            self._label.setStyleSheet(f"""
                QLabel {{
                    color: {ColorPalette.NEUTRAL_700};
                    font-size: {TypographyScale.LABEL.font_size}px;
                    font-weight: {TypographyScale.LABEL.font_weight};
                }}
            """)
            label_layout.addWidget(self._label)

            if self._required:
                required_indicator = QLabel("*")
                required_indicator.setStyleSheet(f"""
                    QLabel {{
                        color: {ColorPalette.ERROR_500};
                        font-size: {TypographyScale.LABEL.font_size}px;
                    }}
                """)
                label_layout.addWidget(required_indicator)

            label_layout.addStretch()
            layout.addLayout(label_layout)

        # Input placeholder (will be replaced by set_input)
        self._input_container = QVBoxLayout()
        self._input_container.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._input_container)

        # Helper text
        if self._helper_text:
            self._helper_label = QLabel(self._helper_text)
            self._helper_label.setStyleSheet(f"""
                QLabel {{
                    color: {ColorPalette.NEUTRAL_500};
                    font-size: {TypographyScale.CAPTION.font_size}px;
                }}
            """)
            self._helper_label.setWordWrap(True)
            layout.addWidget(self._helper_label)

        # Error message (hidden initially)
        self._error_label = QLabel()
        self._error_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.ERROR_600};
                font-size: {TypographyScale.CAPTION.font_size}px;
            }}
        """)
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

    def set_input(self, input_widget: QWidget) -> None:
        """Set the input widget for this field.

        Args:
            input_widget: The input widget (e.g., BrunellyTextInput).
        """
        # Remove existing input
        if self._input:
            self._input_container.removeWidget(self._input)
            self._input.setParent(None)

        self._input = input_widget
        self._input_container.addWidget(input_widget)

        # Set accessibility relationship
        if hasattr(self, "_label") and self._label_text:
            input_widget.setAccessibleName(self._label_text)

    def get_input(self) -> Optional[QWidget]:
        """Get the input widget.

        Returns:
            The input widget, or None if not set.
        """
        return self._input

    def set_error(self, message: str) -> None:
        """Set an error message.

        Args:
            message: Error message to display. Empty string clears error.
        """
        self._error_message = message
        if message:
            self._error_label.setText(message)
            self._error_label.show()
            if isinstance(self._input, BrunellyTextInput):
                self._input.set_validation_state(ValidationState.INVALID)
        else:
            self._error_label.hide()
            if isinstance(self._input, BrunellyTextInput):
                self._input.clear_validation()

    def clear_error(self) -> None:
        """Clear any error message."""
        self.set_error("")

    def has_error(self) -> bool:
        """Check if the field has an error.

        Returns:
            True if an error message is set.
        """
        return bool(self._error_message)
