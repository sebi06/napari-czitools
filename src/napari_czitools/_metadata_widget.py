import warnings
from enum import Enum

from qtpy import QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ._datatreewidget import DataTreeWidget

warnings.filterwarnings("ignore", category=DeprecationWarning)


class MetadataDisplayMode(Enum):
    NONE = "None"
    TREE = "Tree"
    TABLE = "Table"


class MdTableWidget(QWidget):
    """
    MdTableWidget is a custom QWidget that displays metadata in a table format using QTableWidget.
    Methods:
        __init__() -> None:
            Initializes the MdTableWidget with a vertical layout and a QTableWidget.
        update_metadata(md_dict: Dict) -> None:
            Updates the table with metadata from the provided dictionary.
                md_dict (Dict): Metadata dictionary where keys are parameters and values are their corresponding values.
        update_style() -> None:
            Updates the style of the table, including font size, type, and header items.
    """

    def __init__(self) -> None:
        super(QWidget, self).__init__()

        self._explicitly_hidden = False
        self.label = "Metadata Table"
        self.tooltip = "Table displaying CZI metadata"

        self.layout = QVBoxLayout(self)
        self.mdtable = QTableWidget()
        self.layout.addWidget(self.mdtable)
        self.mdtable.setShowGrid(True)
        self.mdtable.setHorizontalHeaderLabels(["Parameter", "Value"])
        header = self.mdtable.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft)

    def update_metadata(self, md_dict: dict) -> None:
        """
        Update the table with the metadata from the dictionary.
        This method updates the table widget (`self.mdtable`) with the metadata
        provided in the `md_dict` dictionary. Each key-value pair in the dictionary
        is added as a row in the table, with the key in the first column and the
        value in the second column. The table is resized to fit the content after
        updating.
            md_dict (Dict): Metadata dictionary where keys are the metadata fields
                            and values are the corresponding metadata values.
        """

        # number of rows is set to number of metadata_tools entries
        row_count = len(md_dict)
        col_count = 2
        self.mdtable.setColumnCount(col_count)
        self.mdtable.setRowCount(row_count)

        # update the table with the entries from metadata_tools dictionary
        for row, (key, value) in enumerate(md_dict.items()):
            newkey = QTableWidgetItem(key)
            self.mdtable.setItem(row, 0, newkey)
            newvalue = QTableWidgetItem(str(value))
            self.mdtable.setItem(row, 1, newvalue)

        # fit columns to content
        self.mdtable.resizeColumnsToContents()

    def update_style(self, font_bold: bool = True, font_size: int = 10) -> None:
        """
        This method customizes the appearance of the table headers by setting
        the font size, boldness, and font family. It also updates the header
        text to "Parameter" and "Value".
        ----------
        font_bold : bool, optional
            Whether the font should be bold. Defaults to True.
        font_size : int, optional
            The size of the font. Defaults to 10.
        -------
        """

        # define font size and type
        fnt = QFont()
        fnt.setPointSize(font_size)
        fnt.setBold(font_bold)
        fnt.setFamily("Arial")

        # update both header items
        # fc = (25, 25, 25)
        item1 = QtWidgets.QTableWidgetItem("Parameter")
        # item1.setForeground(QtGui.QColor(25, 25, 25))
        item1.setFont(fnt)
        self.mdtable.setHorizontalHeaderItem(0, item1)

        item2 = QtWidgets.QTableWidgetItem("Value")
        # item2.setForeground(QtGui.QColor(25, 25, 25))
        item2.setFont(fnt)
        self.mdtable.setHorizontalHeaderItem(1, item2)

    def setRowCount(self, count: int) -> None:
        """
        Convenience method to set the row count of the internal table widget.

        Args:
            count (int): The number of rows to set.
        """
        self.mdtable.setRowCount(count)


class MdTreeWidget(QWidget):
    """
    A widget for displaying metadata in a tree structure.
    Attributes:
        label (str): The label for the widget, default is "Metadata Tree".
        layout (QVBoxLayout): The layout manager for the widget.
        mdtree (DataTreeWidget): The tree widget used to display metadata.
    Args:
        data (optional): The metadata to be displayed in the tree. Defaults to None.
        expandlevel (int, optional): The initial depth to which the tree should be expanded. Defaults to 0.
    Methods:
        setData(data, expandlevel=0, hideRoot=True):
            Updates the metadata displayed in the tree widget.
            Args:
                data: The new metadata to be displayed.
                expandlevel (int, optional): The depth to which the tree should be expanded. Defaults to 0.
                hideRoot (bool, optional): Whether to hide the root node of the tree. Defaults to True.
    """

    def __init__(self, data=None, expandlevel=0, show_type_column=True) -> None:
        super(QWidget, self).__init__()

        self._explicitly_hidden = False
        self.label = "Metadata Tree"
        self.show_type_column = show_type_column

        self.layout = QVBoxLayout(self)
        self.mdtree = DataTreeWidget(data=data)
        # First set data with default expansion
        self.mdtree.setData(data, expandlevel=0, hideRoot=True)
        self.mdtree.setAlternatingRowColors(False)

        # Set type column visibility
        self.set_type_column_visibility(show_type_column)

        # Collapse everything first
        self.mdtree.collapseAll()

        # Expand only the "image" entry by one level
        self._expand_specific_item("image", levels=1)

        # Then expand according to our logic
        if expandlevel > 0:
            # With hideRoot=True, we need to expand one less level
            self.mdtree.expandToDepth(expandlevel - 1)
        # If expandlevel=0, everything stays collapsed except "image"
        self.layout.addWidget(self.mdtree)

    def setData(self, data, expandlevel: int = 0, hideRoot: bool = True) -> None:
        """
        Updates the metadata displayed in the tree widget.

        This method sets new data in the tree widget, applies the current type column
        visibility setting, and handles the expansion logic. It first collapses all
        items, then specifically expands the "image" entry by one level, and finally
        applies any additional expansion based on the expandlevel parameter.

        Args:
            data: The new metadata to be displayed in the tree. Can be any data
                  structure supported by DataTreeWidget.
            expandlevel (int, optional): The depth to which the tree should be
                                       expanded. Defaults to 0 (collapsed).
            hideRoot (bool, optional): Whether to hide the root node of the tree.
                                     Defaults to True.
        """
        # First set the data without any expansion (use expandlevel=0 but we'll override it)
        self.mdtree.setData(data, expandlevel=0, hideRoot=hideRoot)
        # Apply type column visibility after setting data
        self.set_type_column_visibility(self.show_type_column)
        # Now collapse everything first
        self.mdtree.collapseAll()

        # Expand only the "image" entry by one level
        self._expand_specific_item("image", levels=1)

        # If expandlevel > 0, also expand other items according to the general logic
        if expandlevel > 0:
            # With hideRoot=True, we need to expand one less level
            self.mdtree.expandToDepth(expandlevel - 1)

    def set_type_column_visibility(self, visible: bool, column_id: int = 2) -> None:
        """
        Set the visibility of a column in the tree widget by its index.

        This method controls whether a specific column (typically the type column)
        is visible in the metadata tree widget. It updates the internal state
        and applies the visibility change to the tree widget.

        Args:
            visible (bool): Whether the column should be visible (True) or hidden (False).
            column_id (int, optional): The index of the column to show/hide.
                                     Defaults to 2 (typically the type column).

        Returns:
            None
        """
        self.show_type_column = visible
        if visible:
            self.mdtree.showColumn(column_id)
        else:
            self.mdtree.hideColumn(column_id)

    def _expand_specific_item(self, item_name: str, levels: int = 1) -> None:
        """
        Expand a specific item in the tree by the specified number of levels.

        This method searches for a top-level item with the given name and expands it
        along with its children to the specified depth. The search is case-insensitive.

        Args:
            item_name (str): The name of the item to find and expand.
            levels (int, optional): The number of levels to expand. Defaults to 1.
                                  If 1, only the found item is expanded.
                                  If > 1, children are expanded recursively.

        Returns:
            None
        """
        # Get the root item (invisible root)
        root = self.mdtree.invisibleRootItem()

        # Search for the item with the specified name
        for i in range(root.childCount()):
            child = root.child(i)
            if child.text(0).lower() == item_name.lower():
                # Expand this item
                self.mdtree.expandItem(child)

                # If levels > 1, expand children as well
                if levels > 1:
                    self._expand_children_recursive(child, levels - 1)
                break

    def _expand_children_recursive(self, item, levels: int) -> None:
        """
        Recursively expand children of an item to the specified depth.

        This helper method traverses the tree structure starting from the given item
        and expands all children up to the specified number of levels deep.

        Args:
            item: The tree widget item whose children should be expanded.
                 This should be a QTreeWidgetItem or compatible object.
            levels (int): The number of levels to expand. When this reaches 0,
                         recursion stops. Each recursive call decrements this value.

        Returns:
            None
        """
        if levels <= 0:
            return

        for i in range(item.childCount()):
            child = item.child(i)
            self.mdtree.expandItem(child)
            if levels > 1:
                self._expand_children_recursive(child, levels - 1)

    def clear(self) -> None:
        """
        Convenience method to clear the internal tree widget.
        """
        self.mdtree.clear()
