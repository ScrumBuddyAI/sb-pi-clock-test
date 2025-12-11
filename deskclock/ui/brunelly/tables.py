"""Brunelly Table Components.

This module provides table components for displaying tabular data following
the Brunelly design system. Tables support sorting, selection, and custom
cell rendering.

The table system consists of:
- BrunellyTable: The main table widget
- BrunellyTableModel: Abstract model for table data
- TableColumn: Column configuration
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Optional, Union

from PySide6.QtCore import (
    Qt,
    Signal,
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QSortFilterProxyModel,
)
from PySide6.QtGui import QBrush, QColor, QPen, QFont, QPainter
from PySide6.QtWidgets import (
    QTableView,
    QHeaderView,
    QWidget,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QAbstractItemView,
    QStyle,
)

from deskclock.ui.brunelly.theme import (
    BrunellyTheme,
    ColorPalette,
    Spacing,
    BorderRadius,
    TypographyScale,
)


# Custom data roles for chip rendering
class TableDataRole:
    """Custom data roles for table cells."""

    # Role for chip type: "role", "status", or None for regular text
    ChipTypeRole = Qt.ItemDataRole.UserRole + 1
    # Role for the raw value (e.g., "admin", "active") for chip coloring
    ChipValueRole = Qt.ItemDataRole.UserRole + 2


# Type alias for Qt model index types
ModelIndex = Union[QModelIndex, QPersistentModelIndex]


class SortOrder(Enum):
    """Sort order for table columns."""

    ASCENDING = auto()
    DESCENDING = auto()
    NONE = auto()


@dataclass
class TableColumn:
    """Configuration for a table column.

    Attributes:
        key: Unique identifier for the column, used to access data.
        header: Display text for the column header.
        width: Optional fixed width in pixels.
        min_width: Minimum column width in pixels.
        sortable: Whether the column can be sorted.
        alignment: Text alignment within cells.
        renderer: Optional custom renderer function for cell content.
    """

    key: str
    header: str
    width: Optional[int] = None
    min_width: int = 80
    sortable: bool = True
    alignment: Qt.AlignmentFlag = (
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    renderer: Optional[Callable[[Any], QWidget]] = None


class BrunellyTableModel(QAbstractTableModel):
    """Abstract table model for Brunelly tables.

    Subclass this to provide data for BrunellyTable. Implement the abstract
    methods to define columns and provide row data.

    Example:
        class UserTableModel(BrunellyTableModel):
            def __init__(self, users: list[User]):
                super().__init__()
                self._users = users
                self._columns = [
                    TableColumn(key="name", header="Name"),
                    TableColumn(key="email", header="Email"),
                ]

            def columns(self) -> list[TableColumn]:
                return self._columns

            def row_count(self) -> int:
                return len(self._users)

            def get_value(self, row: int, column_key: str) -> Any:
                user = self._users[row]
                return getattr(user, column_key, "")
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the table model.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self._columns: list[TableColumn] = []

    def columns(self) -> list[TableColumn]:
        """Return the list of column configurations.

        Subclasses must implement this method.

        Returns:
            List of TableColumn configurations.
        """
        return self._columns

    def row_count(self) -> int:
        """Return the number of rows in the model.

        Subclasses must implement this method.

        Returns:
            Number of data rows.
        """
        return 0

    def get_value(self, row: int, column_key: str) -> Any:
        """Get the value for a specific cell.

        Subclasses must implement this method.

        Args:
            row: Row index.
            column_key: Column key identifier.

        Returns:
            Cell value (any type, will be converted to string for display).
        """
        return ""

    def get_row_data(self, row: int) -> Any:
        """Get the full data object for a row.

        Override this to return the underlying data object for a row,
        useful for row actions that need the full object.

        Args:
            row: Row index.

        Returns:
            The data object for the row, or None.
        """
        return None

    # Qt model interface implementation

    def rowCount(self, parent: ModelIndex = QModelIndex()) -> int:
        """Return number of rows (Qt interface)."""
        if parent.isValid():
            return 0
        return self.row_count()

    def columnCount(self, parent: ModelIndex = QModelIndex()) -> int:
        """Return number of columns (Qt interface)."""
        if parent.isValid():
            return 0
        return len(self.columns())

    def data(self, index: ModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for a cell (Qt interface)."""
        if not index.isValid():
            return None

        columns = self.columns()
        if index.column() >= len(columns):
            return None

        column = columns[index.column()]

        if role == Qt.ItemDataRole.DisplayRole:
            value = self.get_value(index.row(), column.key)
            return str(value) if value is not None else ""

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return column.alignment

        if role == Qt.ItemDataRole.UserRole:
            # Return the raw value for custom rendering
            return self.get_value(index.row(), column.key)

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return header data (Qt interface)."""
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            columns = self.columns()
            if section < len(columns):
                return columns[section].header
        return None

    def refresh(self) -> None:
        """Refresh the table data.

        Call this after modifying the underlying data to update the view.
        """
        self.beginResetModel()
        self.endResetModel()


class BrunellyTableDelegate(QStyledItemDelegate):
    """Custom delegate for Brunelly table cell rendering.

    Provides consistent styling for table cells including padding,
    typography, and hover states. Supports rendering chips for
    role and status columns.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the delegate.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

    def paint(
        self,
        painter: Any,
        option: QStyleOptionViewItem,
        index: ModelIndex,
    ) -> None:
        """Paint a table cell.

        Renders chips for role/status columns, regular text otherwise.
        """
        # Check if this cell should render as a chip
        chip_type = index.data(TableDataRole.ChipTypeRole)

        if chip_type in ("role", "status"):
            self._paint_chip(painter, option, index, chip_type)
        else:
            super().paint(painter, option, index)

    def _paint_chip(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: ModelIndex,
        chip_type: str,
    ) -> None:
        """Paint a chip in the cell.

        Args:
            painter: QPainter to use.
            option: Style options.
            index: Model index.
            chip_type: Type of chip ("role" or "status").
        """
        # Draw background for selection/hover/focus states
        # Note: state and rect are inherited from QStyleOption but not in PySide6 stubs
        has_focus = bool(option.state & QStyle.StateFlag.State_HasFocus)  # type: ignore[attr-defined]
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)  # type: ignore[attr-defined]
        is_hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)  # type: ignore[attr-defined]

        if is_selected:
            painter.fillRect(option.rect, QColor(ColorPalette.PRIMARY_50))  # type: ignore[attr-defined]
        elif is_hovered:
            painter.fillRect(option.rect, QColor(ColorPalette.NEUTRAL_50))  # type: ignore[attr-defined]

        # Get chip value and display text
        chip_value = index.data(TableDataRole.ChipValueRole)
        display_text = index.data(Qt.ItemDataRole.DisplayRole)

        if not chip_value or not display_text:
            return

        # Get colors based on chip type
        if chip_type == "role":
            bg_color, text_color, border_color = BrunellyTheme.get_role_colors(
                chip_value
            )
        else:
            bg_color, text_color, border_color = BrunellyTheme.get_status_colors(
                chip_value
            )

        # Calculate chip dimensions
        font = QFont()
        font.setPixelSize(TypographyScale.CHIP.font_size)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)

        text_width = painter.fontMetrics().horizontalAdvance(display_text)
        chip_padding_h = Spacing.CHIP_PADDING_H
        chip_padding_v = Spacing.CHIP_PADDING_V
        chip_width = text_width + (chip_padding_h * 2)
        chip_height = TypographyScale.CHIP.font_size + (chip_padding_v * 2) + 2

        # Center chip in cell
        cell_rect = option.rect  # type: ignore[attr-defined]
        chip_x = cell_rect.x() + Spacing.TABLE_CELL_PADDING_H
        chip_y = cell_rect.y() + (cell_rect.height() - chip_height) // 2

        # Draw chip background
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        chip_rect = painter.window()
        chip_rect.setRect(int(chip_x), int(chip_y), int(chip_width), int(chip_height))

        # Background
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.setPen(QPen(QColor(border_color), 1))
        painter.drawRoundedRect(
            chip_x, chip_y, chip_width, chip_height, BorderRadius.SM, BorderRadius.SM
        )

        # Text
        painter.setPen(QColor(text_color))
        text_x = chip_x + chip_padding_h
        text_y = chip_y + chip_padding_v + painter.fontMetrics().ascent()
        painter.drawText(int(text_x), int(text_y), display_text)

        # Draw focus ring for keyboard accessibility
        if has_focus:
            focus_pen = QPen(QColor(ColorPalette.PRIMARY_500), 2)
            focus_pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(focus_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Draw focus ring slightly outside the chip
            painter.drawRoundedRect(
                chip_x - 2,
                chip_y - 2,
                chip_width + 4,
                chip_height + 4,
                BorderRadius.SM + 2,
                BorderRadius.SM + 2,
            )

        painter.restore()

    def sizeHint(
        self,
        option: QStyleOptionViewItem,
        index: ModelIndex,
    ) -> Any:
        """Return the size hint for a cell."""
        chip_type = index.data(TableDataRole.ChipTypeRole)

        if chip_type in ("role", "status"):
            # Return size suitable for chip
            display_text = index.data(Qt.ItemDataRole.DisplayRole) or ""
            font = QFont()
            font.setPixelSize(TypographyScale.CHIP.font_size)
            from PySide6.QtGui import QFontMetrics

            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(display_text)
            chip_width = (
                text_width
                + (Spacing.CHIP_PADDING_H * 2)
                + (Spacing.TABLE_CELL_PADDING_H * 2)
            )
            chip_height = (
                TypographyScale.CHIP.font_size
                + (Spacing.CHIP_PADDING_V * 2)
                + Spacing.TABLE_CELL_PADDING_V * 2
            )
            from PySide6.QtCore import QSize

            return QSize(int(chip_width), int(chip_height))

        return super().sizeHint(option, index)


class BrunellyTable(QTableView):
    """A styled table view following the Brunelly design system.

    Provides a consistent table appearance with sorting, selection,
    and keyboard navigation support.

    Signals:
        row_selected: Emitted when a row is selected, with row index.
        row_double_clicked: Emitted when a row is double-clicked.
        row_action: Emitted for custom row actions.

    Example:
        model = UserTableModel(users)
        table = BrunellyTable()
        table.set_model(model)
        table.row_selected.connect(on_row_selected)
    """

    row_selected = Signal(int)
    row_double_clicked = Signal(int)
    row_action = Signal(str, int)  # action_name, row_index

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the table.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self._model: Optional[BrunellyTableModel] = None
        self._proxy_model: Optional[QSortFilterProxyModel] = None

        self._configure_view()
        self._apply_styles()
        self._connect_signals()

    def _configure_view(self) -> None:
        """Configure table view properties."""
        # Selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Header configuration
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionsClickable(True)
        header.setHighlightSections(False)

        # Vertical header (row numbers) - hide by default
        self.verticalHeader().setVisible(False)

        # Grid and scrolling
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Set delegate for custom rendering
        self.setItemDelegate(BrunellyTableDelegate(self))

        # Focus and accessibility
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Data table")

    def _apply_styles(self) -> None:
        """Apply Brunelly table styles."""
        self.setStyleSheet(f"""
            QTableView {{
                background-color: {ColorPalette.NEUTRAL_0};
                border: 1px solid {ColorPalette.NEUTRAL_200};
                border-radius: {BorderRadius.LG}px;
                gridline-color: transparent;
                font-size: {TypographyScale.BODY.font_size}px;
            }}
            QTableView::item {{
                padding: {Spacing.TABLE_CELL_PADDING_V}px {Spacing.TABLE_CELL_PADDING_H}px;
                border-bottom: 1px solid {ColorPalette.NEUTRAL_100};
            }}
            QTableView::item:selected {{
                background-color: {ColorPalette.PRIMARY_50};
                color: {ColorPalette.NEUTRAL_900};
            }}
            QTableView::item:hover {{
                background-color: {ColorPalette.NEUTRAL_50};
            }}
            QTableView::item:selected:hover {{
                background-color: {ColorPalette.PRIMARY_100};
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.NEUTRAL_50};
                color: {ColorPalette.NEUTRAL_600};
                font-weight: {TypographyScale.LABEL.font_weight};
                font-size: {TypographyScale.CAPTION.font_size}px;
                text-transform: uppercase;
                padding: {Spacing.TABLE_CELL_PADDING_V}px {Spacing.TABLE_CELL_PADDING_H}px;
                border: none;
                border-bottom: 1px solid {ColorPalette.NEUTRAL_200};
            }}
            QHeaderView::section:hover {{
                background-color: {ColorPalette.NEUTRAL_100};
            }}
            QTableView QScrollBar:vertical {{
                border: none;
                background-color: {ColorPalette.NEUTRAL_50};
                width: 8px;
                margin: 0;
            }}
            QTableView QScrollBar::handle:vertical {{
                background-color: {ColorPalette.NEUTRAL_300};
                border-radius: 4px;
                min-height: 20px;
            }}
            QTableView QScrollBar::handle:vertical:hover {{
                background-color: {ColorPalette.NEUTRAL_400};
            }}
            QTableView QScrollBar::add-line:vertical,
            QTableView QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.clicked.connect(self._on_clicked)
        self.doubleClicked.connect(self._on_double_clicked)

    def _on_clicked(self, index: QModelIndex) -> None:
        """Handle cell click."""
        source_index = self._map_to_source(index)
        if source_index.isValid():
            self.row_selected.emit(source_index.row())

    def _on_double_clicked(self, index: QModelIndex) -> None:
        """Handle cell double-click."""
        source_index = self._map_to_source(index)
        if source_index.isValid():
            self.row_double_clicked.emit(source_index.row())

    def _map_to_source(self, index: QModelIndex) -> QModelIndex:
        """Map proxy index to source index."""
        if self._proxy_model and index.isValid():
            return self._proxy_model.mapToSource(index)
        return index

    def set_model(self, model: BrunellyTableModel) -> None:
        """Set the table data model.

        Args:
            model: The data model to display.
        """
        self._model = model

        # Create proxy model for sorting/filtering
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(model)
        self._proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.setModel(self._proxy_model)
        self.setSortingEnabled(True)

        # Configure column widths
        self._configure_columns()

    def _configure_columns(self) -> None:
        """Configure column widths based on column definitions."""
        if not self._model:
            return

        header = self.horizontalHeader()
        columns = self._model.columns()

        for i, column in enumerate(columns):
            if column.width:
                header.resizeSection(i, column.width)
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

            header.setMinimumSectionSize(column.min_width)

    def get_selected_row(self) -> Optional[int]:
        """Get the currently selected row index.

        Returns:
            Selected row index, or None if no selection.
        """
        indexes = self.selectedIndexes()
        if indexes:
            source_index = self._map_to_source(indexes[0])
            return source_index.row()
        return None

    def get_selected_data(self) -> Any:
        """Get the data object for the selected row.

        Returns:
            The data object, or None if no selection.
        """
        row = self.get_selected_row()
        if row is not None and self._model:
            return self._model.get_row_data(row)
        return None

    def refresh(self) -> None:
        """Refresh the table data."""
        if self._model:
            self._model.refresh()

    def set_filter(self, text: str) -> None:
        """Set a filter on the table data.

        Args:
            text: Filter text to match against all columns.
        """
        if self._proxy_model:
            self._proxy_model.setFilterFixedString(text)
            self._proxy_model.setFilterCaseSensitivity(
                Qt.CaseSensitivity.CaseInsensitive
            )
