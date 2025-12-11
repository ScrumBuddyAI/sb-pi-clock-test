"""Brunelly Notification Components.

This module provides notification components following the Brunelly design
system. Notifications communicate feedback, status, and errors to users.

Notification types:
- BrunellyBanner: Full-width banners for page-level messages
- BrunellyInlineError: Compact inline error messages for forms
- BrunellyToast: Temporary toast notifications (future enhancement)
"""

from enum import Enum, auto
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)

from deskclock.ui.brunelly.theme import (
    ColorPalette,
    Spacing,
    BorderRadius,
    TypographyScale,
)


class BannerVariant(Enum):
    """Banner style variants."""

    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()


def _get_banner_colors(variant: BannerVariant) -> tuple[str, str, str, str]:
    """Get colors for a banner variant.

    Args:
        variant: Banner variant.

    Returns:
        Tuple of (background, text, border, icon_color).
    """
    colors = {
        BannerVariant.INFO: (
            ColorPalette.INFO_50,
            ColorPalette.INFO_700,
            ColorPalette.INFO_500,
            ColorPalette.INFO_500,
        ),
        BannerVariant.SUCCESS: (
            ColorPalette.SUCCESS_50,
            ColorPalette.SUCCESS_700,
            ColorPalette.SUCCESS_500,
            ColorPalette.SUCCESS_500,
        ),
        BannerVariant.WARNING: (
            ColorPalette.WARNING_50,
            ColorPalette.WARNING_700,
            ColorPalette.WARNING_500,
            ColorPalette.WARNING_500,
        ),
        BannerVariant.ERROR: (
            ColorPalette.ERROR_50,
            ColorPalette.ERROR_700,
            ColorPalette.ERROR_500,
            ColorPalette.ERROR_500,
        ),
    }
    return colors[variant]


class BrunellyBanner(QFrame):
    """A styled banner for page-level messages.

    Banners display important information, success confirmations,
    warnings, or errors at the top of a page or section.

    Signals:
        dismissed: Emitted when the banner is dismissed.
        action_clicked: Emitted when an action button is clicked.

    Example:
        # Success banner
        banner = BrunellyBanner(
            message="User invited successfully!",
            variant=BannerVariant.SUCCESS,
            dismissible=True,
        )

        # Error banner with action
        error_banner = BrunellyBanner(
            message="Failed to load users.",
            variant=BannerVariant.ERROR,
            action_text="Retry",
        )
        error_banner.action_clicked.connect(retry_load)
    """

    dismissed = Signal()
    action_clicked = Signal()

    def __init__(
        self,
        message: str,
        variant: BannerVariant = BannerVariant.INFO,
        title: str = "",
        dismissible: bool = False,
        action_text: str = "",
        auto_dismiss_ms: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the banner.

        Args:
            message: Banner message text.
            variant: Visual style variant.
            title: Optional bold title before message.
            dismissible: Whether to show a dismiss button.
            action_text: Optional action button text.
            auto_dismiss_ms: Auto-dismiss after milliseconds (0 = no auto-dismiss).
            parent: Parent widget.
        """
        super().__init__(parent)
        self._message = message
        self._variant = variant
        self._title = title
        self._dismissible = dismissible
        self._action_text = action_text

        self._setup_ui()
        self._apply_styles()

        if auto_dismiss_ms > 0:
            QTimer.singleShot(auto_dismiss_ms, self._dismiss)

    def _setup_ui(self) -> None:
        """Set up the banner layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.BASE, Spacing.MD, Spacing.BASE, Spacing.MD)
        layout.setSpacing(Spacing.MD)

        # Icon placeholder (could be enhanced with actual icons)
        icon_label = QLabel(self._get_icon_text())
        icon_label.setObjectName("bannerIcon")
        layout.addWidget(icon_label)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(Spacing.XS)

        if self._title:
            title_label = QLabel(self._title)
            title_label.setObjectName("bannerTitle")
            text_layout.addWidget(title_label)

        message_label = QLabel(self._message)
        message_label.setObjectName("bannerMessage")
        message_label.setWordWrap(True)
        text_layout.addWidget(message_label)

        layout.addLayout(text_layout, stretch=1)

        # Action button
        if self._action_text:
            action_btn = QPushButton(self._action_text)
            action_btn.setObjectName("bannerAction")
            action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            action_btn.clicked.connect(self.action_clicked.emit)
            layout.addWidget(action_btn)

        # Dismiss button
        if self._dismissible:
            dismiss_btn = QPushButton("\u2715")  # Unicode X
            dismiss_btn.setObjectName("bannerDismiss")
            dismiss_btn.setFixedSize(24, 24)
            dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            dismiss_btn.clicked.connect(self._dismiss)
            dismiss_btn.setAccessibleName("Dismiss")
            layout.addWidget(dismiss_btn)

    def _get_icon_text(self) -> str:
        """Get icon character for the variant."""
        icons = {
            BannerVariant.INFO: "\u2139",  # i in circle
            BannerVariant.SUCCESS: "\u2713",  # checkmark
            BannerVariant.WARNING: "\u26A0",  # warning triangle
            BannerVariant.ERROR: "\u2717",  # X mark
        }
        return icons.get(self._variant, "\u2139")

    def _apply_styles(self) -> None:
        """Apply Brunelly banner styles."""
        bg, text, border, icon = _get_banner_colors(self._variant)

        self.setStyleSheet(f"""
            BrunellyBanner {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {BorderRadius.MD}px;
            }}
            #bannerIcon {{
                color: {icon};
                font-size: 16px;
                font-weight: bold;
            }}
            #bannerTitle {{
                color: {text};
                font-size: {TypographyScale.LABEL.font_size}px;
                font-weight: {TypographyScale.LABEL.font_weight};
            }}
            #bannerMessage {{
                color: {text};
                font-size: {TypographyScale.BODY.font_size}px;
            }}
            #bannerAction {{
                background-color: transparent;
                color: {text};
                border: none;
                font-size: {TypographyScale.BODY.font_size}px;
                font-weight: {TypographyScale.LABEL.font_weight};
                text-decoration: underline;
                padding: {Spacing.XS}px {Spacing.SM}px;
            }}
            #bannerAction:hover {{
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: {BorderRadius.SM}px;
            }}
            #bannerDismiss {{
                background-color: transparent;
                color: {text};
                border: none;
                font-size: 14px;
                border-radius: {BorderRadius.SM}px;
            }}
            #bannerDismiss:hover {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
        """)

    def _dismiss(self) -> None:
        """Dismiss the banner."""
        self.dismissed.emit()
        self.hide()
        self.deleteLater()

    def set_message(self, message: str) -> None:
        """Update the banner message.

        Args:
            message: New message text.
        """
        self._message = message
        # Find and update the message label
        for child in self.findChildren(QLabel):
            if child.objectName() == "bannerMessage":
                child.setText(message)
                break


class BrunellyInlineError(QWidget):
    """An inline error message for form validation.

    Displays a compact error message typically below a form field.

    Example:
        error = BrunellyInlineError("Email is required")
        form_layout.addWidget(error)
    """

    def __init__(
        self,
        message: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the inline error.

        Args:
            message: Error message text.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._message = message

        self._setup_ui()
        self._apply_styles()

        if not message:
            self.hide()

    def _setup_ui(self) -> None:
        """Set up the error layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, Spacing.XS, 0, 0)
        layout.setSpacing(Spacing.XS)

        # Error icon
        self._icon = QLabel("\u26A0")  # Warning triangle
        self._icon.setObjectName("errorIcon")
        layout.addWidget(self._icon)

        # Error message
        self._label = QLabel(self._message)
        self._label.setObjectName("errorMessage")
        self._label.setWordWrap(True)
        layout.addWidget(self._label, stretch=1)

    def _apply_styles(self) -> None:
        """Apply error styles."""
        self.setStyleSheet(f"""
            #errorIcon {{
                color: {ColorPalette.ERROR_500};
                font-size: 12px;
            }}
            #errorMessage {{
                color: {ColorPalette.ERROR_600};
                font-size: {TypographyScale.CAPTION.font_size}px;
            }}
        """)

    def set_message(self, message: str) -> None:
        """Set the error message.

        Args:
            message: Error message. Empty string hides the error.
        """
        self._message = message
        self._label.setText(message)
        self.setVisible(bool(message))

    def clear(self) -> None:
        """Clear the error message."""
        self.set_message("")
