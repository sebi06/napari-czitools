# the code for this widegt is inspired by:
# https://github.com/sleepbysleep/range_slider_for_Qt5_and_PyQt5/blob/master/pyqt5_ranger_slider/range_slider.py
#
# https://www.mail-archive.com/pyqt@riverbankcomputing.com/msg22889.html

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QVBoxLayout,
    QWidget,
)


class LabeledDoubleRangeSliderWidget(QWidget):
    """A complete widget that includes both label and double range slider with unified visibility control.

    This widget combines a DoubleRangeSlider with optional label and readout display,
    providing a complete UI component for range selection with visual feedback.

    Attributes:
        valueChanged: Signal emitted when slider values change, passes (low, high) values
    """

    valueChanged = Signal(int, int)  # Signal to emit low and high values

    def __init__(
        self,
        dimension_label: str = "Range",
        min_value: int = 0,
        max_value: int = 10,
        enabled: bool = True,
        readout: bool = True,
        visible: bool = True,
        show_label: bool = True,
    ) -> None:
        """Initialize the labeled double range slider widget.

        Args:
            dimension_label: Label text for the slider
            min_value: Minimum value for the slider range
            max_value: Maximum value for the slider range
            enabled: Whether the slider is enabled for interaction
            readout: Whether to show slice count readout
            visible: Whether the widget is initially visible
            show_label: Whether to show the dimension label
        """
        super().__init__()

        self.dimension_label: str = dimension_label
        self.show_label: bool = show_label
        self.readout_enabled: bool = readout

        # Initialize slider values
        self._low: int = min_value
        self._high: int = max_value

        # Create the main layout
        layout = QVBoxLayout()

        # Create and add the label if requested
        if show_label:
            self.label = QLabel(
                f"{dimension_label} Slider (Range: {min_value}-{max_value})"
            )
            layout.addWidget(self.label)

        # Create horizontal layout for slider and readout
        slider_layout = QHBoxLayout()

        # Create the slider
        self.slider = DoubleRangeSlider(
            dimension_label=dimension_label,
            min_value=min_value,
            max_value=max_value,
            enabled=enabled,
        )
        slider_layout.addWidget(self.slider)

        # Create the readout label if requested
        if readout:
            self.readout_label = QLabel()
            self.readout_label.setMinimumWidth(80)
            self.readout_label.setAlignment(Qt.AlignCenter)
            self.update_readout()
            slider_layout.addWidget(self.readout_label)

        slider_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(slider_layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set overall visibility and enabled state
        self.setVisible(visible)
        self.setEnabled(enabled)

        # Connect slider signals
        self.slider.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, low: int, high: int) -> None:
        """Handle value changes from the slider.

        Args:
            low: New low value from the slider
            high: New high value from the slider
        """
        self._low = low
        self._high = high
        if self.readout_enabled:
            self.update_readout()
        self.valueChanged.emit(low, high)

    def update_readout(self) -> None:
        """Update the readout label with current slice count."""
        if self.readout_enabled and hasattr(self, "readout_label"):
            slice_count = self.slice_count()
            self.readout_label.setText(f"Slices: {slice_count}")

    def update_label(self) -> None:
        """Update the main label with current range information."""
        if self.show_label and hasattr(self, "label"):
            min_val = self.minimum()
            max_val = self.maximum()
            self.label.setText(
                f"{self.dimension_label} Slider (Range: {min_val}-{max_val})"
            )

    # Slider value methods
    def low(self) -> int:
        """Get the current low value.

        Returns:
            Current low value of the slider
        """
        return self._low

    def setLow(self, low: int) -> None:
        """Set the low value of the slider.

        Args:
            low: New low value to set
        """
        self._low = low
        self.slider.setLow(low)

    def high(self) -> int:
        """Get the current high value.

        Returns:
            Current high value of the slider
        """
        return self._high

    def setHigh(self, high: int) -> None:
        """Set the high value of the slider.

        Args:
            high: New high value to set
        """
        self._high = high
        self.slider.setHigh(high)

    def slice_count(self) -> int:
        """Return the number of slices: max - min + 1.

        Returns:
            Number of slices in the current range
        """
        return self._high - self._low + 1

    # Widget control methods
    def setEnabled(self, enabled: bool) -> None:
        """Set the enabled state of the widget and its slider.

        Args:
            enabled: Whether the widget should be enabled
        """
        super().setEnabled(enabled)
        self.slider.setEnabled(enabled)

    def setVisible(self, visible: bool) -> None:
        """Set the visibility of the entire labeled slider widget.

        Arg:
            visible: Whether the widget should be visible
        """
        super().setVisible(visible)

    def setTickPosition(self, position) -> None:
        """Set the tick position for the slider.

        Args:
            position: Tick position constant from QSlider
        """
        self.slider.setTickPosition(position)

    def minimum(self) -> int:
        """Get the minimum value of the slider.

        Returns:
            Minimum value of the slider range
        """
        return self.slider.minimum()

    def maximum(self) -> int:
        """Get the maximum value of the slider.

        Returns:
            Maximum value of the slider range
        """
        return self.slider.maximum()

    def setMinimum(self, minimum: int) -> None:
        """Set the minimum value of the slider.

        Args:
            minimum: New minimum value for the slider
        """
        self.slider.setMinimum(minimum)
        self.update_label()

    def setMaximum(self, maximum: int) -> None:
        """Set the maximum value of the slider.

        Args:
            maximum: New maximum value for the slider
        """
        self.slider.setMaximum(maximum)
        self.update_label()


class DoubleRangeSlider(QSlider):
    """A slider widget with dual handles for selecting a range of values.

    This custom slider allows users to select both minimum and maximum values
    within a range using two draggable handles. The handles are color-coded:
    blue for the minimum value and red for the maximum value.

    Attributes:
        valueChanged: Signal emitted when either handle value changes, passes (low, high) values
    """

    valueChanged = Signal(int, int)  # Signal to emit low and high values

    def __init__(
        self,
        dimension_label: str = "Range",
        min_value: int = 0,
        max_value: int = 10,
        enabled: bool = True,
    ) -> None:
        """Initialize the double range slider.
        Args:
            dimension_label: Label text describing what the slider controls
            min_value: Minimum value for the slider range
            max_value: Maximum value for the slider range
            enabled: Whether the slider is enabled for interaction
        """
        super().__init__(Qt.Horizontal)

        self.dimension_label: str = dimension_label
        self._low: int = min_value
        self._high: int = max_value

        self.setMinimum(min_value)
        self.setMaximum(max_value)
        self.setEnabled(enabled)

        self.pressed_control: QStyle.SubControl = QStyle.SC_None
        self.hover_control: QStyle.SubControl = QStyle.SC_None
        self.click_offset: int = 0
        self.active_slider: int = 0  # 0 for low, 1 for high, -1 for both

    def low(self) -> int:
        """Get the current low (minimum) value.
        Returns:
            Current low value of the slider
        """
        return self._low

    def setLow(self, low: int) -> None:
        """Set the low (minimum) value of the slider.
        Args:
            low: New low value to set
        """
        self._low = low
        self.update()
        self.valueChanged.emit(self._low, self._high)

    def high(self) -> int:
        """Get the current high (maximum) value.
        Returns:
            Current high value of the slider
        """
        return self._high

    def setHigh(self, high: int) -> None:
        """Set the high (maximum) value of the slider.

        Args:
            high: New high value to set
        """
        self._high = high
        self.update()
        self.valueChanged.emit(self._low, self._high)

    def paintEvent(self, event) -> None:
        """Custom paint event to draw the slider with dual colored handles.
        Draws the slider groove, tick marks (if enabled), and two colored handles:
        blue for the minimum value and red for the maximum value.

        Args:
            event: Paint event from Qt
        """
        painter = QPainter(self)
        style = QApplication.style()

        # First draw the groove/track
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.subControls = QStyle.SC_SliderGroove
        if self.tickPosition() != self.NoTicks:
            opt.subControls |= QStyle.SC_SliderTickmarks
        style.drawComplexControl(QStyle.CC_Slider, opt, painter, self)

        # Now draw the colored handles
        for i, value in enumerate([self._low, self._high]):
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            opt.subControls = QStyle.SC_SliderHandle

            if self.pressed_control and (
                (self.active_slider == i) or (self.active_slider == -1)
            ):
                opt.activeSubControls = self.pressed_control
                opt.state |= QStyle.State_Sunken
            else:
                opt.activeSubControls = self.hover_control

            opt.sliderPosition = value
            opt.sliderValue = value

            # Get the handle rectangle
            handle_rect = style.subControlRect(
                QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
            )

            # Set color based on enabled state and slider index
            if not self.isEnabled():
                # Gray when disabled
                painter.fillRect(handle_rect, QColor(128, 128, 128))
            else:
                # Colored when enabled
                if i == 0:  # Min slider - Blue
                    painter.fillRect(handle_rect, QColor(0, 100, 255))
                else:  # Max slider - Red
                    painter.fillRect(handle_rect, QColor(255, 50, 50))

            # Draw a border around the handle
            painter.setPen(QColor(0, 0, 0))
            painter.drawRect(handle_rect)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press events to detect which handle was clicked.

        Determines which handle (low, high, or both) should be activated
        based on the mouse click position.

        Args:
            event: Mouse press event from Qt
        """
        event.accept()
        style = QApplication.style()
        button = event.button()

        if button:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            self.active_slider = -1

            for i, value in enumerate([self._low, self._high]):
                opt.sliderPosition = value
                hit = style.hitTestComplexControl(
                    QStyle.CC_Slider, opt, event.pos(), self
                )
                if hit == QStyle.SC_SliderHandle:
                    self.active_slider = i
                    self.pressed_control = hit
                    self.triggerAction(self.SliderMove)
                    self.setRepeatAction(self.SliderNoAction)
                    self.setSliderDown(True)
                    break

            if self.active_slider < 0:
                self.pressed_control = QStyle.SC_SliderHandle
                self.click_offset = self.__pixelPosToRangeValue(
                    self.__pick(event.pos())
                )
                self.triggerAction(self.SliderMove)
                self.setRepeatAction(self.SliderNoAction)
        else:
            event.ignore()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move events for dragging slider handles.

        This method handles the dragging behavior for both individual handles and
        simultaneous movement of both handles. It ensures that:
        - The low value never exceeds the high value
        - Both values stay within the slider's minimum and maximum bounds
        - When dragging both handles simultaneously, they maintain their relative positions

        Args:
            event: Mouse move event from Qt containing the current mouse position
        """
        if self.pressed_control != QStyle.SC_SliderHandle:
            event.ignore()
            return

        event.accept()
        new_pos: int = self.__pixelPosToRangeValue(self.__pick(event.pos()))

        if self.active_slider < 0:
            # Moving both sliders simultaneously
            offset: int = new_pos - self.click_offset
            self._high += offset
            self._low += offset

            # Ensure bounds are respected when moving both handles
            if self._low < self.minimum():
                diff: int = self.minimum() - self._low
                self._low += diff
                self._high += diff
            if self._high > self.maximum():
                diff: int = self.maximum() - self._high
                self._low += diff
                self._high += diff
        elif self.active_slider == 0:
            # Moving the low (minimum) handle
            if new_pos > self._high:
                # If low handle is dragged past high handle, merge them
                self._low = self._high = new_pos
            else:
                self._low = new_pos
        else:
            # Moving the high (maximum) handle
            if new_pos < self._low:
                # If high handle is dragged past low handle, merge them
                self._low = self._high = new_pos
            else:
                self._high = new_pos

        self.click_offset = new_pos
        self.update()
        self.valueChanged.emit(self._low, self._high)

    def __pick(self, pt) -> int:
        """Extract the relevant coordinate from a point based on slider orientation.

        For horizontal sliders, returns the x-coordinate. For vertical sliders,
        returns the y-coordinate. This is used internally for mouse position
        calculations during handle dragging.

        Args:
            pt: QPoint object containing mouse coordinates

        Returns:
            The relevant coordinate (x for horizontal, y for vertical) as an integer
        """
        if self.orientation() == Qt.Horizontal:
            return pt.x()
        else:
            return pt.y()

    def __pixelPosToRangeValue(self, pos: int) -> int:
        """Convert pixel position to slider value within the valid range.

        This method converts a pixel position on the slider to its corresponding
        value within the slider's range. It accounts for the slider's orientation,
        groove dimensions, and handle size to provide accurate position-to-value
        mapping for mouse interactions.

        Args:
            pos: Pixel position along the slider's primary axis (x for horizontal,
                 y for vertical sliders)

        Returns:
            The slider value corresponding to the given pixel position, clamped
            to the slider's minimum and maximum range
        """
        opt: QStyleOptionSlider = QStyleOptionSlider()
        self.initStyleOption(opt)
        style: QStyle = QApplication.style()

        gr: object = style.subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self
        )
        sr: object = style.subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
        )

        if self.orientation() == Qt.Horizontal:
            slider_length: int = sr.width()
            slider_min: int = gr.x()
            slider_max: int = gr.right() - slider_length + 1
        else:
            slider_length: int = sr.height()
            slider_min: int = gr.y()
            slider_max: int = gr.bottom() - slider_length + 1

        return style.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            pos - slider_min,
            slider_max - slider_min,
            opt.upsideDown,
        )


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

    def echo(low, high):
        print(f"Low: {low}, High: {high}")

    def toggle_visibility():
        """Toggle the visibility of the complete labeled slider."""
        labeled_slider.setVisible(not labeled_slider.isVisible())
        toggle_button.setText(
            f"{'Show' if not labeled_slider.isVisible() else 'Hide'} Labeled Slider"
        )

    app = QApplication(sys.argv)

    # Test the complete labeled slider widget
    labeled_slider = LabeledDoubleRangeSliderWidget(
        dimension_label="Time",
        min_value=0,
        max_value=19,
        enabled=True,
        readout=True,
        visible=True,
        show_label=True,
    )
    labeled_slider.setLow(0)
    labeled_slider.setHigh(19)
    labeled_slider.setTickPosition(QSlider.TicksBelow)
    labeled_slider.valueChanged.connect(echo)

    # Create a main widget
    widget = QWidget()
    layout = QVBoxLayout()

    layout.addWidget(labeled_slider)

    toggle_button = QPushButton("Hide Labeled Slider")
    toggle_button.clicked.connect(toggle_visibility)
    layout.addWidget(toggle_button)

    widget.setLayout(layout)

    widget.show()
    widget.raise_()
    app.exec_()
