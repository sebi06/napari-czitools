"""Range slider widgets using superqt's multi-handle slider components.

This module provides range slider widgets for selecting a range of values
(or a single value as a degenerate range like 3-3) using superqt's
QRangeSlider and QLabeledRangeSlider instead of a custom QSlider subclass.
"""

import types
from typing import Any, Sequence

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from superqt import QLabeledRangeSlider, QRangeSlider


def _allow_handle_overlap(slider: QRangeSlider) -> None:
    """Patch a QRangeSlider to allow handles at the same position.

    By default superqt's ``QRangeSlider`` enforces a minimum distance
    of ``singleStep()`` between adjacent handles.  This prevents
    single-value selection (e.g. setting both handles to 3 to extract
    a single frame).  The patch replaces the internal
    ``_neighbor_bound`` method with one that uses zero minimum distance
    so both handles can occupy the same value.

    Args:
        slider: The QRangeSlider instance to patch.  For a
            ``QLabeledRangeSlider`` pass its ``._slider`` attribute.
    """

    def _neighbor_bound(self: QRangeSlider, val: float, index: int) -> float:
        # Allow handles to sit at the same position (zero gap)
        # instead of enforcing singleStep() separation.
        _lst = self._position
        if index > 0:
            val = max(_lst[index - 1], val)
        if index < (len(_lst) - 1):
            val = min(_lst[index + 1], val)
        return val

    slider._neighbor_bound = types.MethodType(_neighbor_bound, slider)  # type: ignore[attr-defined]


class LabeledDoubleRangeSliderWidget(QWidget):
    """A widget with dimension label, QLabeledRangeSlider, and slice readout.

    Uses superqt's QLabeledRangeSlider internally for the dual-handle
    range selection, adding a dimension label and a slice count readout.

    Attributes:
        valueChanged: Signal emitted when slider values change,
            passes (low, high) values.
    """

    valueChanged = Signal(int, int)

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
            dimension_label: Label text for the slider.
            min_value: Minimum value for the slider range.
            max_value: Maximum value for the slider range.
            enabled: Whether the slider is enabled for interaction.
            readout: Whether to show slice count readout.
            visible: Whether the widget is initially visible.
            show_label: Whether to show the dimension label.
        """
        super().__init__()

        self.dimension_label: str = dimension_label
        self.show_label: bool = show_label
        self.readout_enabled: bool = readout

        self._low: int = min_value
        self._high: int = max_value
        self._single_value_mode: bool = False
        self._updating: bool = False

        layout = QVBoxLayout()

        if show_label:
            self.label = QLabel(f"{dimension_label} Slider" f" (Range: {min_value}-{max_value})")
            layout.addWidget(self.label)

        slider_layout = QHBoxLayout()

        self.slider = QLabeledRangeSlider(Qt.Horizontal)
        _allow_handle_overlap(self.slider._slider)
        self.slider.setMinimum(min_value)
        self.slider.setMaximum(max_value)
        self.slider.setValue((min_value, max_value))
        slider_layout.addWidget(self.slider)

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

        self.setVisible(visible)
        self.setEnabled(enabled)

        self.slider.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, values: tuple[int, ...]) -> None:
        """Handle value changes from the QLabeledRangeSlider.

        Args:
            values: Tuple of (low, high) from the slider.
        """
        if self._updating:
            return

        low, high = int(values[0]), int(values[1])

        if self._single_value_mode and low != high:
            new_val = low if low != self._low else high
            self._low = new_val
            self._high = new_val
            self._updating = True
            self.slider.setValue((new_val, new_val))
            self._updating = False
            if self.readout_enabled:
                self.update_readout()
            self.valueChanged.emit(new_val, new_val)
            return

        self._low = low
        self._high = high
        if self.readout_enabled:
            self.update_readout()
        self.valueChanged.emit(low, high)

    def update_readout(self) -> None:
        """Update the readout label and dimension label text.

        If readout is enabled, updates the readout label to display the
        current slice count.  If the label is shown, updates it with
        the current slider range.
        """
        if self.readout_enabled and hasattr(self, "readout_label"):
            slice_count = self.slice_count()
            self.readout_label.setText(f"Slices: {slice_count}")
        if self.show_label and hasattr(self, "label"):
            self.label.setText(f"{self.dimension_label} Slider" f" (Range: {self._low}-{self._high})")

    def update_label(self) -> None:
        """Update the dimension label with current min/max range."""
        if self.show_label and hasattr(self, "label"):
            min_val = self.minimum()
            max_val = self.maximum()
            self.label.setText(f"{self.dimension_label} Slider" f" (Range: {min_val}-{max_val})")

    def low(self) -> int:
        """Get the current low value.

        Returns:
            Current low value of the slider.
        """
        return self._low

    def setLow(self, low: int) -> None:
        """Set the low value of the slider.

        Args:
            low: New low value to set.
        """
        self._low = low
        self._updating = True
        self.slider.setValue((low, self._high))
        self._updating = False
        if self.readout_enabled:
            self.update_readout()
        self.valueChanged.emit(self._low, self._high)

    def high(self) -> int:
        """Get the current high value.

        Returns:
            Current high value of the slider.
        """
        return self._high

    def setHigh(self, high: int) -> None:
        """Set the high value of the slider.

        Args:
            high: New high value to set.
        """
        self._high = high
        self._updating = True
        self.slider.setValue((self._low, high))
        self._updating = False
        if self.readout_enabled:
            self.update_readout()
        self.valueChanged.emit(self._low, self._high)

    def slice_count(self) -> int:
        """Return the number of slices: high - low + 1.

        Returns:
            Number of slices in the current range.
        """
        return self._high - self._low + 1

    def setEnabled(self, enabled: bool) -> None:
        """Set the enabled state of the widget and its slider.

        Args:
            enabled: Whether the widget should be enabled.
        """
        super().setEnabled(enabled)
        self.slider.setEnabled(enabled)

    def setVisible(self, visible: bool) -> None:
        """Set the visibility of the entire widget.

        Args:
            visible: Whether the widget should be visible.
        """
        super().setVisible(visible)

    def setTickPosition(self, position: QSlider.TickPosition) -> None:
        """Set the tick position for the slider.

        Args:
            position: Tick position constant from QSlider.
        """
        self.slider.setTickPosition(position)

    def minimum(self) -> int:
        """Get the minimum value of the slider.

        Returns:
            Minimum value of the slider range.
        """
        return self.slider.minimum()

    def maximum(self) -> int:
        """Get the maximum value of the slider.

        Returns:
            Maximum value of the slider range.
        """
        return self.slider.maximum()

    def setMinimum(self, minimum: int) -> None:
        """Set the minimum value of the slider.

        Args:
            minimum: New minimum value for the slider.
        """
        self.slider.setMinimum(minimum)

    def setMaximum(self, maximum: int) -> None:
        """Set the maximum value of the slider.

        Args:
            maximum: New maximum value for the slider.
        """
        self.slider.setMaximum(maximum)

    def setSingleValueMode(self, enabled: bool) -> None:
        """Set the slider to single value mode.

        When enabled, both handles move together so only a single
        value can be selected (e.g. 3-3).

        Args:
            enabled: Whether to enable single value mode.
        """
        self._single_value_mode = enabled

    def setProperty(self, name: str, value: Any) -> None:
        """Override setProperty to handle custom properties.

        Intercepts ``"single_value_mode"`` to toggle single-value
        mode; all other property names are forwarded to QWidget.

        Args:
            name: Property name.
            value: Property value.
        """
        if name == "single_value_mode":
            self.setSingleValueMode(bool(value))
        else:
            super().setProperty(name, value)


class DoubleRangeSlider(QWidget):
    """A dual-handle range slider using superqt's QRangeSlider.

    This wraps QRangeSlider to provide a backwards-compatible API with
    named low/high accessors and a valueChanged signal that emits two
    individual int arguments.

    Attributes:
        valueChanged: Signal emitted when handle values change,
            passes (low, high).
    """

    valueChanged = Signal(int, int)

    def __init__(
        self,
        dimension_label: str = "Range",
        min_value: int = 0,
        max_value: int = 10,
        enabled: bool = True,
    ) -> None:
        """Initialize the double range slider.

        Args:
            dimension_label: Label for the slider dimension.
            min_value: Minimum value for the slider range.
            max_value: Maximum value for the slider range.
            enabled: Whether the slider is enabled for interaction.
        """
        super().__init__()

        self.dimension_label: str = dimension_label
        self.single_value_mode: bool = False
        self._low: int = min_value
        self._high: int = max_value
        self._updating: bool = False

        self._slider = QRangeSlider(Qt.Horizontal)
        _allow_handle_overlap(self._slider)
        self._slider.setMinimum(min_value)
        self._slider.setMaximum(max_value)
        self._slider.setValue((min_value, max_value))

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._slider)
        self.setLayout(layout)
        self.setEnabled(enabled)

        self._slider.valueChanged.connect(self._on_values_changed)

    def _on_values_changed(self, values: tuple[int, ...]) -> None:
        """Handle value changes from the internal QRangeSlider.

        Args:
            values: Tuple of (low, high) values from QRangeSlider.
        """
        if self._updating:
            return

        low, high = int(values[0]), int(values[1])

        if self.single_value_mode and low != high:
            new_val = low if low != self._low else high
            self._low = new_val
            self._high = new_val
            self._updating = True
            self._slider.setValue((new_val, new_val))
            self._updating = False
            self.valueChanged.emit(new_val, new_val)
            return

        self._low = low
        self._high = high
        self.valueChanged.emit(low, high)

    def low(self) -> int:
        """Get the current low value."""
        return self._low

    def setLow(self, low: int) -> None:
        """Set the low value of the slider."""
        self._low = low
        self._updating = True
        self._slider.setValue((low, self._high))
        self._updating = False
        self.valueChanged.emit(self._low, self._high)

    def high(self) -> int:
        """Get the current high value."""
        return self._high

    def setHigh(self, high: int) -> None:
        """Set the high value of the slider."""
        self._high = high
        self._updating = True
        self._slider.setValue((self._low, high))
        self._updating = False
        self.valueChanged.emit(self._low, self._high)

    def minimum(self) -> int:
        """Get the minimum value."""
        return self._slider.minimum()

    def maximum(self) -> int:
        """Get the maximum value."""
        return self._slider.maximum()

    def setMinimum(self, minimum: int) -> None:
        """Set the minimum value."""
        self._slider.setMinimum(minimum)

    def setMaximum(self, maximum: int) -> None:
        """Set the maximum value."""
        self._slider.setMaximum(maximum)

    def setTickPosition(self, position: QSlider.TickPosition) -> None:
        """Set the tick position."""
        self._slider.setTickPosition(position)

    def tickPosition(self) -> QSlider.TickPosition:
        """Get the tick position."""
        return self._slider.tickPosition()

    def setOrientation(self, orientation: Qt.Orientation) -> None:
        """Set the slider orientation."""
        self._slider.setOrientation(orientation)

    def orientation(self) -> Qt.Orientation:
        """Get the slider orientation."""
        return self._slider.orientation()


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication, QPushButton

    def echo(low, high):
        print(f"Low: {low}, High: {high}")

    def toggle_visibility():
        """Toggle the visibility of the complete labeled slider."""
        labeled_slider.setVisible(not labeled_slider.isVisible())
        toggle_button.setText(f"{'Show' if not labeled_slider.isVisible() else 'Hide'}" " Labeled Slider")

    app = QApplication(sys.argv)

    min_value = 0
    max_value = 9

    labeled_slider = LabeledDoubleRangeSliderWidget(
        dimension_label="Time",
        min_value=min_value,
        max_value=max_value,
        enabled=True,
        readout=True,
        visible=True,
        show_label=True,
    )
    labeled_slider.setLow(min_value)
    labeled_slider.setHigh(max_value)
    labeled_slider.valueChanged.connect(echo)

    widget = QWidget()
    layout = QVBoxLayout()

    layout.addWidget(labeled_slider)

    toggle_button = QPushButton("Hide Labeled Slider")
    toggle_button.clicked.connect(toggle_visibility)
    layout.addWidget(toggle_button)

    widget.setLayout(layout)
    widget.show()
    sys.exit(app.exec_())
