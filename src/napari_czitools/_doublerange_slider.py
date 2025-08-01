from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import QApplication, QHBoxLayout, QLabel, QSlider, QStyle, QStyleOptionSlider, QVBoxLayout, QWidget


class LabeledDoubleRangeSliderWidget(QWidget):
    """A complete widget that includes both label and double range slider with unified visibility control."""

    valueChanged = Signal(int, int)  # Signal to emit low and high values

    def __init__(
        self,
        dimension_label="Range",
        min_value=0,
        max_value=10,
        enabled=True,
        readout=True,
        visible=True,
        show_label=True,
    ):
        super().__init__()

        self.dimension_label = dimension_label
        self.show_label = show_label
        self.readout_enabled = readout

        # Initialize slider values
        self._low = min_value
        self._high = max_value

        # Create the main layout
        layout = QVBoxLayout()

        # Create and add the label if requested
        if show_label:
            self.label = QLabel(f"{dimension_label} Slider (Range: {min_value}-{max_value})")
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

    def _on_value_changed(self, low, high):
        """Handle value changes from the slider."""
        self._low = low
        self._high = high
        if self.readout_enabled:
            self.update_readout()
        self.valueChanged.emit(low, high)

    def update_readout(self):
        """Update the readout label with current slice count."""
        if self.readout_enabled and hasattr(self, "readout_label"):
            slice_count = self.slice_count()
            self.readout_label.setText(f"Slices: {slice_count}")

    def update_label(self):
        """Update the main label with current range information."""
        if self.show_label and hasattr(self, "label"):
            min_val = self.minimum()
            max_val = self.maximum()
            self.label.setText(f"{self.dimension_label} Slider (Range: {min_val}-{max_val})")

    # Slider value methods
    def low(self):
        return self._low

    def setLow(self, low):
        self._low = low
        self.slider.setLow(low)

    def high(self):
        return self._high

    def setHigh(self, high):
        self._high = high
        self.slider.setHigh(high)

    def slice_count(self):
        """Return the number of slices: max - min + 1"""
        return self._high - self._low + 1

    # Widget control methods
    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.slider.setEnabled(enabled)

    def setVisible(self, visible):
        """Set the visibility of the entire labeled slider widget."""
        super().setVisible(visible)

    def setTickPosition(self, position):
        self.slider.setTickPosition(position)

    def minimum(self):
        return self.slider.minimum()

    def maximum(self):
        return self.slider.maximum()

    def setMinimum(self, minimum):
        self.slider.setMinimum(minimum)
        self.update_label()

    def setMaximum(self, maximum):
        self.slider.setMaximum(maximum)
        self.update_label()


class DoubleRangeSlider(QSlider):
    """A slider for ranges with dual handles."""

    valueChanged = Signal(int, int)  # Signal to emit low and high values

    def __init__(
        self,
        dimension_label="Range",
        min_value=0,
        max_value=10,
        enabled=True,
    ):
        super().__init__(Qt.Horizontal)

        self.dimension_label = dimension_label
        self._low = min_value
        self._high = max_value

        self.setMinimum(min_value)
        self.setMaximum(max_value)
        self.setEnabled(enabled)

        self.pressed_control = QStyle.SC_None
        self.hover_control = QStyle.SC_None
        self.click_offset = 0
        self.active_slider = 0  # 0 for low, 1 for high, -1 for both

    def low(self):
        return self._low

    def setLow(self, low):
        self._low = low
        self.update()
        self.valueChanged.emit(self._low, self._high)

    def high(self):
        return self._high

    def setHigh(self, high):
        self._high = high
        self.update()
        self.valueChanged.emit(self._low, self._high)

    def paintEvent(self, event):
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

            if self.pressed_control and ((self.active_slider == i) or (self.active_slider == -1)):
                opt.activeSubControls = self.pressed_control
                opt.state |= QStyle.State_Sunken
            else:
                opt.activeSubControls = self.hover_control

            opt.sliderPosition = value
            opt.sliderValue = value

            # Get the handle rectangle
            handle_rect = style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

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

    def mousePressEvent(self, event):
        event.accept()
        style = QApplication.style()
        button = event.button()

        if button:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            self.active_slider = -1

            for i, value in enumerate([self._low, self._high]):
                opt.sliderPosition = value
                hit = style.hitTestComplexControl(QStyle.CC_Slider, opt, event.pos(), self)
                if hit == QStyle.SC_SliderHandle:
                    self.active_slider = i
                    self.pressed_control = hit
                    self.triggerAction(self.SliderMove)
                    self.setRepeatAction(self.SliderNoAction)
                    self.setSliderDown(True)
                    break

            if self.active_slider < 0:
                self.pressed_control = QStyle.SC_SliderHandle
                self.click_offset = self.__pixelPosToRangeValue(self.__pick(event.pos()))
                self.triggerAction(self.SliderMove)
                self.setRepeatAction(self.SliderNoAction)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.pressed_control != QStyle.SC_SliderHandle:
            event.ignore()
            return

        event.accept()
        new_pos = self.__pixelPosToRangeValue(self.__pick(event.pos()))

        if self.active_slider < 0:
            offset = new_pos - self.click_offset
            self._high += offset
            self._low += offset
            if self._low < self.minimum():
                diff = self.minimum() - self._low
                self._low += diff
                self._high += diff
            if self._high > self.maximum():
                diff = self.maximum() - self._high
                self._low += diff
                self._high += diff
        elif self.active_slider == 0:
            if new_pos > self._high:
                self._low = self._high = new_pos
            else:
                self._low = new_pos
        else:
            if new_pos < self._low:
                self._low = self._high = new_pos
            else:
                self._high = new_pos

        self.click_offset = new_pos
        self.update()
        self.valueChanged.emit(self._low, self._high)

    def __pick(self, pt):
        if self.orientation() == Qt.Horizontal:
            return pt.x()
        else:
            return pt.y()

    def __pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = QApplication.style()

        gr = style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        sr = style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1

        return style.sliderValueFromPosition(
            self.minimum(), self.maximum(), pos - slider_min, slider_max - slider_min, opt.upsideDown
        )


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

    def echo(low, high):
        print(f"Low: {low}, High: {high}")

    def toggle_visibility():
        """Toggle the visibility of the complete labeled slider."""
        labeled_slider.setVisible(not labeled_slider.isVisible())
        toggle_button.setText(f"{'Show' if not labeled_slider.isVisible() else 'Hide'} Labeled Slider")

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
