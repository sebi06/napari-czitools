from qtpy.QtWidgets import (
    QApplication,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QWidget,
    QVBoxLayout,
    QLabel,
    QStylePainter,
)
from qtpy.QtCore import Qt, QRect, Signal


class DoubleHandleSlider(QSlider):
    """A QSlider with two handles (min and max) that allows overlapping values."""

    valueChanged = Signal(int, int)  # Signal to emit min and max values

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)

        # Initialize the min and max handles
        self.min_value = 2
        self.max_value = 2
        self.setMinimum(0)
        self.setMaximum(9)

        # Set default step size
        self.setSingleStep(1)

    def setValues(self, min_value, max_value):
        """Set the values of the two handles."""
        self.min_value = max(self.minimum(), min(min_value, self.maximum()))
        self.max_value = max(self.minimum(), min(max_value, self.maximum()))
        self.update()
        self.valueChanged.emit(self.min_value, self.max_value)

    def getValues(self):
        """Get the current values of the two handles."""
        return self.min_value, self.max_value

    def mousePressEvent(self, event):
        """Handle mouse press events to determine which handle to move."""
        if event.button() == Qt.LeftButton:
            handle_clicked = self._whichHandleClicked(event.pos())
            if handle_clicked == "min":
                self._active_handle = "min"
            elif handle_clicked == "max":
                self._active_handle = "max"
            else:
                self._active_handle = None

    def mouseMoveEvent(self, event):
        """Handle mouse move events to move the active handle."""
        if self._active_handle == "min":
            new_value = self.pixelPosToValue(event.pos())
            self.setValues(new_value, max(new_value, self.max_value))
        elif self._active_handle == "max":
            new_value = self.pixelPosToValue(event.pos())
            self.setValues(min(new_value, self.min_value), new_value)

    def paintEvent(self, event):
        """Custom paint event to draw the slider with two handles."""
        painter = QStylePainter(self)
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        # Draw the groove
        opt.subControls = QStyle.SC_SliderGroove
        painter.drawComplexControl(QStyle.CC_Slider, opt)

        # Draw the range between the two handles
        groove_rect = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        handle_min_pos = self.valueToPixelPos(self.min_value)
        handle_max_pos = self.valueToPixelPos(self.max_value)
        range_rect = QRect(handle_min_pos, groove_rect.top(), handle_max_pos - handle_min_pos, groove_rect.height())
        painter.fillRect(range_rect, self.palette().highlight())

        # Draw the min handle
        opt.subControls = QStyle.SC_SliderHandle
        opt.sliderPosition = self.min_value
        painter.drawComplexControl(QStyle.CC_Slider, opt)

        # Draw the max handle
        opt.sliderPosition = self.max_value
        painter.drawComplexControl(QStyle.CC_Slider, opt)

    def _whichHandleClicked(self, pos):
        """Determine which handle (min or max) was clicked."""
        min_handle_rect = self._handleRect(self.min_value)
        max_handle_rect = self._handleRect(self.max_value)

        if min_handle_rect.contains(pos):
            return "min"
        elif max_handle_rect.contains(pos):
            return "max"
        return None

    def _handleRect(self, value):
        """Get the rectangle of the handle for a given value."""
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.sliderPosition = value
        handle_rect = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        return handle_rect

    def valueToPixelPos(self, value):
        """Convert a slider value to a pixel position."""
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        groove_rect = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        slider_min = self.minimum()
        slider_max = self.maximum()
        return groove_rect.left() + (groove_rect.width() * (value - slider_min)) // (slider_max - slider_min)

    def pixelPosToValue(self, pos):
        """Convert a pixel position to a slider value."""
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        groove_rect = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        slider_min = self.minimum()
        slider_max = self.maximum()
        pixel_pos = pos.x() - groove_rect.left()
        return slider_min + (pixel_pos * (slider_max - slider_min)) // groove_rect.width()


class RangeSliderDemo(QWidget):
    """Demo widget to showcase the DoubleHandleSlider."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Range Slider with Two Handles")
        self.resize(400, 200)

        # Create the range slider
        self.range_slider = DoubleHandleSlider()
        self.range_slider.setValues(2, 2)

        # Create a label to display the current range
        self.range_label = QLabel("Range: 2 - 2")

        # Connect the range slider's valueChanged signal
        self.range_slider.valueChanged.connect(self.update_label)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.range_slider)
        layout.addWidget(self.range_label)
        self.setLayout(layout)

    def update_label(self, min_val, max_val):
        """Update the label with the current range."""
        self.range_label.setText(f"Range: {min_val} - {max_val}")


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    demo = RangeSliderDemo()
    demo.show()
    app.exec_()
