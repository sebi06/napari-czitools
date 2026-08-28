import os
from pathlib import Path

import pytest
from qtpy.QtCore import QMimeData, QPointF, Qt, QUrl
from qtpy.QtGui import QDropEvent

from napari_czitools._doublerange_slider import LabeledDoubleRangeSliderWidget
from napari_czitools._range_widget import RangeSliderWidget
from napari_czitools._widget import (
    MAX_DOCK_WIDTH,
    CziReaderWidget,
)

# Check if we're running in a headless environment (like GitHub Actions)
HEADLESS = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"

# Skip GUI tests in headless environments unless xvfb is available
pytestmark = pytest.mark.skipif(
    HEADLESS and not os.environ.get("DISPLAY"),
    reason="GUI tests require display server (use xvfb-run in CI)",
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
    assert widget.load_pixeldata.enabled is False
    assert not hasattr(widget, "lazy_loading_checkbox")
    assert widget.max_coarse_edge_label.text() == "3D preview size:"
    assert widget.max_coarse_edge_spinbox.isEnabled() is False
    assert "GPU memory" in widget.max_coarse_edge_spinbox.toolTip()

    # assert isinstance(widget.scene_slider, RangeSliderWidget)
    # assert isinstance(widget.time_slider, RangeSliderWidget)
    # assert isinstance(widget.channel_slider, RangeSliderWidget)
    # assert isinstance(widget.z_slider, RangeSliderWidget)

    assert isinstance(widget.scene_slider, RangeSliderWidget | LabeledDoubleRangeSliderWidget)
    assert isinstance(widget.time_slider, RangeSliderWidget | LabeledDoubleRangeSliderWidget)
    assert isinstance(
        widget.channel_slider,
        RangeSliderWidget | LabeledDoubleRangeSliderWidget,
    )
    assert isinstance(widget.z_slider, RangeSliderWidget | LabeledDoubleRangeSliderWidget)


def test_czi_reader_widget_allows_wide_dock(qapp):
    """The widget and its dock container should permit wide layouts."""
    from qtpy.QtWidgets import QDockWidget, QSizePolicy

    dock = QDockWidget()
    widget = CziReaderWidget(object())
    dock.setWidget(widget)

    dock.show()
    qapp.processEvents()
    initial_widget_y = widget.geometry().y()

    widget.scene_slider.hide()
    widget.time_slider.hide()
    qapp.processEvents()

    assert widget.maximumWidth() == MAX_DOCK_WIDTH
    assert dock.maximumWidth() == MAX_DOCK_WIDTH
    assert widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding
    assert dock.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding
    assert widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Expanding
    assert dock.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Expanding
    assert widget.geometry().y() == initial_widget_y


def test_czi_reader_widget_accepts_dropped_czi(qapp, tmp_path):
    """Test that dropping one local CZI updates the file selection."""
    filepath = tmp_path / "image.CZI"
    filepath.touch()
    widget = CziReaderWidget(object())
    widget.filename_edit.line_edit.changed.disconnect(widget._file_changed)

    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile(str(filepath))])
    event = QDropEvent(
        QPointF(1, 1),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    handled = widget.eventFilter(
        widget.filename_edit.line_edit.native,
        event,
    )

    assert handled
    assert Path(widget.filename_edit.value) == filepath
    assert event.isAccepted()


def test_czi_reader_widget_persists_coarse_edge(qapp, mocker):
    """The configured 3D preview size should persist and reach the reader."""
    settings = mocker.patch("napari_czitools._widget.QSettings").return_value
    settings.value.return_value = 1024
    reader = mocker.patch("napari_czitools._widget.reader_function_adv")
    widget = CziReaderWidget(object())
    widget.filename_edit.line_edit.changed.disconnect(widget._file_changed)
    widget.filename_edit.value = "test.czi"

    assert widget.max_coarse_edge_spinbox.value() == 1024

    widget.max_coarse_edge_spinbox.setValue(1536)
    widget._loadbutton_pressed()

    settings.setValue.assert_called_with("rendering/max_coarse_edge", 1536)
    assert reader.call_args.kwargs["max_coarse_edge"] == 1536
    assert reader.call_args.kwargs["use_lazy"] is True
    assert reader.call_args.kwargs["use_dask"] is True
    assert reader.call_args.kwargs["use_multiscale"] is True
