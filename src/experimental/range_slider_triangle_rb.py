from qtpy.QtCore import QPoint, QRect, Qt, Signal
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QStylePainter,
    QVBoxLayout,
    QWidget,
)


class DoubleHandleSlider(QSlider):
    """A QSlider with two handles (min and max) that allows overlapping values."""

    valueChanged = Signal(int, int)  # Signal to emit min and max values

    def __init__(self, min_value: int = 0, max_value: int = 1, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)

        # Initialize the min and max handles
        self.min_value = min_value
        self.max_value = max_value
        self.setMinimum(min_value)
        self.setMaximum(max_value)

        # Set default step size
        self.setSingleStep(1)

        # Set a fixed height for the slider
        self.setFixedHeight(40)

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

    # def paintEvent(self, event):
    #     """Custom paint event to draw the slider with two handles."""
    #     painter = QStylePainter(self)
    #     opt = QStyleOptionSlider()
    #     self.initStyleOption(opt)

    #     # Draw the groove
    #     opt.subControls = QStyle.SC_SliderGroove
    #     painter.drawComplexControl(QStyle.CC_Slider, opt)

    #     # Draw the range between the two handles
    #     groove_rect = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
    #     handle_min_pos = self.valueToPixelPos(self.min_value)
    #     handle_max_pos = self.valueToPixelPos(self.max_value)
    #     range_rect = QRect(handle_min_pos, groove_rect.top(), handle_max_pos - handle_min_pos, groove_rect.height())
    #     painter.fillRect(range_rect, self.palette().highlight())

    #     # Draw the min handle
    #     opt.subControls = QStyle.SC_SliderHandle
    #     opt.sliderPosition = self.min_value
    #     painter.drawComplexControl(QStyle.CC_Slider, opt)

    #     # Draw the max handle
    #     opt.sliderPosition = self.max_value
    #     painter.drawComplexControl(QStyle.CC_Slider, opt)

    def paintEvent(self, event):
        """Custom paint event to draw the slider with increased height."""
        painter = QPainter(self)
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        # Draw the groove with increased height
        opt.subControls = QStyle.SC_SliderGroove
        groove_rect = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        groove_rect.setHeight(20)  # Increase the groove height
        painter.fillRect(groove_rect, self.palette().dark().color())

        # Draw the range between the two handles
        handle_min_pos = self.valueToPixelPos(self.min_value)
        handle_max_pos = self.valueToPixelPos(self.max_value)
        range_rect = QRect(handle_min_pos, groove_rect.top(), handle_max_pos - handle_min_pos, groove_rect.height())
        painter.fillRect(range_rect, self.palette().highlight())

        # Draw the min handle as a upward-facing triangle
        min_handle_rect = self._handleRect(self.min_value)
        min_triangle = [
            min_handle_rect.center() + QPoint(-10, 20),
            min_handle_rect.center() + QPoint(10, 20),
            min_handle_rect.center() + QPoint(0, 0),
        ]
        painter.setBrush(Qt.blue)  # Set color for the min handle to blue
        painter.setPen(Qt.blue)
        painter.drawPolygon(min_triangle)

        # Draw the max handle as an downward-facing triangle
        max_handle_rect = self._handleRect(self.max_value)
        max_triangle = [
            max_handle_rect.center() + QPoint(-10, -20),
            max_handle_rect.center() + QPoint(10, -20),
            max_handle_rect.center() + QPoint(0, 0),
        ]
        painter.setBrush(Qt.red)  # Set color for the max handle to red
        painter.setPen(Qt.red)
        painter.drawPolygon(max_triangle)

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

    def __init__(self, dimension_label="Time", min_value=0, max_value=0, readout=True, visible=True, enabled=True):
        super().__init__()

        self.setWindowTitle("Range Slider with Two Handles")
        self.resize(400, 200)

        self.dimension_label = dimension_label

        # Create the range slider
        self.range_slider = DoubleHandleSlider(min_value=min_value, max_value=max_value, orientation=Qt.Horizontal)
        self.range_slider.min_value = min_value
        self.range_slider.max_value = max_value
        self.range_slider.visible = visible
        self.range_slider.enabled = enabled
        self.range_slider.setValues(min_value=self.range_slider.min_value, max_value=self.range_slider.max_value)
        self.range_slider.setStyleSheet("border: 1px solid red;")

        # Create a label to display the current range
        self.range_label = QLabel(
            f"{self.dimension_label} Slices: {self.range_slider.max_value - self.range_slider.min_value + 1}"
        )

        # Create a readout label to display the current range values
        self.readout_label = QLabel(f"{self.range_slider.min_value} - {self.range_slider.max_value}")
        self.readout_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        # Update the layout to place the label and readout above the slider
        label_layout = QHBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        label_layout.setSpacing(0)  # Add spacing between label and readout
        label_layout.addWidget(self.range_label)
        label_layout.addWidget(self.readout_label)

        slider_layout = QVBoxLayout()
        slider_layout.addLayout(label_layout)
        slider_layout.addWidget(self.range_slider)
        slider_layout.setSpacing(0)  # Reduce space between slider layout and label layout

        self.setLayout(slider_layout)

        # Connect the range slider's valueChanged signal
        self.range_slider.valueChanged.connect(self.update_label)

    def update_label(self):
        """Update the label and readout with the current range."""
        self.range_label.setText(
            f"{self.dimension_label} Slices: {self.range_slider.max_value - self.range_slider.min_value + 1}"
        )
        self.readout_label.setText(f"{self.range_slider.min_value} - {self.range_slider.max_value}")


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    demo = RangeSliderDemo(dimension_label="Time", min_value=0, max_value=99, visible=True, enabled=True)
    demo.show()
    app.exec_()
