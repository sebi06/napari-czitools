"""
Tests for the _doublerange_slider module.

This module tests both the LabeledDoubleRangeSliderWidget and DoubleRangeSlider classes
to ensure proper functionality of the dual-handle range slider components.
"""

from unittest.mock import MagicMock, patch

import pytest
from qtpy.QtCore import QPoint, Qt
from qtpy.QtGui import QMouseEvent
from qtpy.QtWidgets import QApplication, QSlider

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
        widget = LabeledDoubleRangeSliderWidget(dimension_label="Test", min_value=0, max_value=5, show_label=True)

        assert hasattr(widget, "label")
        assert widget.label.text() == "Test Slider (Range: 0-5)"

    def test_init_with_readout(self):
        """Test initialization with readout enabled."""
        widget = LabeledDoubleRangeSliderWidget(dimension_label="Test", min_value=0, max_value=5, readout=True)

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

        # Test getter
        assert widget.low() == 0

        # Test setter
        widget.setLow(3)
        assert widget.low() == 3
        assert widget._low == 3

    def test_high_value_getter_setter(self):
        """Test high value getter and setter."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10)

        # Test getter
        assert widget.high() == 10

        # Test setter
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
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10, readout=True)

        # Test initial readout
        initial_text = widget.readout_label.text()
        assert "Slices:" in initial_text

        # Change values and update
        widget.setLow(2)
        widget.setHigh(5)
        widget.update_readout()

        expected_slices = widget.slice_count()
        assert f"Slices: {expected_slices}" == widget.readout_label.text()

    def test_update_readout_disabled(self):
        """Test update_readout when readout is disabled."""
        widget = LabeledDoubleRangeSliderWidget(readout=False)

        # Should not raise an error even without readout_label
        widget.update_readout()  # Should complete without error

    def test_update_label(self):
        """Test label update functionality."""
        widget = LabeledDoubleRangeSliderWidget(dimension_label="Test", min_value=0, max_value=10, show_label=True)

        # Test initial label
        initial_text = widget.label.text()
        assert "Test Slider (Range:" in initial_text

        # Update label
        widget.update_label()

        min_val = widget.minimum()
        max_val = widget.maximum()
        expected_text = f"Test Slider (Range: {min_val}-{max_val})"
        assert widget.label.text() == expected_text

    def test_update_label_disabled(self):
        """Test update_label when label is disabled."""
        widget = LabeledDoubleRangeSliderWidget(show_label=False)

        # Should not raise an error even without label
        widget.update_label()  # Should complete without error

    def test_value_changed_signal(self):
        """Test valueChanged signal emission."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10)

        # Connect signal to mock
        signal_mock = MagicMock()
        widget.valueChanged.connect(signal_mock)

        # Trigger value change through slider
        widget.slider.setLow(3)

        # Verify signal was emitted
        signal_mock.assert_called_with(3, 10)

    def test_on_value_changed(self):
        """Test internal value change handler."""
        widget = LabeledDoubleRangeSliderWidget(min_value=0, max_value=10, readout=True, show_label=True)

        # Mock the signal emission
        signal_mock = MagicMock()
        widget.valueChanged.connect(signal_mock)

        # Call the internal handler
        widget._on_value_changed(2, 8)

        # Verify values were updated
        assert widget._low == 2
        assert widget._high == 8

        # Verify signal was emitted
        signal_mock.assert_called_with(2, 8)

    def test_widget_control_methods(self):
        """Test widget control methods (setEnabled, setVisible, etc.)."""
        widget = LabeledDoubleRangeSliderWidget()

        # Test setEnabled
        widget.setEnabled(False)
        assert not widget.isEnabled()
        assert not widget.slider.isEnabled()

        widget.setEnabled(True)
        assert widget.isEnabled()
        assert widget.slider.isEnabled()

        # Test setVisible
        widget.setVisible(False)
        assert not widget.isVisible()

        widget.setVisible(True)
        assert widget.isVisible()

    def test_tick_position(self):
        """Test tick position setting."""
        widget = LabeledDoubleRangeSliderWidget()

        # Test setting tick position
        widget.setTickPosition(QSlider.TicksBelow)
        # Note: We can't easily test the actual tick position without accessing internal Qt state

    def test_minimum_maximum_methods(self):
        """Test minimum and maximum value methods."""
        widget = LabeledDoubleRangeSliderWidget(min_value=5, max_value=15)

        # Test getters
        assert widget.minimum() == 5
        assert widget.maximum() == 15

        # Test setters
        widget.setMinimum(2)
        widget.setMaximum(20)

        assert widget.minimum() == 2
        assert widget.maximum() == 20


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

        # Test getter
        assert slider.low() == 0

        # Test setter with signal emission
        signal_mock = MagicMock()
        slider.valueChanged.connect(signal_mock)

        slider.setLow(3)
        assert slider.low() == 3
        signal_mock.assert_called_with(3, 10)

    def test_high_value_getter_setter(self):
        """Test high value getter and setter."""
        slider = DoubleRangeSlider(min_value=0, max_value=10)

        # Test getter
        assert slider.high() == 10

        # Test setter with signal emission
        signal_mock = MagicMock()
        slider.valueChanged.connect(signal_mock)

        slider.setHigh(7)
        assert slider.high() == 7
        signal_mock.assert_called_with(0, 7)

    def test_paint_event(self):
        """Test paint event handling."""
        slider = DoubleRangeSlider()
        slider.setGeometry(0, 0, 200, 30)  # Set a size for the slider

        # Create a mock paint event and patch both QPainter and QApplication.style
        with (
            patch("napari_czitools._doublerange_slider.QPainter") as mock_painter,
            patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style,
        ):

            mock_painter_instance = MagicMock()
            mock_painter.return_value = mock_painter_instance

            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            # Create a mock paint event
            mock_event = MagicMock()

            # Call paintEvent - should not raise an exception
            slider.paintEvent(mock_event)

            # Verify QPainter was instantiated
            mock_painter.assert_called_once_with(slider)
            # Verify that drawing methods were called
            assert mock_style_instance.drawComplexControl.called

    def test_mouse_press_event_normal_handles(self):
        """Test mouse press event for normal handle detection."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.setGeometry(0, 0, 200, 30)  # Set a size for the slider

        # Create a mock mouse event
        with patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style:
            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            # Mock hit test to return handle hit
            mock_style_instance.hitTestComplexControl.return_value = mock_style_instance.SC_SliderHandle

            # Create mouse press event
            event = QMouseEvent(
                QMouseEvent.MouseButtonPress, QPoint(50, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier
            )

            # Call the method
            slider.mousePressEvent(event)

            # Verify event was accepted
            assert event.isAccepted()

    def test_mouse_press_event_overlapping_handles(self):
        """Test mouse press event when handles overlap."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider._low = 50
        slider._high = 50  # Overlapping handles
        slider.setGeometry(0, 0, 200, 30)

        with patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style:
            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            # Mock handle rectangle
            mock_rect = MagicMock()
            mock_rect.contains.return_value = True
            mock_rect.center.return_value.x.return_value = 100
            mock_style_instance.subControlRect.return_value = mock_rect

            # Create mouse press event (right side of handle - should select max handle)
            event = QMouseEvent(
                QMouseEvent.MouseButtonPress,
                QPoint(105, 15),  # Right of center
                Qt.LeftButton,
                Qt.LeftButton,
                Qt.NoModifier,
            )

            slider.mousePressEvent(event)

            # Should select max handle (index 1)
            assert slider.active_slider == 1

    def test_mouse_move_event_low_handle(self):
        """Test mouse move event for low handle."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = 0  # Low handle
        slider.setGeometry(0, 0, 200, 30)

        with patch.object(slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=25):
            # Create mouse move event
            event = QMouseEvent(QMouseEvent.MouseMove, QPoint(50, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

            signal_mock = MagicMock()
            slider.valueChanged.connect(signal_mock)

            slider.mouseMoveEvent(event)

            # Low value should be updated if new_pos <= high
            assert slider._low == 25
            signal_mock.assert_called()

    def test_mouse_move_event_high_handle(self):
        """Test mouse move event for high handle."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = 1  # High handle
        slider.setGeometry(0, 0, 200, 30)

        with patch.object(slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=75):
            # Create mouse move event
            event = QMouseEvent(QMouseEvent.MouseMove, QPoint(150, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

            signal_mock = MagicMock()
            slider.valueChanged.connect(signal_mock)

            slider.mouseMoveEvent(event)

            # High value should be updated if new_pos >= low
            assert slider._high == 75
            signal_mock.assert_called()

    def test_mouse_move_event_both_handles(self):
        """Test mouse move event for both handles simultaneously."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = -1  # Both handles
        slider.click_offset = 50
        slider._low = 20
        slider._high = 80
        slider.setGeometry(0, 0, 200, 30)

        with patch.object(slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=60):
            # Create mouse move event
            event = QMouseEvent(QMouseEvent.MouseMove, QPoint(120, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

            signal_mock = MagicMock()
            slider.valueChanged.connect(signal_mock)

            original_low = slider._low
            original_high = slider._high

            slider.mouseMoveEvent(event)

            # Both handles should move by the offset
            offset = 60 - 50  # new_pos - click_offset
            assert slider._low == original_low + offset
            assert slider._high == original_high + offset
            signal_mock.assert_called()

    def test_mouse_move_event_boundary_constraints(self):
        """Test mouse move event with boundary constraints."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = -1  # Both handles
        slider.click_offset = 50
        slider._low = 10
        slider._high = 90
        slider.setGeometry(0, 0, 200, 30)

        # Test moving beyond maximum
        with patch.object(slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=70):
            event = QMouseEvent(QMouseEvent.MouseMove, QPoint(140, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

            slider.mouseMoveEvent(event)

            # Should adjust to stay within bounds
            offset = 70 - 50  # 20
            expected_high = 90 + offset  # 110, but clamped
            if expected_high > 100:
                diff = expected_high - 100
                expected_low = 10 + offset - diff
                expected_high = 100
                assert slider._low == expected_low
                assert slider._high == expected_high

    def test_mouse_release_event(self):
        """Test mouse release event."""
        slider = DoubleRangeSlider()
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = 0

        # Create mouse release event
        event = QMouseEvent(QMouseEvent.MouseButtonRelease, QPoint(50, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

        slider.mouseReleaseEvent(event)

        # Should reset pressed state
        assert slider.pressed_control == slider.style().SC_None
        assert slider.active_slider == -1
        assert event.isAccepted()

    def test_pick_horizontal(self):
        """Test __pick method for horizontal orientation."""
        slider = DoubleRangeSlider()

        point = QPoint(50, 25)
        result = slider._DoubleRangeSlider__pick(point)

        # Should return x coordinate for horizontal slider
        assert result == 50

    def test_pick_vertical(self):
        """Test __pick method for vertical orientation."""
        slider = DoubleRangeSlider()
        slider.setOrientation(Qt.Vertical)

        point = QPoint(50, 25)
        result = slider._DoubleRangeSlider__pick(point)

        # Should return y coordinate for vertical slider
        assert result == 25

    def test_pixel_pos_to_range_value(self):
        """Test __pixelPosToRangeValue method."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.setGeometry(0, 0, 200, 30)

        with patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style:
            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            # Mock the style calculations
            mock_style_instance.sliderValueFromPosition.return_value = 50

            # Mock rectangles
            mock_groove_rect = MagicMock()
            mock_groove_rect.x.return_value = 10
            mock_groove_rect.right.return_value = 190

            mock_handle_rect = MagicMock()
            mock_handle_rect.width.return_value = 20

            mock_style_instance.subControlRect.side_effect = [mock_groove_rect, mock_handle_rect]

            result = slider._DoubleRangeSlider__pixelPosToRangeValue(100)

            # Should call sliderValueFromPosition with correct parameters
            mock_style_instance.sliderValueFromPosition.assert_called_once()
            assert result == 50

    def test_mouse_move_event_ignored_when_not_pressed(self):
        """Test that mouse move event is ignored when no control is pressed."""
        slider = DoubleRangeSlider()
        slider.pressed_control = slider.style().SC_None  # No control pressed

        event = QMouseEvent(QMouseEvent.MouseMove, QPoint(50, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

        slider.mouseMoveEvent(event)

        # Event should be ignored
        assert not event.isAccepted()

    def test_low_handle_movement_constraint(self):
        """Test that low handle cannot move beyond high handle."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider._low = 30
        slider._high = 70
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = 0  # Low handle

        with patch.object(
            slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=80
        ):  # Try to move beyond high
            event = QMouseEvent(QMouseEvent.MouseMove, QPoint(160, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

            original_low = slider._low
            slider.mouseMoveEvent(event)

            # Low should not change because new_pos (80) > high (70)
            assert slider._low == original_low

    def test_high_handle_movement_constraint(self):
        """Test that high handle cannot move beyond low handle."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider._low = 30
        slider._high = 70
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = 1  # High handle

        with patch.object(
            slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=20
        ):  # Try to move beyond low
            event = QMouseEvent(QMouseEvent.MouseMove, QPoint(40, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

            original_high = slider._high
            slider.mouseMoveEvent(event)

            # High should not change because new_pos (20) < low (30)
            assert slider._high == original_high

    def test_paint_event_with_tick_marks(self):
        """Test paint event with tick marks enabled."""
        slider = DoubleRangeSlider()
        slider.setTickPosition(QSlider.TicksBelow)  # Enable tick marks
        slider.setGeometry(0, 0, 200, 30)

        with (
            patch("napari_czitools._doublerange_slider.QPainter") as mock_painter,
            patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style,
        ):

            mock_painter_instance = MagicMock()
            mock_painter.return_value = mock_painter_instance

            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            mock_event = MagicMock()

            slider.paintEvent(mock_event)

            # Verify QPainter was instantiated
            mock_painter.assert_called_once_with(slider)

    def test_paint_event_pressed_control_states(self):
        """Test paint event with different pressed control states."""
        slider = DoubleRangeSlider()
        slider.setGeometry(0, 0, 200, 30)

        # Test with pressed control and active slider
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = 0

        with (
            patch("napari_czitools._doublerange_slider.QPainter") as mock_painter,
            patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style,
        ):

            mock_painter_instance = MagicMock()
            mock_painter.return_value = mock_painter_instance

            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            mock_event = MagicMock()

            slider.paintEvent(mock_event)

            # Verify QPainter was instantiated
            mock_painter.assert_called_once_with(slider)

    def test_paint_event_disabled_state(self):
        """Test paint event when slider is disabled."""
        slider = DoubleRangeSlider()
        slider.setEnabled(False)
        slider.setGeometry(0, 0, 200, 30)

        with (
            patch("napari_czitools._doublerange_slider.QPainter") as mock_painter,
            patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style,
        ):

            mock_painter_instance = MagicMock()
            mock_painter.return_value = mock_painter_instance

            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            mock_event = MagicMock()

            slider.paintEvent(mock_event)

            # Verify QPainter was instantiated
            mock_painter.assert_called_once_with(slider)

    def test_mouse_press_event_no_button(self):
        """Test mouse press event when no button is pressed."""
        slider = DoubleRangeSlider()

        # Create mouse press event with no button
        event = QMouseEvent(
            QMouseEvent.MouseButtonPress, QPoint(50, 15), Qt.NoButton, Qt.NoButton, Qt.NoModifier  # No button pressed
        )

        slider.mousePressEvent(event)

        # Event should be ignored
        assert not event.isAccepted()

    def test_mouse_press_event_no_handle_hit(self):
        """Test mouse press event when no handle is hit."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.setGeometry(0, 0, 200, 30)

        with patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style:
            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            # Mock hit test to return no handle hit
            mock_style_instance.hitTestComplexControl.return_value = mock_style_instance.SC_None

            with patch.object(slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=50):
                event = QMouseEvent(
                    QMouseEvent.MouseButtonPress, QPoint(100, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier
                )

                slider.mousePressEvent(event)

                # Should set click_offset when no handle is hit
                assert slider.click_offset == 50
                assert slider.active_slider < 0

    def test_mouse_move_event_boundary_constraints_minimum(self):
        """Test mouse move event with boundary constraints at minimum."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = -1  # Both handles
        slider.click_offset = 30
        slider._low = 10
        slider._high = 40

        # Test moving beyond minimum
        with patch.object(slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=5):  # Would move low to -15
            event = QMouseEvent(QMouseEvent.MouseMove, QPoint(10, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

            original_range = slider._high - slider._low
            slider.mouseMoveEvent(event)

            # Should adjust to stay within bounds
            assert slider._low >= 0  # Should not go below minimum
            assert slider._high - slider._low == original_range  # Range should be preserved

    def test_vertical_orientation_pick(self):
        """Test __pick method for vertical orientation."""
        slider = DoubleRangeSlider()
        slider.setOrientation(Qt.Vertical)

        point = QPoint(50, 25)
        result = slider._DoubleRangeSlider__pick(point)

        # Should return y coordinate for vertical slider
        assert result == 25

    def test_pixel_pos_to_range_value_vertical(self):
        """Test __pixelPosToRangeValue method for vertical orientation."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.setOrientation(Qt.Vertical)
        slider.setGeometry(0, 0, 30, 200)

        with patch("napari_czitools._doublerange_slider.QApplication.style") as mock_style:
            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            # Mock the style calculations for vertical
            mock_style_instance.sliderValueFromPosition.return_value = 50

            # Mock rectangles for vertical orientation
            mock_groove_rect = MagicMock()
            mock_groove_rect.y.return_value = 10
            mock_groove_rect.bottom.return_value = 190

            mock_handle_rect = MagicMock()
            mock_handle_rect.height.return_value = 20

            mock_style_instance.subControlRect.side_effect = [mock_groove_rect, mock_handle_rect]

            result = slider._DoubleRangeSlider__pixelPosToRangeValue(100)

            # Should call sliderValueFromPosition with correct parameters
            mock_style_instance.sliderValueFromPosition.assert_called_once()
            assert result == 50

    def test_mouse_move_event_boundary_maximum_adjustment(self):
        """Test mouse move event boundary adjustment when exceeding maximum."""
        slider = DoubleRangeSlider(min_value=0, max_value=100)
        slider.pressed_control = slider.style().SC_SliderHandle
        slider.active_slider = -1  # Both handles
        slider.click_offset = 70
        slider._low = 80
        slider._high = 95

        # Test moving beyond maximum
        with patch.object(
            slider, "_DoubleRangeSlider__pixelPosToRangeValue", return_value=90
        ):  # Would move high to 115
            event = QMouseEvent(QMouseEvent.MouseMove, QPoint(180, 15), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

            original_range = slider._high - slider._low
            slider.mouseMoveEvent(event)

            # Should adjust to stay within bounds
            assert slider._high <= 100  # Should not exceed maximum
            assert slider._high - slider._low == original_range  # Range should be preserved


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()
