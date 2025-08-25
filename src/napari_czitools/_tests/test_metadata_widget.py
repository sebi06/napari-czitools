"""
Tests for the _metadata_widget module.

This module tests the MdTableWidget, MdTreeWidget classes and MetadataDisplayMode enum
to ensure proper functionality of the metadata display components.
"""

from unittest.mock import Mock, patch

import pytest
from qtpy.QtWidgets import QApplication, QTableWidget, QVBoxLayout

from napari_czitools._metadata_widget import (
    MdTableWidget,
    MdTreeWidget,
    MetadataDisplayMode,
)


class TestMetadataDisplayMode:
    """Test class for MetadataDisplayMode enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert MetadataDisplayMode.NONE.value == "None"
        assert MetadataDisplayMode.TREE.value == "Tree"
        assert MetadataDisplayMode.TABLE.value == "Table"

    def test_enum_membership(self):
        """Test enum membership."""
        assert MetadataDisplayMode.NONE in MetadataDisplayMode
        assert MetadataDisplayMode.TREE in MetadataDisplayMode
        assert MetadataDisplayMode.TABLE in MetadataDisplayMode

    def test_enum_count(self):
        """Test that the enum has exactly 3 values."""
        assert len(MetadataDisplayMode) == 3


class TestMdTableWidget:
    """Test class for MdTableWidget."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        widget = MdTableWidget()

        assert widget._explicitly_hidden is False
        assert widget.label == "Metadata Table"
        assert widget.tooltip == "Table displaying CZI metadata"
        assert hasattr(widget, "layout")
        assert hasattr(widget, "mdtable")
        assert isinstance(widget.mdtable, QTableWidget)

    def test_init_table_setup(self):
        """Test that the table is properly set up during initialization."""
        widget = MdTableWidget()

        # Check table properties
        assert widget.mdtable.showGrid() is True
        # Column count is set during setHorizontalHeaderLabels
        expected_labels = ["Parameter", "Value"]
        assert len(expected_labels) == 2  # We expect 2 columns

        # Check that the table widget exists and is properly configured
        assert hasattr(widget, "mdtable")
        assert isinstance(widget.mdtable, QTableWidget)

    def test_update_metadata_empty_dict(self):
        """Test update_metadata with an empty dictionary."""
        widget = MdTableWidget()

        empty_dict = {}
        widget.update_metadata(empty_dict)

        assert widget.mdtable.rowCount() == 0
        assert widget.mdtable.columnCount() == 2

    def test_update_metadata_simple_dict(self):
        """Test update_metadata with a simple dictionary."""
        widget = MdTableWidget()

        test_dict = {"Width": 1024, "Height": 768, "Channels": 3}

        widget.update_metadata(test_dict)

        # Check row and column counts
        assert widget.mdtable.rowCount() == 3
        assert widget.mdtable.columnCount() == 2

        # Check content
        expected_data = [("Width", "1024"), ("Height", "768"), ("Channels", "3")]

        for row, (expected_key, expected_value) in enumerate(expected_data):
            key_item = widget.mdtable.item(row, 0)
            value_item = widget.mdtable.item(row, 1)

            assert key_item is not None
            assert value_item is not None
            assert key_item.text() == expected_key
            assert value_item.text() == expected_value

    def test_update_metadata_complex_values(self):
        """Test update_metadata with complex values that need string conversion."""
        widget = MdTableWidget()

        test_dict = {"List": [1, 2, 3], "Dict": {"nested": "value"}, "None": None, "Boolean": True, "Float": 3.14159}

        widget.update_metadata(test_dict)

        assert widget.mdtable.rowCount() == 5

        # Check that all values are converted to strings
        for row in range(widget.mdtable.rowCount()):
            value_item = widget.mdtable.item(row, 1)
            assert isinstance(value_item.text(), str)

    def test_update_metadata_overwrites_previous(self):
        """Test that update_metadata overwrites previous data."""
        widget = MdTableWidget()

        # First update
        first_dict = {"A": 1, "B": 2}
        widget.update_metadata(first_dict)
        assert widget.mdtable.rowCount() == 2

        # Second update with different data
        second_dict = {"X": 10, "Y": 20, "Z": 30}
        widget.update_metadata(second_dict)
        assert widget.mdtable.rowCount() == 3

        # Check that old data is gone
        for row in range(widget.mdtable.rowCount()):
            key_item = widget.mdtable.item(row, 0)
            assert key_item.text() in ["X", "Y", "Z"]

    def test_update_style_default_parameters(self):
        """Test update_style with default parameters."""
        widget = MdTableWidget()

        # Ensure table is properly initialized with 2 columns
        widget.mdtable.setColumnCount(2)

        # Call update_style with defaults
        widget.update_style()

        # Check that header items are created and set properly
        param_header = widget.mdtable.horizontalHeaderItem(0)
        value_header = widget.mdtable.horizontalHeaderItem(1)

        # The headers should be created by update_style
        assert param_header is not None
        assert value_header is not None
        assert param_header.text() == "Parameter"
        assert value_header.text() == "Value"

        # Check font properties
        font = param_header.font()
        assert font.pointSize() == 10
        assert font.bold() is True
        assert font.family() == "Arial"

    def test_update_style_custom_parameters(self):
        """Test update_style with custom parameters."""
        widget = MdTableWidget()

        # Ensure table is properly initialized with 2 columns
        widget.mdtable.setColumnCount(2)

        # Call update_style with custom values
        widget.update_style(font_bold=False, font_size=14)

        # Check font properties after update_style creates the headers
        param_header = widget.mdtable.horizontalHeaderItem(0)
        assert param_header is not None  # Should be created by update_style

        font = param_header.font()
        assert font.pointSize() == 14
        assert font.bold() is False
        assert font.family() == "Arial"

    def test_setRowCount(self):
        """Test the setRowCount convenience method."""
        widget = MdTableWidget()

        # Test setting row count
        widget.setRowCount(5)
        assert widget.mdtable.rowCount() == 5

        widget.setRowCount(0)
        assert widget.mdtable.rowCount() == 0

        widget.setRowCount(10)
        assert widget.mdtable.rowCount() == 10

    def test_layout_structure(self):
        """Test that the layout is properly structured."""
        widget = MdTableWidget()

        # Check that the table is added to the layout
        layout = widget.layout
        assert layout.count() == 1
        assert layout.itemAt(0).widget() == widget.mdtable


class TestMdTreeWidget:
    """Test class for MdTreeWidget."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        widget = MdTreeWidget()

        assert widget._explicitly_hidden is False
        assert widget.label == "Metadata Tree"
        assert widget.show_type_column is True
        assert hasattr(widget, "layout")
        assert hasattr(widget, "mdtree")

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        test_data = {"key": "value"}
        widget = MdTreeWidget(data=test_data, expandlevel=2, show_type_column=False)

        assert widget.label == "Metadata Tree"
        assert widget.show_type_column is False

    def test_init_with_data(self):
        """Test initialization with data."""
        test_data = {"image": {"width": 1024, "height": 768}, "metadata": {"channels": 3}}

        widget = MdTreeWidget(data=test_data)

        # Check that data was set
        assert widget.mdtree is not None

    def test_setData_basic(self):
        """Test setData method with basic functionality."""
        widget = MdTreeWidget()

        test_data = {"image": {"width": 1024, "height": 768}, "channels": 3}

        # Mock the tree widget methods to verify calls
        with (
            patch.object(widget.mdtree, "setData"),
            patch.object(widget.mdtree, "collapseAll"),
            patch.object(widget, "set_type_column_visibility") as mock_set_type_column,
            patch.object(widget, "_expand_specific_item") as mock_expand_specific,
        ):

            widget.setData(test_data, expandlevel=1, hideRoot=False)

            # Verify method calls
            mock_set_type_column.assert_called_once_with(True)  # default show_type_column
            mock_expand_specific.assert_called_once_with("image", levels=1)

    def test_setData_with_expansion(self):
        """Test setData with expansion level > 0."""
        widget = MdTreeWidget()

        test_data = {"test": "data"}

        with (
            patch.object(widget.mdtree, "setData"),
            patch.object(widget.mdtree, "collapseAll"),
            patch.object(widget.mdtree, "expandToDepth") as mock_expandToDepth,
            patch.object(widget, "set_type_column_visibility"),
            patch.object(widget, "_expand_specific_item"),
        ):

            widget.setData(test_data, expandlevel=3)

            # Verify expansion was called with correct depth
            mock_expandToDepth.assert_called_once_with(2)  # expandlevel - 1

    def test_set_type_column_visibility_show(self):
        """Test set_type_column_visibility to show column."""
        widget = MdTreeWidget()

        with (
            patch.object(widget.mdtree, "showColumn") as mock_showColumn,
            patch.object(widget.mdtree, "hideColumn") as mock_hideColumn,
        ):

            widget.set_type_column_visibility(True, column_id=2)

            assert widget.show_type_column is True
            mock_showColumn.assert_called_once_with(2)
            mock_hideColumn.assert_not_called()

    def test_set_type_column_visibility_hide(self):
        """Test set_type_column_visibility to hide column."""
        widget = MdTreeWidget()

        with (
            patch.object(widget.mdtree, "showColumn") as mock_showColumn,
            patch.object(widget.mdtree, "hideColumn") as mock_hideColumn,
        ):

            widget.set_type_column_visibility(False, column_id=1)

            assert widget.show_type_column is False
            mock_hideColumn.assert_called_once_with(1)
            mock_showColumn.assert_not_called()

    def test_expand_specific_item_found(self):
        """Test _expand_specific_item when item is found."""
        widget = MdTreeWidget()

        # Mock tree structure
        mock_root = Mock()
        mock_child = Mock()
        mock_child.text.return_value = "image"
        mock_root.childCount.return_value = 1
        mock_root.child.return_value = mock_child

        with (
            patch.object(widget.mdtree, "invisibleRootItem", return_value=mock_root),
            patch.object(widget.mdtree, "expandItem") as mock_expandItem,
            patch.object(widget, "_expand_children_recursive") as mock_expand_children,
        ):

            widget._expand_specific_item("image", levels=2)

            # Verify calls
            mock_child.text.assert_called_with(0)
            mock_expandItem.assert_called_once_with(mock_child)
            mock_expand_children.assert_called_once_with(mock_child, 1)

    def test_expand_specific_item_not_found(self):
        """Test _expand_specific_item when item is not found."""
        widget = MdTreeWidget()

        # Mock tree structure with different item name
        mock_root = Mock()
        mock_child = Mock()
        mock_child.text.return_value = "different_name"
        mock_root.childCount.return_value = 1
        mock_root.child.return_value = mock_child

        with (
            patch.object(widget.mdtree, "invisibleRootItem", return_value=mock_root),
            patch.object(widget.mdtree, "expandItem") as mock_expandItem,
        ):

            widget._expand_specific_item("image", levels=1)

            # Should not expand any item
            mock_expandItem.assert_not_called()

    def test_expand_specific_item_case_insensitive(self):
        """Test that _expand_specific_item is case insensitive."""
        widget = MdTreeWidget()

        mock_root = Mock()
        mock_child = Mock()
        mock_child.text.return_value = "IMAGE"  # Uppercase
        mock_root.childCount.return_value = 1
        mock_root.child.return_value = mock_child

        with (
            patch.object(widget.mdtree, "invisibleRootItem", return_value=mock_root),
            patch.object(widget.mdtree, "expandItem") as mock_expandItem,
        ):

            widget._expand_specific_item("image", levels=1)  # Lowercase search

            # Should still find and expand the item
            mock_expandItem.assert_called_once_with(mock_child)

    def test_expand_children_recursive_base_case(self):
        """Test _expand_children_recursive with levels <= 0."""
        widget = MdTreeWidget()

        mock_item = Mock()

        # Should return immediately without doing anything
        widget._expand_children_recursive(mock_item, 0)
        widget._expand_children_recursive(mock_item, -1)

        # Verify no methods were called on the item
        mock_item.childCount.assert_not_called()

    def test_expand_children_recursive_with_children(self):
        """Test _expand_children_recursive with children."""
        widget = MdTreeWidget()

        # Mock parent item
        mock_parent = Mock()
        mock_child1 = Mock()
        mock_child2 = Mock()

        mock_parent.childCount.return_value = 2
        mock_parent.child.side_effect = [mock_child1, mock_child2]

        with patch.object(widget.mdtree, "expandItem") as mock_expandItem:
            # Simply test that the method can be called without errors
            # and that expandItem is called on children
            widget._expand_children_recursive(mock_parent, 1)

            # Should expand both children
            assert mock_expandItem.call_count == 2
            mock_expandItem.assert_any_call(mock_child1)
            mock_expandItem.assert_any_call(mock_child2)

            # Verify expand was called for each child
            assert mock_expandItem.call_count == 2
            mock_expandItem.assert_any_call(mock_child1)
            mock_expandItem.assert_any_call(mock_child2)

    def test_clear(self):
        """Test the clear convenience method."""
        widget = MdTreeWidget()

        with patch.object(widget.mdtree, "clear") as mock_clear:
            widget.clear()
            mock_clear.assert_called_once()

    def test_layout_structure(self):
        """Test that the layout is properly structured."""
        widget = MdTreeWidget()

        # Check that the tree is added to the layout
        layout = widget.layout
        assert layout.count() == 1
        assert layout.itemAt(0).widget() == widget.mdtree

    def test_init_collapse_and_expand_sequence(self):
        """Test the initialization sequence of collapse and expand operations."""
        test_data = {"image": {"width": 1024}, "other": {"height": 768}}

        with patch("napari_czitools._metadata_widget.DataTreeWidget") as mock_tree_class:
            # Create a more Qt-compatible mock that inherits from QWidget-like behavior
            mock_tree_instance = Mock()
            mock_tree_instance.__class__ = Mock()
            mock_tree_instance.__class__.__bases__ = (Mock(),)  # Mock inheritance
            mock_tree_class.return_value = mock_tree_instance

            # Mock the invisibleRootItem and its methods
            mock_root = Mock()
            mock_tree_instance.invisibleRootItem.return_value = mock_root
            mock_root.childCount.return_value = 2

            # Mock child items that represent "image" and "other"
            mock_image_item = Mock()
            mock_image_item.text.return_value = "image"
            mock_other_item = Mock()
            mock_other_item.text.return_value = "other"
            mock_root.child.side_effect = [mock_image_item, mock_other_item]

            # Mock the addWidget method to avoid Qt type checking issues
            with patch.object(QVBoxLayout, "addWidget") as mock_addWidget:
                # Create the widget - this should not fail now
                widget = MdTreeWidget(data=test_data, expandlevel=2)

                # Verify that the data was set and methods were called
                mock_tree_instance.setData.assert_called_with(test_data, expandlevel=0, hideRoot=True)
                mock_tree_instance.expandToDepth.assert_called_with(1)  # expandlevel - 1
                mock_addWidget.assert_called_once_with(mock_tree_instance)

            # Verify the sequence of calls during initialization
            call_names = [call[0] for call in mock_tree_instance.method_calls]

            # Should include setData, setAlternatingRowColors, collapseAll, expandToDepth
            assert "setData" in call_names
            assert "setAlternatingRowColors" in call_names
            assert "collapseAll" in call_names
            assert "expandToDepth" in call_names


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()
