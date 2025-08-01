from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import QApplication, QSlider, QStyle, QStyleOptionSlider


class RangeSlider(QSlider):
    """A slider for ranges.

    This class provides a dual-slider for ranges, where there is a defined
    maximum and minimum, as is a normal slider, but instead of having a
    single slider value, there are 2 slider values.

    This class emits the same signals as the QSlider base class, with the exception of valueChanged
    """

    valueChanged = Signal(int, int)  # Signal to emit low and high values

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)

        self._low = self.minimum()
        self._high = self.maximum()

        self.pressed_control = QStyle.SC_None
        self.hover_control = QStyle.SC_None
        self.click_offset = 0

        # 0 for the low, 1 for the high, -1 for both
        self.active_slider = 0

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

            # Set color based on slider index
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
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

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
                self._low = self._high = new_pos  # Allow both handles to have the same value
            else:
                self._low = new_pos
        else:
            if new_pos < self._low:
                self._low = self._high = new_pos  # Allow both handles to have the same value
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

    def echo(value):
        print(value)

    app = QApplication(sys.argv)
    slider = RangeSlider(Qt.Horizontal)
    slider.setMinimum(0)
    slider.setMaximum(19)
    slider.setLow(0)
    slider.setHigh(10)
    slider.setTickPosition(QSlider.TicksBelow)
    slider.valueChanged.connect(lambda low, high: echo(f"Low: {low}, High: {high}"))
    slider.show()
    slider.raise_()
    app.exec_()
