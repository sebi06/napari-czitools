"""
Comprehensive tests for CziReaderWidget methods.

This module contains thorough tests for all methods in the CziReaderWidget class
that were not previously covered by tests. The tests are designed to work across
Linux, Windows, and macOS platforms when executed as part of GitHub Actions.

The tests cover:
- Metadata display mode changes
- Range slider reset functionality
- Type column visibility changes
- Pixel data loading button functionality
- Slider type changes and dynamic slider creation
- Metadata-based slider updates

All tests use proper mocking to avoid dependencies on external files and
include comprehensive documentation explaining their purpose.
"""

import contextlib
import os
from unittest.mock import Mock, patch

import pytest
from qtpy.QtWidgets import QApplication

from napari_czitools._doublerange_slider import LabeledDoubleRangeSliderWidget
from napari_czitools._range_widget import RangeSliderWidget
from napari_czitools._widget import CziReaderWidget, SliderType

# Check if we're running in a headless environment (like GitHub Actions)
HEADLESS = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"

# Skip GUI tests in headless environments unless xvfb is available
pytestmark = pytest.mark.skipif(
    HEADLESS and not os.environ.get("DISPLAY"), reason="GUI tests require display server (use xvfb-run in CI)"
)


@pytest.fixture(scope="session")
def qapp():
    """
    Create QApplication for tests.

    This fixture ensures that a QApplication instance exists for Qt-based testing.
    It's session-scoped to avoid recreating the application multiple times.

    Returns:
        QApplication: The Qt application instance
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def mock_viewer():
    """
    Create a mock napari viewer for testing.

    Returns:
        Mock: A mock napari viewer object that can be used in widget initialization
    """
    return Mock()


@pytest.fixture
def widget_with_double_sliders(qapp, mock_viewer):
    """
    Create a CziReaderWidget with DoubleRangeSlider type for testing.

    Args:
        qapp: Qt application fixture
        mock_viewer: Mock viewer fixture

    Returns:
        CziReaderWidget: Widget instance configured with double range sliders
    """
    return CziReaderWidget(mock_viewer, sliders=SliderType.DoubleRangeSlider)


@pytest.fixture
def widget_with_two_sliders(qapp, mock_viewer):
    """
    Create a CziReaderWidget with TwoSliders type for testing.

    Args:
        qapp: Qt application fixture
        mock_viewer: Mock viewer fixture

    Returns:
        CziReaderWidget: Widget instance configured with two separate sliders
    """
    return CziReaderWidget(mock_viewer, sliders=SliderType.TwoSliders)


class TestMetadataDisplayModeChanges:
    """Test metadata display mode switching functionality."""

    def test_mdwidget_changed_table_to_tree(self, widget_with_double_sliders):
        """
        Test switching from table to tree metadata display mode.

        This test verifies that when the metadata display is changed from table
        to tree view, the current widget is properly switched to the tree widget.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Initially should be showing table
        assert widget.current_md_widget == widget.mdtable

        # Mock the UI methods to focus on logic testing
        widget.main_layout.removeWidget = Mock()
        widget.main_layout.insertWidget = Mock()
        widget.mdtable.hide = Mock()
        widget.mdtree.show = Mock()
        widget.type_column_checkbox.show = Mock()
        widget.type_column_checkbox.hide = Mock()

        # Change to tree view
        widget.mdata_widget.value = "Tree"
        widget._mdwidget_changed()

        # Verify tree is now current
        assert widget.current_md_widget == widget.mdtree
        # Verify show() was called on the checkbox
        widget.type_column_checkbox.show.assert_called()

    def test_mdwidget_changed_tree_to_table(self, widget_with_double_sliders):
        """
        Test switching from tree to table metadata display mode.

        This test verifies that when the metadata display is changed from tree
        to table view, the appropriate widget is hidden/shown and the type column
        checkbox becomes hidden.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Start with tree view
        widget.current_md_widget = widget.mdtree
        widget.type_column_checkbox.show()

        # Change to table view
        widget.mdata_widget.value = "Table"
        widget._mdwidget_changed()

        # Verify table is now current and checkbox is hidden
        assert widget.current_md_widget == widget.mdtable
        assert not widget.type_column_checkbox.isVisible()


class TestMetadataResetFunctionality:
    """Test metadata widget reset functionality."""

    def test_reset_metadata_widgets_clears_data(self, widget_with_double_sliders):
        """
        Test that reset_metadata_widgets properly clears both tree and table widgets.

        This test ensures that when metadata widgets are reset, both the tree
        and table widgets are properly cleared of any previous data.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Mock the clear and setRowCount methods
        widget.mdtree.clear = Mock()
        widget.mdtable.setRowCount = Mock()

        # Call the reset method
        widget._reset_metadata_widgets()

        # Verify both widgets were cleared
        widget.mdtree.clear.assert_called_once()
        widget.mdtable.setRowCount.assert_called_once_with(0)


class TestRangeSliderResetFunctionality:
    """Test range slider reset functionality for both slider types."""

    def test_reset_range_sliders_double_slider_type(self, widget_with_double_sliders):
        """
        Test range slider reset for DoubleRangeSlider type.

        This test verifies that when range sliders are reset for double range
        slider type, all sliders are properly disabled and reset to default values.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Mock the slider methods for all sliders
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            slider.setEnabled = Mock()
            slider.setMinimum = Mock()
            slider.setMaximum = Mock()
            slider.setLow = Mock()
            slider.setHigh = Mock()
            slider.setVisible = Mock()

        # Call the reset method
        widget._reset_range_sliders()

        # Verify all sliders were reset properly
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            slider.setEnabled.assert_called_once_with(False)
            slider.setMinimum.assert_called_once_with(0)
            slider.setMaximum.assert_called_once_with(0)
            slider.setLow.assert_called_once_with(0)
            slider.setHigh.assert_called_once_with(0)
            slider.setVisible.assert_called_once_with(True)

    def test_reset_range_sliders_two_slider_type(self, widget_with_two_sliders):
        """
        Test range slider reset for TwoSliders type.

        This test verifies that when range sliders are reset for two slider
        type, all sliders are properly disabled and reset to default values.

        Args:
            widget_with_two_sliders: Widget fixture with two separate sliders
        """
        widget = widget_with_two_sliders

        # Mock the slider properties for all sliders
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            # Mock the enabled property
            slider.enabled = True
            # Mock the min and max sliders
            slider.min_slider = Mock()
            slider.max_slider = Mock()

        # Call the reset method
        widget._reset_range_sliders()

        # Verify all sliders were reset properly
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            assert slider.enabled is False
            # Verify min slider was reset
            assert slider.min_slider.min == 0
            assert slider.min_slider.max == 0
            assert slider.min_slider.value == 0
            # Verify max slider was reset
            assert slider.max_slider.min == 0
            assert slider.max_slider.max == 0
            assert slider.max_slider.value == 0


class TestTypeColumnVisibility:
    """Test type column visibility toggle functionality."""

    def test_type_column_changed_show_column(self, widget_with_double_sliders):
        """
        Test showing the type column in tree view.

        This test verifies that when the type column checkbox is checked,
        the tree widget properly shows the type column.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Mock the tree widget method
        widget.mdtree.set_type_column_visibility = Mock()

        # Set checkbox to checked
        widget.type_column_checkbox.setChecked(True)

        # Call the method
        widget._type_column_changed()

        # Verify the tree widget was updated correctly
        assert widget.show_type_column is True
        widget.mdtree.set_type_column_visibility.assert_called_once_with(visible=True, column_id=2)

    def test_type_column_changed_hide_column(self, widget_with_double_sliders):
        """
        Test hiding the type column in tree view.

        This test verifies that when the type column checkbox is unchecked,
        the tree widget properly hides the type column.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Mock the tree widget method
        widget.mdtree.set_type_column_visibility = Mock()

        # Set initial state directly without triggering signals
        widget.show_type_column = True

        # Set checkbox to unchecked directly
        widget.type_column_checkbox.setChecked(False)

        # Clear any previous calls to the mock that may have happened during setup
        widget.mdtree.set_type_column_visibility.reset_mock()

        # Call the method directly
        widget._type_column_changed()

        # Verify the tree widget was updated correctly
        assert widget.show_type_column is False
        widget.mdtree.set_type_column_visibility.assert_called_once_with(visible=False, column_id=2)


class TestPixelDataLoading:
    """Test pixel data loading button functionality."""

    @patch("napari_czitools._widget.reader_function_adv")
    def test_loadbutton_pressed_double_slider_type(self, mock_reader, widget_with_double_sliders):
        """
        Test pixel data loading with DoubleRangeSlider type.

        This test verifies that when the load pixel data button is pressed
        with double range sliders, the correct plane values are extracted
        and passed to the reader function.

        Args:
            mock_reader: Mock of the reader_function_adv
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Mock the _file_changed method to prevent file loading issues
        widget._file_changed = Mock()

        # Ensure we're using DoubleRangeSlider type
        widget.sliders = SliderType.DoubleRangeSlider

        # Mock the slider values
        widget.scene_slider.low = Mock(return_value=0)
        widget.scene_slider.high = Mock(return_value=2)
        widget.time_slider.low = Mock(return_value=1)
        widget.time_slider.high = Mock(return_value=3)
        widget.channel_slider.low = Mock(return_value=0)
        widget.channel_slider.high = Mock(return_value=1)
        widget.z_slider.low = Mock(return_value=2)
        widget.z_slider.high = Mock(return_value=4)

        # Set filename using the property getter approach
        # Create a mock property that returns our test filename
        test_filename = "test_file.czi"
        type(widget.filename_edit).value = property(lambda self: test_filename)

        # Call the method
        widget._loadbutton_pressed()

        # Verify reader was called with correct parameters
        expected_planes = {
            "S": (0, 2),
            "T": (1, 3),
            "C": (0, 1),
            "Z": (2, 4),
        }
        mock_reader.assert_called_once()
        call_args = mock_reader.call_args
        # Check filename by extracting the basename
        import os

        filename = os.path.basename(str(call_args[0][0]))
        assert filename == "test_file.czi"  # filename
        assert call_args[1]["planes"] == expected_planes

    @patch("napari_czitools._widget.reader_function_adv")
    def test_loadbutton_pressed_two_slider_type(self, mock_reader, widget_with_two_sliders):
        """
        Test pixel data loading with TwoSliders type.

        This test verifies that when the load pixel data button is pressed
        with two separate sliders, the correct plane values are extracted
        and passed to the reader function.

        Args:
            mock_reader: Mock of the reader_function_adv
            widget_with_two_sliders: Widget fixture with two separate sliders
        """
        widget = widget_with_two_sliders

        # Mock the _file_changed method to prevent file loading issues
        widget._file_changed = Mock()

        # Ensure we're using TwoSliders type
        widget.sliders = SliderType.TwoSliders

        # Mock the slider values for all sliders - create proper mock objects
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)

            # Create mock min/max sliders with value attributes
            min_slider_mock = Mock()
            max_slider_mock = Mock()

            # Set default values
            min_slider_mock.value = 0
            max_slider_mock.value = 0

            # Assign to the slider
            slider.min_slider = min_slider_mock
            slider.max_slider = max_slider_mock

        # Set specific values for testing
        widget.scene_slider.min_slider.value = 0
        widget.scene_slider.max_slider.value = 2
        widget.time_slider.min_slider.value = 1
        widget.time_slider.max_slider.value = 3
        widget.channel_slider.min_slider.value = 0
        widget.channel_slider.max_slider.value = 1
        widget.z_slider.min_slider.value = 2
        widget.z_slider.max_slider.value = 4

        # Set filename using the property getter approach
        # Create a mock property that returns our test filename
        test_filename = "test_file.czi"
        type(widget.filename_edit).value = property(lambda self: test_filename)

        # Call the method
        widget._loadbutton_pressed()

        # Verify reader was called with correct parameters
        expected_planes = {
            "S": (0, 2),
            "T": (1, 3),
            "C": (0, 1),
            "Z": (2, 4),
        }
        mock_reader.assert_called_once()
        call_args = mock_reader.call_args
        # Check filename by extracting the basename
        filename = os.path.basename(str(call_args[0][0]))
        assert filename == "test_file.czi"  # filename
        assert call_args[1]["planes"] == expected_planes

    @patch("napari_czitools._widget.reader_function_adv")
    def test_lazy_checkbox_default_and_reader_use_lazy(self, mock_reader, widget_with_double_sliders):
        """Verify Lazy Loading checkbox default is checked and passed to reader."""
        widget = widget_with_double_sliders

        # Default checkbox should be present and checked
        assert hasattr(widget, "lazy_loading_checkbox")
        assert widget.lazy_loading_checkbox.isChecked() is True

        # Mock file change prevention
        widget._file_changed = Mock()

        # Set filename property
        test_filename = "test_file.czi"
        type(widget.filename_edit).value = property(lambda self: test_filename)

        # Press load button (checkbox is checked) -> use_lazy True
        widget._loadbutton_pressed()
        mock_reader.assert_called()
        _, kwargs = mock_reader.call_args
        assert kwargs.get("use_lazy", None) is True

        # Now uncheck and press again
        widget.lazy_loading_checkbox.setChecked(False)
        widget._loadbutton_pressed()
        # mock_reader should have been called again; inspect last call
        _, kwargs2 = mock_reader.call_args
        assert kwargs2.get("use_lazy", None) is False


class TestSliderTypeChanges:
    """Test dynamic slider type changing functionality."""

    def test_slider_type_changed_to_double_range(self, widget_with_two_sliders):
        """
        Test changing slider type from TwoSliders to DoubleRangeSlider.

        This test verifies that when the slider type is changed from two separate
        sliders to double range sliders, the old sliders are properly removed
        and new ones are created with the correct type.

        Args:
            widget_with_two_sliders: Widget fixture with two separate sliders
        """
        widget = widget_with_two_sliders

        # Store initial slider types for verification
        initial_slider_type = type(widget.scene_slider)
        assert initial_slider_type == RangeSliderWidget

        # Mock the removal and creation methods
        widget._remove_existing_sliders = Mock()
        widget._create_sliders = Mock()
        widget._update_sliders_from_metadata = Mock()

        # Add mock metadata to trigger the update call
        widget.metadata = Mock()

        # Change to DoubleRangeSlider
        widget._slider_type_changed("DoubleRangeSlider")

        # Verify the process was followed
        assert widget.sliders == SliderType.DoubleRangeSlider
        widget._remove_existing_sliders.assert_called_once()
        widget._create_sliders.assert_called_once()
        widget._update_sliders_from_metadata.assert_called_once()

    def test_slider_type_changed_to_two_sliders(self, widget_with_double_sliders):
        """
        Test changing slider type from DoubleRangeSlider to TwoSliders.

        This test verifies that when the slider type is changed from double range
        sliders to two separate sliders, the old sliders are properly removed
        and new ones are created with the correct type.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Store initial slider type for verification
        initial_slider_type = type(widget.scene_slider)
        assert initial_slider_type == LabeledDoubleRangeSliderWidget

        # Mock the removal and creation methods
        widget._remove_existing_sliders = Mock()
        widget._create_sliders = Mock()
        widget._update_sliders_from_metadata = Mock()

        # Add mock metadata to trigger the update call
        widget.metadata = Mock()

        # Change to TwoSliders
        widget._slider_type_changed("TwoSliders")

        # Verify the process was followed
        assert widget.sliders == SliderType.TwoSliders
        widget._remove_existing_sliders.assert_called_once()
        widget._create_sliders.assert_called_once()
        widget._update_sliders_from_metadata.assert_called_once()

    def test_slider_type_changed_same_type_no_change(self, widget_with_double_sliders):
        """
        Test that changing to the same slider type does nothing.

        This test verifies that when the slider type is "changed" to the same
        type it already is, no action is taken to avoid unnecessary work.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Mock the removal and creation methods
        widget._remove_existing_sliders = Mock()
        widget._create_sliders = Mock()
        widget._update_sliders_from_metadata = Mock()

        # Try to change to the same type
        widget._slider_type_changed("DoubleRangeSlider")

        # Verify no methods were called
        widget._remove_existing_sliders.assert_not_called()
        widget._create_sliders.assert_not_called()
        widget._update_sliders_from_metadata.assert_not_called()

    def test_slider_type_changed_invalid_value(self, widget_with_double_sliders):
        """
        Test that invalid slider type values are ignored.

        This test verifies that when an invalid slider type value is provided,
        the method returns early without making any changes.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Mock the removal and creation methods
        widget._remove_existing_sliders = Mock()
        widget._create_sliders = Mock()
        widget._update_sliders_from_metadata = Mock()

        # Try to change to an invalid type
        widget._slider_type_changed("InvalidType")

        # Verify no methods were called
        widget._remove_existing_sliders.assert_not_called()
        widget._create_sliders.assert_not_called()
        widget._update_sliders_from_metadata.assert_not_called()


class TestSliderRemovalAndCreation:
    """Test slider removal and creation functionality."""

    def test_remove_existing_sliders_double_range_type(self, widget_with_double_sliders):
        """
        Test removal of existing DoubleRangeSlider type sliders.

        This test verifies that when removing double range sliders, they are
        properly removed from the layout and their parent is set to None.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Mock the layout and slider methods
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            slider.setParent = Mock()

        widget.main_layout.removeWidget = Mock()

        # Call the method
        widget._remove_existing_sliders()

        # Verify sliders were removed from layout
        assert widget.main_layout.removeWidget.call_count == 4

        # Verify slider attributes were deleted
        assert not hasattr(widget, "scene_slider")
        assert not hasattr(widget, "time_slider")
        assert not hasattr(widget, "channel_slider")
        assert not hasattr(widget, "z_slider")

    def test_remove_existing_sliders_two_slider_type(self, widget_with_two_sliders):
        """
        Test removal of existing TwoSliders type sliders.

        This test verifies that when removing two separate sliders, they are
        properly removed from the layout using their native attribute.

        Args:
            widget_with_two_sliders: Widget fixture with two separate sliders
        """
        widget = widget_with_two_sliders

        # Mock the layout and slider methods
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            slider.native.setParent = Mock()

        widget.main_layout.removeWidget = Mock()

        # Call the method
        widget._remove_existing_sliders()

        # Verify sliders were removed from layout
        assert widget.main_layout.removeWidget.call_count == 4

        # Verify slider attributes were deleted
        assert not hasattr(widget, "scene_slider")
        assert not hasattr(widget, "time_slider")
        assert not hasattr(widget, "channel_slider")
        assert not hasattr(widget, "z_slider")

    @patch("napari_czitools._widget.LabeledDoubleRangeSliderWidget")
    def test_create_sliders_double_range_type(self, mock_double_slider, widget_with_double_sliders):
        """
        Test creation of DoubleRangeSlider type sliders.

        This test verifies that when creating double range sliders, the correct
        slider types are instantiated and added to the layout.

        Args:
            mock_double_slider: Mock of LabeledDoubleRangeSliderWidget
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Remove existing sliders first
        widget._remove_existing_sliders()

        # Mock the layout method
        widget.main_layout.addWidget = Mock()

        # Create mock slider instances
        mock_slider_instance = Mock()
        mock_double_slider.return_value = mock_slider_instance

        # Call the method
        widget._create_sliders()

        # Verify sliders were created
        assert mock_double_slider.call_count == 4
        assert widget.main_layout.addWidget.call_count == 4

        # Verify sliders were assigned as attributes
        assert hasattr(widget, "scene_slider")
        assert hasattr(widget, "time_slider")
        assert hasattr(widget, "channel_slider")
        assert hasattr(widget, "z_slider")

    @patch("napari_czitools._widget.RangeSliderWidget")
    def test_create_sliders_two_slider_type(self, mock_range_slider, widget_with_two_sliders):
        """
        Test creation of TwoSliders type sliders.

        This test verifies that when creating two separate sliders, the correct
        slider types are instantiated and added to the layout.

        Args:
            mock_range_slider: Mock of RangeSliderWidget
            widget_with_two_sliders: Widget fixture with two separate sliders
        """
        widget = widget_with_two_sliders

        # Remove existing sliders first
        widget._remove_existing_sliders()

        # Mock the layout method
        widget.main_layout.addWidget = Mock()

        # Create mock slider instances with native attribute
        mock_slider_instance = Mock()
        mock_slider_instance.native = Mock()
        mock_range_slider.return_value = mock_slider_instance

        # Call the method
        widget._create_sliders()

        # Verify sliders were created
        assert mock_range_slider.call_count == 4
        assert widget.main_layout.addWidget.call_count == 4

        # Verify sliders were assigned as attributes
        assert hasattr(widget, "scene_slider")
        assert hasattr(widget, "time_slider")
        assert hasattr(widget, "channel_slider")
        assert hasattr(widget, "z_slider")


class TestMetadataSliderUpdates:
    """Test slider updates based on metadata."""

    def test_update_sliders_from_metadata_no_metadata(self, widget_with_double_sliders):
        """
        Test slider update when no metadata is available.

        This test verifies that when there is no metadata available, the
        slider update method returns early without making any changes.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Ensure no metadata is set
        if hasattr(widget, "metadata"):
            delattr(widget, "metadata")

        # Mock slider methods to verify they're not called
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            slider.setEnabled = Mock()

        # Call the method
        widget._update_sliders_from_metadata()

        # Verify no slider methods were called
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            slider.setEnabled.assert_not_called()

    def test_update_sliders_from_metadata_double_range_with_data(self, widget_with_double_sliders):
        """
        Test slider update with metadata for DoubleRangeSlider type.

        This test verifies that when metadata is available, double range sliders
        are properly updated with the correct ranges and enabled/disabled states.

        Args:
            widget_with_double_sliders: Widget fixture with double range sliders
        """
        widget = widget_with_double_sliders

        # Create mock metadata
        mock_metadata = Mock()
        mock_metadata.image = Mock()
        mock_metadata.image.SizeS = 5
        mock_metadata.image.SizeT = 10
        mock_metadata.image.SizeC = 3
        mock_metadata.image.SizeZ = 1  # Should be disabled
        widget.metadata = mock_metadata

        # Mock slider methods
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            slider.setMinimum = Mock()
            slider.setMaximum = Mock()
            slider.setLow = Mock()
            slider.setHigh = Mock()
            slider.setEnabled = Mock()
            slider.setVisible = Mock()

        # Call the method
        widget._update_sliders_from_metadata()

        # Verify scene slider (SizeS = 5, should be enabled)
        widget.scene_slider.setMinimum.assert_called_with(0)
        widget.scene_slider.setMaximum.assert_called_with(4)
        widget.scene_slider.setLow.assert_called_with(0)
        widget.scene_slider.setHigh.assert_called_with(4)
        widget.scene_slider.setEnabled.assert_called_with(True)

        # Verify time slider (SizeT = 10, should be enabled)
        widget.time_slider.setMinimum.assert_called_with(0)
        widget.time_slider.setMaximum.assert_called_with(9)
        widget.time_slider.setLow.assert_called_with(0)
        widget.time_slider.setHigh.assert_called_with(9)
        widget.time_slider.setEnabled.assert_called_with(True)

        # Verify channel slider (SizeC = 3, should be enabled)
        widget.channel_slider.setMinimum.assert_called_with(0)
        widget.channel_slider.setMaximum.assert_called_with(2)
        widget.channel_slider.setLow.assert_called_with(0)
        widget.channel_slider.setHigh.assert_called_with(2)
        widget.channel_slider.setEnabled.assert_called_with(True)

        # Verify z slider (SizeZ = 1, should be disabled)
        widget.z_slider.setEnabled.assert_called_with(False)
        widget.z_slider.setVisible.assert_called_with(False)

    def test_update_sliders_from_metadata_two_sliders_with_data(self, widget_with_two_sliders):
        """
        Test slider update with metadata for TwoSliders type.

        This test verifies that when metadata is available, two separate sliders
        are properly updated with the correct ranges and enabled/disabled states.

        Args:
            widget_with_two_sliders: Widget fixture with two separate sliders
        """
        widget = widget_with_two_sliders

        # Create mock metadata
        mock_metadata = Mock()
        mock_metadata.image = Mock()
        mock_metadata.image.SizeS = 5
        mock_metadata.image.SizeT = 10
        mock_metadata.image.SizeC = 3
        mock_metadata.image.SizeZ = 1  # Should be disabled
        widget.metadata = mock_metadata

        # Mock slider properties for all sliders
        for slider_name in ["scene_slider", "time_slider", "channel_slider", "z_slider"]:
            slider = getattr(widget, slider_name)
            slider.enabled = False
            slider.min_slider = Mock()
            slider.max_slider = Mock()

        # Call the method
        widget._update_sliders_from_metadata()

        # Verify scene slider (SizeS = 5, should be enabled)
        assert widget.scene_slider.enabled is True
        assert widget.scene_slider.min_slider.min == 0
        assert widget.scene_slider.min_slider.max == 4
        assert widget.scene_slider.max_slider.min == 0
        assert widget.scene_slider.max_slider.max == 4
        assert widget.scene_slider.min_slider.value == 0
        assert widget.scene_slider.max_slider.value == 4

        # Verify time slider (SizeT = 10, should be enabled)
        assert widget.time_slider.enabled is True
        assert widget.time_slider.min_slider.min == 0
        assert widget.time_slider.min_slider.max == 9
        assert widget.time_slider.max_slider.min == 0
        assert widget.time_slider.max_slider.max == 9
        assert widget.time_slider.min_slider.value == 0
        assert widget.time_slider.max_slider.value == 9

        # Verify channel slider (SizeC = 3, should be enabled)
        assert widget.channel_slider.enabled is True
        assert widget.channel_slider.min_slider.min == 0
        assert widget.channel_slider.min_slider.max == 2
        assert widget.channel_slider.max_slider.min == 0
        assert widget.channel_slider.max_slider.max == 2
        assert widget.channel_slider.min_slider.value == 0
        assert widget.channel_slider.max_slider.value == 2

        # Verify z slider (SizeZ = 1, should be disabled)
        assert widget.z_slider.enabled is False


if __name__ == "__main__":
    """
    Allow running tests directly when the module is executed.

    This enables developers to run these specific tests independently
    for debugging or development purposes.
    """
    import sys

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    with contextlib.suppress(SystemExit):
        pytest.main([__file__, "-v"])
