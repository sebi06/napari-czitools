from magicgui.widgets import Container, Label, Slider

# from qtpy.QtWidgets import QApplication


class RangeSliderWidget:
    """
    A widget for selecting a range of values using two sliders (min and max) and displaying the number of slices.
    Attributes:
        dimension_label (str): Label for the dimension being adjusted (e.g., "Time").
        min_value (int): Minimum value for the range slider.
        max_value (int): Maximum value for the range slider.
        readout (bool): Whether to display the current value of the sliders.
        visible (bool): Whether the sliders and label are visible.
        enabled (bool): Whether the sliders are enabled for interaction.
        range_label (Label): A label displaying the number of slices in the selected range.
        min_slider (Slider): A slider for selecting the minimum value of the range.
        max_slider (Slider): A slider for selecting the maximum value of the range.
        container (Container): A container holding the label and sliders.
    Methods:
        update_range():
            Updates the range label based on the current values of the sliders.
            Ensures that the minimum slider value does not exceed the maximum slider value and vice versa.
        show():
            Displays the widget container.
    """

    def __init__(
        self,
        dimension_label="Time",
        min_value=0,
        max_value=0,
        readout=True,
        visible=True,
        enabled=True,
    ):
        self.dimension_label = dimension_label
        self.min_value = min_value
        self.max_value = max_value
        self.readout = readout
        self.visible = visible
        self._enabled = enabled  # Store as private attribute
        self._single_value_mode = (
            False  # Flag to force both sliders to move together
        )

        # Create widgets
        self.range_label = Label(
            value=f"{dimension_label} Slices: {max_value - min_value + 1}"
        )
        self.min_slider = Slider(
            label="Min",
            min=min_value,
            max=max_value,
            value=min_value,
            readout=readout,
            visible=visible,
            enabled=enabled,
        )
        self.max_slider = Slider(
            label="Max",
            min=min_value,
            max=max_value,
            value=max_value,
            readout=readout,
            visible=visible,
            enabled=enabled,
        )

        # Connect sliders to update function
        self.min_slider.changed.connect(self.update_range)
        self.max_slider.changed.connect(self.update_range)

        # Create container
        self.container = Container(
            widgets=[self.range_label, self.min_slider, self.max_slider]
        )
        self.container.visible = visible
        self.container.enabled = enabled

    def update_range(self):
        # If in single value mode, keep min and max synchronized
        if self._single_value_mode:
            # When either slider changes, set both to the same value
            min_val = self.min_slider.value
            max_val = self.max_slider.value

            # Determine which slider was moved by comparing to stored values
            # Use whichever value is different from the stored value
            if min_val != self.min_value:
                # Min slider was moved, use its value
                new_value = min_val
            elif max_val != self.max_value:
                # Max slider was moved, use its value
                new_value = max_val
            else:
                # No change detected, keep current values
                new_value = self.min_value

            # Temporarily disconnect signals to avoid feedback loops
            self.min_slider.changed.disconnect(self.update_range)
            self.max_slider.changed.disconnect(self.update_range)

            try:
                if self.min_slider.value != new_value:
                    self.min_slider.value = new_value
                if self.max_slider.value != new_value:
                    self.max_slider.value = new_value

                # Update stored values for next comparison
                self.min_value = new_value
                self.max_value = new_value
            finally:
                # Reconnect signals
                self.min_slider.changed.connect(self.update_range)
                self.max_slider.changed.connect(self.update_range)

            # Update label - always show 1 slice since min == max
            self.range_label.value = f"{self.dimension_label} Slices: 1"
            return

        min_val = self.min_slider.value
        max_val = self.max_slider.value

        # Ensure min <= max
        if min_val > max_val:
            self.max_slider.value = min_val
        elif max_val < min_val:
            self.min_slider.value = max_val

        # Update label
        self.range_label.value = (
            f"{self.dimension_label} Slices: {max_val - min_val + 1}"
        )

    @property
    def enabled(self):
        """Get the enabled state of the widget."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Set the enabled state of the widget and update all components."""
        self._enabled = value
        self.container.enabled = value
        self.min_slider.enabled = value
        self.max_slider.enabled = value

    def lock_values(self, min_val: int, max_val: int):
        """Enable single value mode where both sliders move together as one."""
        self.min_value = min_val
        self.max_value = max_val
        self.min_slider.value = min_val
        self.max_slider.value = max_val
        self._single_value_mode = True

    def unlock_values(self):
        """Disable single value mode to allow independent min/max selection."""
        self._single_value_mode = False

    @property
    def native(self):
        """Expose the native Qt widget of the container."""
        return self.container.native

    def show(self):
        self.container.show()
