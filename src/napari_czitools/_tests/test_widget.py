import os

import pytest

from napari_czitools._doublerange_slider import LabeledDoubleRangeSliderWidget
from napari_czitools._range_widget import RangeSliderWidget
from napari_czitools._widget import (
    CziReaderWidget,
)

# Check if we're running in a headless environment (like GitHub Actions)
HEADLESS = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"

# Skip GUI tests in headless environments unless xvfb is available
pytestmark = pytest.mark.skipif(
    HEADLESS and not os.environ.get("DISPLAY"), reason="GUI tests require display server (use xvfb-run in CI)"
)


def test_czi_reader_widget_initialization(make_napari_viewer):
    """Test that the CziReaderWidget initializes correctly."""
    viewer = make_napari_viewer()
    widget = CziReaderWidget(viewer)

    assert isinstance(widget, CziReaderWidget)
    assert widget.viewer == viewer
    # FileEdit widget may initialize with current directory as default
    assert widget.filename_edit.value is not None
    assert widget.mdata_widget.value == "Table"

    # assert isinstance(widget.scene_slider, RangeSliderWidget)
    # assert isinstance(widget.time_slider, RangeSliderWidget)
    # assert isinstance(widget.channel_slider, RangeSliderWidget)
    # assert isinstance(widget.z_slider, RangeSliderWidget)

    assert isinstance(widget.scene_slider, RangeSliderWidget | LabeledDoubleRangeSliderWidget)
    assert isinstance(widget.time_slider, RangeSliderWidget | LabeledDoubleRangeSliderWidget)
    assert isinstance(widget.channel_slider, RangeSliderWidget | LabeledDoubleRangeSliderWidget)
    assert isinstance(widget.z_slider, RangeSliderWidget | LabeledDoubleRangeSliderWidget)
