from magicgui import magicgui
from magicgui.widgets import Slider, Label, Container
from qtpy.QtWidgets import QApplication


@magicgui(
    layout="vertical",
)
def range_slider_widget():
    # Create a label to display the current range
    range_label = Label(value="Range: 2 - 2")

    # Create two sliders for min and max
    min_slider = Slider(label="Min", min=0, max=9, value=2)
    max_slider = Slider(label="Max", min=0, max=9, value=2)

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
        range_label.value = f"Range: {min_slider.value} - {max_slider.value}"

    # Connect the sliders to the update function
    min_slider.changed.connect(update_range)
    max_slider.changed.connect(update_range)

    # Create a container to hold the sliders and the label
    container = Container(widgets=[range_label, min_slider, max_slider])
    return container


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    widget = range_slider_widget()
    widget.show()
    app.exec_()
