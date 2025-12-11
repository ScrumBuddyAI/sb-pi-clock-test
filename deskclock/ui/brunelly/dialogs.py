"""Brunelly Dialog Components.

This module provides modal dialog components following the Brunelly design
system. Dialogs are used for focused interactions like forms, confirmations,
and alerts.

Dialog types:
- BrunellyDialog: General-purpose modal with custom content
- BrunellyConfirmDialog: Confirmation dialog with action buttons
"""

from enum import Enum
from typing import Optional, Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QFrame,
)

from deskclock.ui.brunelly.theme import (
    ColorPalette,
    Spacing,
    BorderRadius,
    TypographyScale,
)
from deskclock.ui.brunelly.buttons import BrunellyButton, ButtonVariant


class DialogSize(Enum):
    """Dialog size presets."""

    SMALL = 400
    MEDIUM = 500
    LARGE = 640


class BrunellyDialog(QDialog):
    """A styled modal dialog following the Brunelly design system.

    Provides a consistent dialog appearance with title, content area,
    and optional footer with action buttons.

    Signals:
        accepted: Emitted when dialog is accepted.
        rejected: Emitted when dialog is rejected.

    Example:
        dialog = BrunellyDialog(
            title="Invite User",
            size=DialogSize.MEDIUM,
            parent=main_window,
        )
        dialog.set_content(invite_form)
        dialog.add_action("Cancel", ButtonVariant.SECONDARY, dialog.reject)
        dialog.add_action("Send Invite", ButtonVariant.PRIMARY, on_submit)
        dialog.exec()
    """

    def __init__(
        self,
        title: str = "",
        size: DialogSize = DialogSize.MEDIUM,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            title: Dialog title.
            size: Dialog size preset.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._title = title
        self._size = size
        self._content: Optional[QWidget] = None
        self._actions: list[tuple[str, ButtonVariant, Callable[[], None]]] = []

        self._setup_dialog()
        self._setup_ui()
        self._apply_styles()

    def _setup_dialog(self) -> None:
        """Configure dialog properties."""
        self.setWindowTitle(self._title)
        self.setModal(True)
        self.setFixedWidth(self._size.value)

        # Remove default window frame for custom styling
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _setup_ui(self) -> None:
        """Set up the dialog layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Dialog frame (for styling)
        self._frame = QFrame()
        self._frame.setObjectName("dialogFrame")
        frame_layout = QVBoxLayout(self._frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Header
        if self._title:
            header = QWidget()
            header.setObjectName("dialogHeader")
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(
                Spacing.LG, Spacing.BASE, Spacing.LG, Spacing.BASE
            )

            title_label = QLabel(self._title)
            title_label.setObjectName("dialogTitle")
            header_layout.addWidget(title_label)
            header_layout.addStretch()

            # Close button
            close_btn = BrunellyButton(
                text="",
                variant=ButtonVariant.TERTIARY,
            )
            close_btn.setText("\u2715")  # Unicode X
            close_btn.setFixedSize(32, 32)
            close_btn.clicked.connect(self.reject)
            close_btn.setAccessibleName("Close dialog")
            header_layout.addWidget(close_btn)

            frame_layout.addWidget(header)

            # Header separator
            separator = QFrame()
            separator.setObjectName("dialogSeparator")
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFixedHeight(1)
            frame_layout.addWidget(separator)

        # Content area
        self._content_container = QWidget()
        self._content_container.setObjectName("dialogContent")
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(
            Spacing.LG, Spacing.BASE, Spacing.LG, Spacing.BASE
        )
        frame_layout.addWidget(self._content_container)

        # Footer (for action buttons)
        self._footer = QWidget()
        self._footer.setObjectName("dialogFooter")
        self._footer_layout = QHBoxLayout(self._footer)
        self._footer_layout.setContentsMargins(
            Spacing.LG, Spacing.BASE, Spacing.LG, Spacing.LG
        )
        self._footer_layout.setSpacing(Spacing.SM)
        self._footer_layout.addStretch()
        self._footer.hide()  # Hidden until actions added
        frame_layout.addWidget(self._footer)

        main_layout.addWidget(self._frame)

    def _apply_styles(self) -> None:
        """Apply Brunelly dialog styles."""
        self.setStyleSheet(f"""
            #dialogFrame {{
                background-color: {ColorPalette.NEUTRAL_0};
                border: 1px solid {ColorPalette.NEUTRAL_200};
                border-radius: {BorderRadius.XL}px;
            }}
            #dialogHeader {{
                background-color: {ColorPalette.NEUTRAL_0};
                border-top-left-radius: {BorderRadius.XL}px;
                border-top-right-radius: {BorderRadius.XL}px;
            }}
            #dialogTitle {{
                color: {ColorPalette.NEUTRAL_900};
                font-size: {TypographyScale.HEADING_3.font_size}px;
                font-weight: {TypographyScale.HEADING_3.font_weight};
            }}
            #dialogSeparator {{
                background-color: {ColorPalette.NEUTRAL_200};
                border: none;
            }}
            #dialogContent {{
                background-color: {ColorPalette.NEUTRAL_0};
            }}
            #dialogFooter {{
                background-color: {ColorPalette.NEUTRAL_50};
                border-top: 1px solid {ColorPalette.NEUTRAL_200};
                border-bottom-left-radius: {BorderRadius.XL}px;
                border-bottom-right-radius: {BorderRadius.XL}px;
            }}
        """)

    def set_content(self, widget: QWidget) -> None:
        """Set the dialog content.

        Args:
            widget: Content widget to display.
        """
        # Remove existing content
        if self._content:
            self._content_layout.removeWidget(self._content)
            self._content.setParent(None)

        self._content = widget
        self._content_layout.addWidget(widget)

    def add_action(
        self,
        text: str,
        variant: ButtonVariant,
        callback: Callable[[], None],
    ) -> BrunellyButton:
        """Add an action button to the footer.

        Args:
            text: Button text.
            variant: Button style variant.
            callback: Function to call when clicked.

        Returns:
            The created button widget.
        """
        button = BrunellyButton(text=text, variant=variant)
        button.clicked.connect(callback)
        self._footer_layout.addWidget(button)
        self._footer.show()
        self._actions.append((text, variant, callback))
        return button

    def clear_actions(self) -> None:
        """Remove all action buttons."""
        while self._footer_layout.count() > 1:  # Keep stretch
            item = self._footer_layout.takeAt(1)
            widget_item = item.widget()
            if widget_item is not None:
                widget_item.deleteLater()
        self._actions.clear()
        self._footer.hide()

    def keyPressEvent(self, event) -> None:
        """Handle key press events.

        Closes dialog on Escape key.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


class BrunellyConfirmDialog(BrunellyDialog):
    """A confirmation dialog with message and action buttons.

    Used for confirming destructive or important actions.

    Signals:
        confirmed: Emitted when user confirms the action.

    Example:
        dialog = BrunellyConfirmDialog(
            title="Disable User",
            message="Are you sure you want to disable this user?",
            confirm_text="Disable",
            confirm_variant=ButtonVariant.DANGER,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # User confirmed
            disable_user()
    """

    confirmed = Signal()

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        confirm_variant: ButtonVariant = ButtonVariant.PRIMARY,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the confirmation dialog.

        Args:
            title: Dialog title.
            message: Confirmation message.
            confirm_text: Text for confirm button.
            cancel_text: Text for cancel button.
            confirm_variant: Style for confirm button.
            parent: Parent widget.
        """
        super().__init__(title=title, size=DialogSize.SMALL, parent=parent)
        self._message = message

        self._setup_confirmation_ui(
            message, confirm_text, cancel_text, confirm_variant
        )

    def _setup_confirmation_ui(
        self,
        message: str,
        confirm_text: str,
        cancel_text: str,
        confirm_variant: ButtonVariant,
    ) -> None:
        """Set up the confirmation dialog content."""
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.NEUTRAL_600};
                font-size: {TypographyScale.BODY.font_size}px;
            }}
        """)
        self.set_content(message_label)

        # Action buttons
        self.add_action(cancel_text, ButtonVariant.SECONDARY, self.reject)
        self.add_action(confirm_text, confirm_variant, self._on_confirm)

    def _on_confirm(self) -> None:
        """Handle confirm button click."""
        self.confirmed.emit()
        self.accept()
