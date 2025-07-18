import warnings

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
        Updates the style of the table headers in the `mdtable` widget.
        This method sets the font size, type, and boldness for the table headers.
        It also sets the text for the headers to "Parameter" and "Value".
        Parameters:
        None
        Returns:
        None
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


class MdTreeWidget(QWidget):
    """
    A custom QWidget that contains a DataTreeWidget for displaying hierarchical data.
    Attributes:
        layout (QVBoxLayout): The main layout of the widget.
        mdtree (DataTreeWidget): The tree widget used to display the data.
    Args:
        data (optional): The data to be displayed in the tree widget. Defaults to None.
        expandlevel (int, optional): The level to which the tree should be expanded initially. Defaults to 0.
    """

    def __init__(self, data=None, expandlevel=0) -> None:
        super(QWidget, self).__init__()

        self._explicitly_hidden = False
        self.label = "Metadata Tree"

        self.layout = QVBoxLayout(self)
        self.mdtree = DataTreeWidget(data=data)
        self.mdtree.setData(data, hideRoot=True)
        self.mdtree.setAlternatingRowColors(False)
        self.mdtree.collapseAll()
        self.mdtree.expandToDepth(expandlevel)
        self.layout.addWidget(self.mdtree)

    def setData(self, data, expandlevel: int = 0, hideRoot: bool = True) -> None:
        self.mdtree.setData(data, hideRoot=hideRoot)
        self.mdtree.expandToDepth(expandlevel)
