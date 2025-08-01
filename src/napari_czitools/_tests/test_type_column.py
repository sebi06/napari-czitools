import pytest
from qtpy.QtWidgets import QApplication

from napari_czitools._metadata_widget import MdTreeWidget
from napari_czitools._widget import CziReaderWidget, SliderType


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_mdtree_type_column(qapp):
    """Test the type column visibility functionality."""

    # Test data
    test_data = {
        "image": {"SizeX": 1024, "SizeY": 1024, "SizeZ": 10, "SizeC": 3, "SizeT": 1},
        "metadata": {"CreationDate": "2024-01-01", "Software": "Test Software"},
    }

    # Test with type column visible (default)
    tree_widget_visible = MdTreeWidget(data=test_data, show_type_column=True)
    assert hasattr(tree_widget_visible, "set_type_column_visibility"), "set_type_column_visibility method missing"
    assert tree_widget_visible.show_type_column, "Type column should be visible by default"

    # Test with type column hidden
    tree_widget_hidden = MdTreeWidget(data=test_data, show_type_column=False)
    assert tree_widget_hidden.show_type_column is False, "Type column should be hidden"

    # Test toggling visibility - use correct method signature
    tree_widget_visible.set_type_column_visibility(visible=False)
    assert tree_widget_visible.show_type_column is False, "Type column should be hidden after toggle"

    tree_widget_visible.set_type_column_visibility(visible=True)
    assert tree_widget_visible.show_type_column is True, "Type column should be visible after toggle"


def test_widget_integration(qapp):
    """Test the CziReaderWidget integration."""

    # Test that the widget can be created with type column control
    widget = CziReaderWidget(None, sliders=SliderType.DoubleRangeSlider, show_type_column=False)
    assert hasattr(widget, "show_type_column"), "show_type_column attribute missing"
    assert hasattr(widget, "type_column_checkbox"), "type_column_checkbox attribute missing"
    assert hasattr(widget, "_type_column_changed"), "_type_column_changed method missing"


if __name__ == "__main__":
    # Run tests manually if executed directly
    import sys

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        print("Testing MdTreeWidget type column functionality...")
        test_mdtree_type_column(app)
        print("✅ MdTreeWidget test passed")

        print("Testing CziReaderWidget integration...")
        test_widget_integration(app)
        print("✅ CziReaderWidget test passed")

        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
