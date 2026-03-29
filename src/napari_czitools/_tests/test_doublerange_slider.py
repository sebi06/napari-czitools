"""
Tests for the _doublerange_slider module.

This module tests both the LabeledDoubleRangeSliderWidget and DoubleRangeSlider
classes which now wrap superqt's QLabeledRangeSlider and QRangeSlider.
"""

from unittest.mock import MagicMock

import pytest
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from napari_czitools._doublerange_slider import (
    DoubleRangeSlider,
    LabeledDoubleRangeSliderWidget,
)


class TestLabeledDoubleRangeSliderWidget:
    """Test class for LabeledDoubleRangeSliderWidget."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        widget = LabeledDoubleRangeSliderWidget()

        assert widget.dimension_label == "Range"
        assert widget.show_label is True
        assert widget.readout_enabled is True
        assert widget._low == 0
        assert widget._high == 10
        assert widget.isVisible() is True
        assert widget.isEnabled() is True

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        widget = LabeledDoubleRangeSliderWidget(
            dimension_label="Time",
            min_value=5,
            max_value=20,
            enabled=False,
            readout=False,
            visible=False,
            show_label=False,
        )

        assert widget.dimension_label == "Time"
        assert widget.show_label is False
        assert widget.readout_enabled is False
        assert widget._low == 5
        assert widget._high == 20
        assert widget.isVisible() is False
        assert widget.isEnabled() is False

    def test_init_with_label(self):
        """Test initialization with label enabled."""
        widget = LabeledDoubleRangeSliderWidget(
            dimension_label="Test",
            min_value=0,
            max_value=5,
            show_label=True,
        )

        assert hasattr(widget, "label")
        assert widget.label.text() == "Test Slider (Range: 0-5)"

    def test_init_with_readout(self):
        """Test initialization with readout enabled."""
        widget = LabeledDoubleRangeSliderWidget(
            dimension_label="Test",
            min_value=0,
            max_value=5,
            readout=True,
        )

        assert hasattr(widget, "readout_label")
        assert "Slices:" in widget.readout_label.text()

    def test_init_without_label(self):
        """Test initialization without label."""
        widget = LabeledDoubleRangeSliderWidget(show_label=False)

        assert not hasattr(widget, "label")

    def test_init_without_readout(self):
        """Test initialization without readout."""
        widget = LabeledDoubleRangeSliderWidget(readout=False)

        assert not hasattr(widget, "readout_label")

    def test_low_value_getter_setter(self):
        """Test low value getter and setter."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10)

        assert widget.low() == 0

        widget.setLow(3)
        assert widget.low() == 3
        assert widget._low == 3

    def test_high_value_getter_setter(self):
        """Test high value getter and setter."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10)

        assert widget.high() == 10

        widget.setHigh(7)
        assert widget.high() == 7
        assert widget._high == 7

    def test_slice_count(self):
        """Test slice count calculation."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10)

        # Default range (0-10)
        assert widget.slice_count() == 11  # 10 - 0 + 1

        # Set custom range
        widget.setLow(3)
        widget.setHigh(7)
        assert widget.slice_count() == 5  # 7 - 3 + 1

    def test_update_readout(self):
        """Test readout update functionality."""
        widget = LabeledDoubleRangeSliderWidget(
            min_value=0, max_value=10, readout=True,
        )

        initial_text = widget.readout_label.text()
        assert "Slices:" in initial_text

        widget.setLow(2)
        widget.setHigh(5)
        widget.update_readout()

        expected_slices = widget.slice_count()
        assert f"Slices: {expected_slices}" == widget.readout_label.text()

    def test_update_readout_disabled(self):
        """Test update_readout when readout is disabled."""
        widget = LabeledDoubleRangeSliderWidget(readout=False)

        # Should not raise an error even without readout_label
        widget.update_readout()

    def test_update_label(self):
        """Test label update functionality."""
        widget = LabeledDoubleRangeSliderWidget(
            dimension_label="Test",
            min_value=0,
            max_value=10,
            show_label=True,
        )

        initial_text = widget.label.text()
        assert "Test Slider (Range:" in initial_text

        widget.update_label()

        min_val = widget.minimum()
        max_val = widget.maximum()
        expected_text = f"Test Slider (Range: {min_val}-{max_val})"
        assert widget.label.text() == expected_text

    def test_update_label_disabled(self):
        """Test update_label when label is disabled."""
        widget = LabeledDoubleRangeSliderWidget(show_label=False)

        # Should not raise an error even without label
        widget.update_label()

    def test_value_changed_signal(self):
        """Test valueChanged signal emission."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10)

        signal_mock = MagicMock()
        widget.valueChanged.connect(signal_mock)

        # Trigger value change through setLow
        widget.setLow(3)

        signal_mock.assert_called_with(3, 10)

    def test_on_value_changed(self):
        """Test internal value change handler."""
        widget = LabeledDoubleRangeSliderWidget(
            min_value=0, max_value=10, readout=True, show_label=True,
        )

        signal_mock = MagicMock()
        widget.valueChanged.connect(signal_mock)

        # Simulate an internal value change from the slider
        widget._on_value_changed((2, 8))

        assert widget._low == 2
        assert widget._high == 8

        signal_mock.assert_called_with(2, 8)

    def test_widget_control_methods(self):
        """Test widget control methods (setEnabled, setVisible, etc.)."""
        widget = LabeledDoubleRangeSliderWidget()

        widget.setEnabled(False)
        assert not widget.isEnabled()
        assert not widget.slider.isEnabled()

        widget.setEnabled(True)
        assert widget.isEnabled()
        assert widget.slider.isEnabled()

        widget.setVisible(False)
        assert not widget.isVisible()

        widget.setVisible(True)
        assert widget.isVisible()

    def test_minimum_maximum_methods(self):
        """Test minimum and maximum value methods."""
        widget = LabeledDoubleRangeSliderWidget(min_value=5, max_value=15)

        assert widget.minimum() == 5
        assert widget.maximum() == 15

        widget.setMinimum(2)
        widget.setMaximum(20)

        assert widget.minimum() == 2
        assert widget.maximum() == 20

    def test_single_value_mode(self):
        """Test single value mode via setProperty and setSingleValueMode."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10)

        # Not enabled by default
        assert widget._single_value_mode is False

        # Enable via setSingleValueMode
        widget.setSingleValueMode(True)
        assert widget._single_value_mode is True

        # Disable
        widget.setSingleValueMode(False)
        assert widget._single_value_mode is False

        # Enable via setProperty
        widget.setProperty("single_value_mode", True)
        assert widget._single_value_mode is True

    def test_single_value_mode_snaps_handles(self):
        """Test that single value mode snaps both handles together."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10)
        widget.setLow(0)
        widget.setHigh(10)
        widget.setSingleValueMode(True)

        # Simulate a change where user moves low handle
        widget._on_value_changed((5, 10))

        assert widget._low == 5
        assert widget._high == 5


class TestDoubleRangeSlider:
    """Test class for DoubleRangeSlider."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        slider = DoubleRangeSlider()

        assert slider.dimension_label == "Range"
        assert slider._low == 0
        assert slider._high == 10
        assert slider.minimum() == 0
        assert slider.maximum() == 10
        assert slider.isEnabled() is True

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        slider = DoubleRangeSlider(
            dimension_label="Custom",
            min_value=5,
            max_value=25,
            enabled=False,
        )

        assert slider.dimension_label == "Custom"
        assert slider._low == 5
        assert slider._high == 25
        assert slider.minimum() == 5
        assert slider.maximum() == 25
        assert slider.isEnabled() is False

    def test_low_value_getter_setter(self):
        """Test low value getter and setter."""
        slider = DoubleRangeSlider(min_value=0, max_value=10)

        assert slider.low() == 0

        signal_mock = MagicMock()
        slider.valueChanged.connect(signal_mock)

        slider.setLow(3)
        assert slider.low() == 3
        signal_mock.assert_called_with(3, 10)

    def test_high_value_getter_setter(self):
        """Test high value getter and setter."""
        slider = DoubleRangeSlider(min_value=0, max_value=10)

        assert slider.high() == 10

        signal_mock = MagicMock()
        slider.valueChanged.connect(signal_mock)

        slider.setHigh(7)
        assert slider.high() == 7
        signal_mock.assert_called_with(0, 7)

    def test_minimum_maximum(self):
        """Test minimum and maximum getters and setters."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)

        assert slider.minimum() == 0
        assert slider.maximum() == 100

        slider.setMinimum(10)
        slider.setMaximum(50)

        assert slider.minimum() == 10
        assert slider.maximum() == 50

    def test_single_value_mode_attribute(self):
        """Test the single_value_mode attribute."""
        slider = DoubleRangeSlider(min_value=0, max_value=10)

        assert slider.single_value_mode is False

        slider.single_value_mode = True
        assert slider.single_value_mode is True

    def test_single_value_mode_snaps_via_signal(self):
        """Test that single value mode snaps handles together on change."""
        slider = DoubleRangeSlider(min_value=0, max_value=10)
        slider.setLow(0)
        slider.setHigh(10)
        slider.single_value_mode = True

        signal_mock = MagicMock()
        slider.valueChanged.connect(signal_mock)

        # Simulate internal change where low moved to 5
        slider._on_values_changed((5, 10))

        assert slider.low() == 5
        assert slider.high() == 5
        signal_mock.assert_called_with(5, 5)

    def test_orientation(self):
        """Test orientation getter and setter."""
        slider = DoubleRangeSlider()

        assert slider.orientation() == Qt.Horizontal

        slider.setOrientation(Qt.Vertical)
        assert slider.orientation() == Qt.Vertical

    def test_value_changed_signal_on_set_low(self):
        """Test that valueChanged signal is emitted when low is set."""
        slider = DoubleRangeSlider(min_value=0, max_value=10)

        signal_mock = MagicMock()
        slider.valueChanged.connect(signal_mock)

        slider.setLow(4)
        signal_mock.assert_called_with(4, 10)

    def test_value_changed_signal_on_set_high(self):
        """Test that valueChanged signal is emitted when high is set."""
        slider = DoubleRangeSlider(min_value=0, max_value=10)

        signal_mock = MagicMock()
        slider.valueChanged.connect(signal_mock)

        slider.setHigh(6)
        signal_mock.assert_called_with(0, 6)

    def test_equal_low_high_values(self):
        """Test setting low and high to the same value (single selection)."""
        slider = DoubleRangeSlider(min_value=0, max_value=10)

        slider.setLow(5)
        slider.setHigh(5)

        assert slider.low() == 5
        assert slider.high() == 5

    def test_enabled_disabled(self):
        """Test enable/disable state."""
        slider = DoubleRangeSlider(min_value=0, max_value=10, enabled=True)
        assert slider.isEnabled() is True

        slider.setEnabled(False)
        assert slider.isEnabled() is False

        slider.setEnabled(True)
        assert slider.isEnabled() is True


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()
