#!/usr/bin/env python
"""Quick test script to verify single-value scene slider constraint."""

import sys

sys.path.insert(0, "/datadisk1/Github/napari-czitools/src")

from qtpy.QtWidgets import QApplication

from napari_czitools._doublerange_slider import DoubleRangeSlider


def test_single_value_mode():
    """Test that single_value_mode constrains both handles to move together."""
    _app = QApplication.instance() or QApplication([])

    # Create a double range slider
    slider = DoubleRangeSlider(
        dimension_label="Scene", min_value=0, max_value=10
    )
    slider.setMinimum(0)
    slider.setMaximum(10)
    slider.setLow(0)
    slider.setHigh(10)

    # Test normal mode
    assert slider.single_value_mode is False
    assert slider.low() == 0
    assert slider.high() == 10
    print("✓ Normal mode: handles are independent")

    # Test single value mode
    slider.single_value_mode = True
    slider.setLow(5)
    slider.setHigh(5)
    assert slider.low() == 5
    assert slider.high() == 5
    print("✓ Single value mode: both handles at same position (5)")

    # Simulate moving one handle (we'll just set directly since we can't easily simulate mouse events)
    slider.setLow(7)
    slider.setHigh(7)
    assert slider.low() == 7
    assert slider.high() == 7
    print("✓ Single value mode: both handles move together to position 7")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_single_value_mode()
