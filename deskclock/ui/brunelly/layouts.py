"""Brunelly Layout Components.

This module provides layout components following the Brunelly design system.
These components establish consistent page structure and content organization.

Layout components:
- BrunellyPageLayout: Standard admin/settings page layout
- BrunellyCard: Content card with optional header
- BrunellyEmptyState: Empty state display with icon and message
"""

from typing import Optional, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)

from deskclock.ui.brunelly.theme import (
    ColorPalette,
    Spacing,
    BorderRadius,
    TypographyScale,
)
from deskclock.ui.brunelly.buttons import BrunellyButton, ButtonVariant


class BrunellyPageLayout(QWidget):
    """Standard page layout for admin/settings pages.

    Provides a consistent page structure with:
    - Page header with title, subtitle, and primary action
    - Scrollable content area
    - Consistent padding and spacing

    Example:
        page = BrunellyPageLayout(
            title="Users",
            subtitle="Manage who can access your project and control their roles.",
            primary_action_text="Invite User",
            primary_action_callback=on_invite_click,
        )
        page.set_content(users_table)
    """

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        primary_action_text: str = "",
        primary_action_callback: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the page layout.

        Args:
            title: Page title.
            subtitle: Page description/subtitle.
            primary_action_text: Text for primary action button.
            primary_action_callback: Callback for primary action.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._primary_action_text = primary_action_text
        self._primary_action_callback = primary_action_callback
        self._content: Optional[QWidget] = None

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Set up the page layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Page header
        self._header = QWidget()
        self._header.setObjectName("pageHeader")
        header_layout = QVBoxLayout(self._header)
        header_layout.setContentsMargins(
            Spacing.PAGE_PADDING,
            Spacing.LG,
            Spacing.PAGE_PADDING,
            Spacing.LG,
        )
        header_layout.setSpacing(Spacing.SM)

        # Title row with primary action
        title_row = QHBoxLayout()
        title_row.setSpacing(Spacing.BASE)

        # Title
        if self._title:
            title_label = QLabel(self._title)
            title_label.setObjectName("pageTitle")
            title_row.addWidget(title_label)

        title_row.addStretch()

        # Primary action button
        if self._primary_action_text:
            self._primary_button = BrunellyButton(
                text=self._primary_action_text,
                variant=ButtonVariant.PRIMARY,
            )
            if self._primary_action_callback:
                self._primary_button.clicked.connect(self._primary_action_callback)
            title_row.addWidget(self._primary_button)

        header_layout.addLayout(title_row)

        # Subtitle
        if self._subtitle:
            subtitle_label = QLabel(self._subtitle)
            subtitle_label.setObjectName("pageSubtitle")
            subtitle_label.setWordWrap(True)
            header_layout.addWidget(subtitle_label)

        main_layout.addWidget(self._header)

        # Content area with scroll
        self._scroll_area = QScrollArea()
        self._scroll_area.setObjectName("pageScrollArea")
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Content container
        self._content_container = QWidget()
        self._content_container.setObjectName("pageContent")
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(
            Spacing.PAGE_PADDING,
            Spacing.BASE,
            Spacing.PAGE_PADDING,
            Spacing.PAGE_PADDING,
        )
        self._content_layout.setSpacing(Spacing.BASE)
        self._content_layout.addStretch()

        self._scroll_area.setWidget(self._content_container)
        main_layout.addWidget(self._scroll_area, stretch=1)

    def _apply_styles(self) -> None:
        """Apply Brunelly page styles."""
        self.setStyleSheet(f"""
            BrunellyPageLayout {{
                background-color: {ColorPalette.NEUTRAL_50};
            }}
            #pageHeader {{
                background-color: {ColorPalette.NEUTRAL_0};
                border-bottom: 1px solid {ColorPalette.NEUTRAL_200};
            }}
            #pageTitle {{
                color: {ColorPalette.NEUTRAL_900};
                font-size: {TypographyScale.HEADING_1.font_size}px;
                font-weight: {TypographyScale.HEADING_1.font_weight};
            }}
            #pageSubtitle {{
                color: {ColorPalette.NEUTRAL_600};
                font-size: {TypographyScale.BODY.font_size}px;
            }}
            #pageScrollArea {{
                background-color: {ColorPalette.NEUTRAL_50};
            }}
            #pageContent {{
                background-color: {ColorPalette.NEUTRAL_50};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {ColorPalette.NEUTRAL_100};
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ColorPalette.NEUTRAL_300};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ColorPalette.NEUTRAL_400};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

    def set_content(self, widget: QWidget) -> None:
        """Set the main content widget.

        Args:
            widget: Content widget to display.
        """
        # Remove existing content
        if self._content:
            self._content_layout.removeWidget(self._content)
            self._content.setParent(None)

        # Remove stretch
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget_item = item.widget()
            if widget_item is not None:
                widget_item.setParent(None)

        self._content = widget
        self._content_layout.addWidget(widget)
        self._content_layout.addStretch()

    def add_content(self, widget: QWidget) -> None:
        """Add a widget to the content area.

        Args:
            widget: Widget to add.
        """
        # Insert before stretch
        count = self._content_layout.count()
        self._content_layout.insertWidget(count - 1, widget)

    def get_primary_button(self) -> Optional[BrunellyButton]:
        """Get the primary action button.

        Returns:
            The primary button, or None if not set.
        """
        return getattr(self, "_primary_button", None)


class BrunellyCard(QFrame):
    """A content card with optional header.

    Cards group related content with consistent styling and
    optional header with title and actions.

    Example:
        card = BrunellyCard(title="User Details")
        card.set_content(details_widget)
    """

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the card.

        Args:
            title: Optional card title.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._title = title
        self._content: Optional[QWidget] = None

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Set up the card layout."""
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Header (if title provided)
        if self._title:
            self._header = QWidget()
            self._header.setObjectName("cardHeader")
            header_layout = QHBoxLayout(self._header)
            header_layout.setContentsMargins(
                Spacing.CARD_PADDING,
                Spacing.BASE,
                Spacing.CARD_PADDING,
                Spacing.BASE,
            )

            title_label = QLabel(self._title)
            title_label.setObjectName("cardTitle")
            header_layout.addWidget(title_label)
            header_layout.addStretch()

            self._main_layout.addWidget(self._header)

        # Content area
        self._content_container = QWidget()
        self._content_container.setObjectName("cardContent")
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(
            Spacing.CARD_PADDING,
            Spacing.CARD_PADDING if not self._title else Spacing.BASE,
            Spacing.CARD_PADDING,
            Spacing.CARD_PADDING,
        )
        self._main_layout.addWidget(self._content_container)

    def _apply_styles(self) -> None:
        """Apply Brunelly card styles."""
        self.setStyleSheet(f"""
            BrunellyCard {{
                background-color: {ColorPalette.NEUTRAL_0};
                border: 1px solid {ColorPalette.NEUTRAL_200};
                border-radius: {BorderRadius.LG}px;
            }}
            #cardHeader {{
                border-bottom: 1px solid {ColorPalette.NEUTRAL_200};
            }}
            #cardTitle {{
                color: {ColorPalette.NEUTRAL_900};
                font-size: {TypographyScale.HEADING_3.font_size}px;
                font-weight: {TypographyScale.HEADING_3.font_weight};
            }}
            #cardContent {{
                background-color: transparent;
            }}
        """)

    def set_content(self, widget: QWidget) -> None:
        """Set the card content.

        Args:
            widget: Content widget.
        """
        if self._content:
            self._content_layout.removeWidget(self._content)
            self._content.setParent(None)

        self._content = widget
        self._content_layout.addWidget(widget)


class BrunellyEmptyState(QWidget):
    """Empty state display with icon, title, message, and optional action.

    Used when there's no data to display, such as an empty user list
    or no search results.

    Example:
        empty = BrunellyEmptyState(
            icon="",  # or use actual icon
            title="No users yet",
            message="Get started by inviting your first team member.",
            action_text="Invite User",
            action_callback=on_invite_click,
        )
    """

    def __init__(
        self,
        icon: str = "",
        title: str = "",
        message: str = "",
        action_text: str = "",
        action_callback: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the empty state.

        Args:
            icon: Icon character or emoji.
            title: Empty state title.
            message: Descriptive message.
            action_text: Optional action button text.
            action_callback: Optional action callback.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._icon = icon
        self._title = title
        self._message = message
        self._action_text = action_text
        self._action_callback = action_callback

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """Set up the empty state layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XXL, Spacing.XL, Spacing.XXL)
        layout.setSpacing(Spacing.BASE)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        if self._icon:
            icon_label = QLabel(self._icon)
            icon_label.setObjectName("emptyIcon")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)

        # Title
        if self._title:
            title_label = QLabel(self._title)
            title_label.setObjectName("emptyTitle")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)

        # Message
        if self._message:
            message_label = QLabel(self._message)
            message_label.setObjectName("emptyMessage")
            message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message_label.setWordWrap(True)
            message_label.setMaximumWidth(400)
            layout.addWidget(message_label)

        # Action button
        if self._action_text:
            layout.addSpacing(Spacing.SM)
            action_btn = BrunellyButton(
                text=self._action_text,
                variant=ButtonVariant.PRIMARY,
            )
            if self._action_callback:
                action_btn.clicked.connect(self._action_callback)
            # Center the button
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.addStretch()
            btn_layout.addWidget(action_btn)
            btn_layout.addStretch()
            layout.addWidget(btn_container)

    def _apply_styles(self) -> None:
        """Apply empty state styles."""
        self.setStyleSheet(f"""
            BrunellyEmptyState {{
                background-color: {ColorPalette.NEUTRAL_0};
            }}
            #emptyIcon {{
                font-size: 48px;
                color: {ColorPalette.NEUTRAL_400};
            }}
            #emptyTitle {{
                color: {ColorPalette.NEUTRAL_900};
                font-size: {TypographyScale.HEADING_3.font_size}px;
                font-weight: {TypographyScale.HEADING_3.font_weight};
            }}
            #emptyMessage {{
                color: {ColorPalette.NEUTRAL_500};
                font-size: {TypographyScale.BODY.font_size}px;
            }}
        """)
