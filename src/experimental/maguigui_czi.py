from magicgui import magicgui
from magicgui.widgets import Container, Label, Slider
from qtpy.QtWidgets import QApplication


@magicgui(layout="vertical")
def range_slider_widget(
    dimension_label: str = "Time",
    min_value: int = 0,
    max_value: int = 0,
    readout=True,
    visible: bool = True,
    enabled: bool = True,
) -> Container:
    """
    Creates a range slider widget for selecting a range of values within a specified dimension.
    This widget includes two sliders for selecting minimum and maximum values, a label displaying
    the current range, and functionality to ensure the minimum value does not exceed the maximum value.
    Parameters
    ----------
    dimension_label : str, optional
        The label for the dimension being adjusted (default is "Time").
    min_value : int, optional
        The minimum value for the sliders (default is 0).
    max_value : int, optional
        The maximum value for the sliders (default is 0).
    readout : bool, optional
        Whether to display the current value of the sliders (default is True).
    visible : bool, optional
        Whether the sliders and label are visible (default is True).
    enabled : bool, optional
        Whether the sliders are enabled for interaction (default is True).
    Returns
    -------
    Container
        A container widget holding the range label and the two sliders.
    Notes
    -----
    - The `min_slider` and `max_slider` are connected to an update function that ensures
    `min_slider.value` does not exceed `max_slider.value` and vice versa.
    - The range label dynamically updates to display the number of slices based on the
    difference between the maximum and minimum slider values.
    """

    # Create a label to display the current range
    range_label = Label(value=f"{dimension_label} Slices: {max_value - min_value + 1}")

    # Create two sliders for min and max
    min_slider = Slider(
        label="Min", min=min_value, max=max_value, value=min_value, readout=readout, visible=visible, enabled=enabled
    )
    max_slider = Slider(
        label="Max", min=min_value, max=max_value, value=max_value, readout=readout, visible=visible, enabled=enabled
    )

    # Update the range label and ensure min <= max
    def update_range():
        min_val = min_slider.value
        max_val = max_slider.value

        # Allow min and max to overlap
        if min_val > max_val:
            max_slider.value = min_val  # Adjust max to match min
        elif max_val < min_val:
            min_slider.value = max_val  # Adjust min to match max

        # Update the label
        range_label.value = f"Num Slices: {max_slider.value - min_slider.value + 1}"

    # Connect the sliders to the update function
    min_slider.changed.connect(update_range)
    max_slider.changed.connect(update_range)

    # Create a container to hold the sliders and the label
    container = Container(widgets=[range_label, min_slider, max_slider])

    return container


# Run the application for testing
if __name__ == "__main__":
    app = QApplication([])
    widget = range_slider_widget(dimension_label="Time", min_value=0, max_value=9, visible=True, enabled=True)
    widget.show()
    app.exec_()
