import os

import pytest

from napari_czitools._range_widget import RangeSliderWidget

# Check if we're running in a headless environment (like GitHub Actions)
HEADLESS = (
    os.environ.get("CI") == "true"
    or os.environ.get("GITHUB_ACTIONS") == "true"
)

# Skip GUI tests in headless environments unless xvfb is available
pytestmark = pytest.mark.skipif(
    HEADLESS and not os.environ.get("DISPLAY"),
    reason="GUI tests require display server (use xvfb-run in CI)",
)


@pytest.fixture
def widget():
    return RangeSliderWidget(
        dimension_label="Time",
        min_value=0,
        max_value=10,
        readout=True,
        visible=True,
        enabled=True,
    )


def test_initial_values(widget):
    assert widget.dimension_label == "Time"
    assert widget.min_value == 0
    assert widget.max_value == 10
    assert widget.range_label.value == "Time Slices: 11"
    assert widget.min_slider.value == 0
    assert widget.max_slider.value == 10


def test_update_range_min_exceeds_max(widget):
    widget.min_slider.value = 8
    widget.max_slider.value = 5
    widget.update_range()
    assert widget.max_slider.value == 8
    assert widget.min_slider.value == 8
    assert widget.range_label.value == "Time Slices: 1"


def test_update_range_max_below_min(widget):
    widget.max_slider.value = 2
    widget.min_slider.value = 5
    widget.update_range()
    assert widget.min_slider.value == 5
    assert widget.range_label.value == "Time Slices: 1"


def test_update_range_valid_values(widget):
    widget.min_slider.value = 3
    widget.max_slider.value = 7
    widget.update_range()
    assert widget.range_label.value == "Time Slices: 5"


def test_enabled_property(widget):
    """Test that the enabled property properly controls all components."""
    # Test initial enabled state
    assert widget.enabled is True
    assert widget.container.enabled is True
    assert widget.min_slider.enabled is True
    assert widget.max_slider.enabled is True

    # Test disabling
    widget.enabled = False
    assert widget.enabled is False
    assert widget.container.enabled is False
    assert widget.min_slider.enabled is False
    assert widget.max_slider.enabled is False

    # Test re-enabling
    widget.enabled = True
    assert widget.enabled is True
    assert widget.container.enabled is True
    assert widget.min_slider.enabled is True
    assert widget.max_slider.enabled is True


def test_visibility_and_enabled(widget):
    assert widget.min_slider.visible is True
    assert widget.max_slider.visible is True
    assert widget.min_slider.enabled is True
    assert widget.max_slider.enabled is True


def test_lock_values(widget):
    """Test that lock_values enables single value mode where both sliders move together."""
    # Enable single value mode with both values at 2
    widget.lock_values(2, 2)

    # Verify that values are set and mode is enabled
    assert widget.min_slider.value == 2
    assert widget.max_slider.value == 2
    assert widget._single_value_mode is True

    # Try to change the min slider value to 4
    widget.min_slider.value = 4
    widget.update_range()
    # Both should be synced to 4
    assert widget.min_slider.value == 4
    assert widget.max_slider.value == 4
    assert widget.range_label.value == "Time Slices: 1"

    # Try to change the max slider value to 7
    widget.max_slider.value = 7
    widget.update_range()
    # Both should be synced to 7
    assert widget.min_slider.value == 7
    assert widget.max_slider.value == 7
    assert widget.range_label.value == "Time Slices: 1"

    # Unlock and verify we can set independent values
    widget.unlock_values()
    assert widget._single_value_mode is False

    # Now we can set different min and max
    widget.min_slider.value = 3
    widget.max_slider.value = 8
    widget.update_range()
    assert widget.min_slider.value == 3
    assert widget.max_slider.value == 8
    assert widget.range_label.value == "Time Slices: 6"
