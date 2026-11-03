"""Focused tests for CZI reference archives and lazy dimension selection."""

import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from napari_czitools._vzip import (
    INSTALL_HINT,
    open_vzip,
    prepare_vzip,
    read_vzip,
    vzip_layers,
)


@pytest.fixture
def archive(tmp_path, monkeypatch):
    """Provide two scene groups with synthetic reference-archive metadata."""
    pytest.importorskip("refkv.zarr")
    import refkv.zarr
    import zarr

    source = tmp_path / "source.czi"
    source.touch()
    path = tmp_path / "source.vzip"
    path.touch()
    store = zarr.storage.MemoryStore()
    root = zarr.open_group(store, mode="w")
    root.attrs["refkv_zarrified"] = {
        "profile": "czi",
        "source": {"url": source.as_uri()},
    }
    data = np.arange(2 * 3 * 4 * 8 * 10, dtype=np.uint16).reshape(
        2, 3, 4, 8, 10
    )
    for scene in (0, 1):
        group = root.create_group(str(scene))
        group.create_array("0", data=data + scene)
        group.create_array("1", data=(data + scene)[..., ::2, ::2])
        group.attrs["ome"] = {
            "multiscales": [
                {
                    "axes": [
                        {"name": axis} for axis in ("t", "c", "z", "y", "x")
                    ],
                    "datasets": [
                        {
                            "path": "0",
                            "coordinateTransformations": [
                                {
                                    "type": "scale",
                                    "scale": [2, 1, 0.5, 0.1, 0.1],
                                },
                            ],
                        },
                        {"path": "1"},
                    ],
                }
            ],
            "omero": {
                "channels": [
                    {
                        "label": "DAPI",
                        "color": "0000FF",
                        "window": {"start": 10, "end": 500},
                    },
                    {"label": "GFP", "color": "00FF00"},
                    {"label": "RFP", "color": "FF0000"},
                ]
            },
        }
    monkeypatch.setattr(refkv.zarr, "open", lambda path: store)
    return path, source, root, data


def test_archive_metadata_and_lazy_selections(archive, monkeypatch):
    """Keep T/Z dimensions, select scenes/channels and preserve physical origin."""
    import dask.array as da

    path, source, _, data = archive
    opened = open_vzip(path)
    assert opened.source == source
    assert opened.sizes == {"S": 2, "T": 2, "C": 3, "Z": 4}

    def fail_compute(*args, **kwargs):
        pytest.fail("Loading archive metadata must not compute pixels")

    with monkeypatch.context() as context:
        context.setattr(da.Array, "compute", fail_compute)
        layers = vzip_layers(
            opened, {"S": (1, 1), "T": (1, 1), "C": (0, 1), "Z": (1, 2)}
        )
    assert len(layers) == 2
    levels, kwargs, kind = layers[0]
    assert kind == "image"
    assert kwargs["multiscale"] is True
    assert kwargs["axis_labels"] == ("t", "z", "y", "x")
    assert kwargs["scale"] == (2, 0.5, 0.1, 0.1)
    assert kwargs["translate"] == (2, 0.5, 0, 0)
    assert kwargs["contrast_limits"] == (10, 500)
    assert "DAPI" in kwargs["name"]
    assert levels[0].shape == (1, 2, 8, 10)
    assert levels[1].shape == (1, 2, 4, 5)
    np.testing.assert_array_equal(levels[0].compute(), (data + 1)[1:2, 0, 1:3])


def test_rectilinear_archive_lazy_selections(archive, monkeypatch):
    """Preserve irregular chunk boundaries and defer reads for every pyramid level."""
    import zarr

    if not hasattr(zarr.Array, "read_chunk_sizes"):
        pytest.skip("This Zarr version does not support rectilinear grids")
    path, _, root, data = archive
    chunks = ((1, 1), (1, 2), (1, 3), (3, 5), (4, 6))
    with zarr.config.set({"array.rectilinear_chunks": True}):
        del root["0"]["0"]
        root["0"].create_array("0", data=data, chunks=chunks)
        with pytest.raises(NotImplementedError, match="rectilinear"):
            _ = root["0"]["0"].chunks
        reads = []
        getitem = zarr.Array.__getitem__

        def record_read(array, selection):
            reads.append(selection)
            return getitem(array, selection)

        monkeypatch.setattr(zarr.Array, "__getitem__", record_read)
        layers = vzip_layers(
            open_vzip(path),
            {"S": (0, 0), "T": (1, 1), "C": (1, 1), "Z": (1, 2)},
        )
        assert not reads
        levels, kwargs, _ = layers[0]
        assert kwargs["multiscale"] is True
        assert levels[0].chunks[-2:] == ((3, 5), (4, 6))
        np.testing.assert_array_equal(levels[0].compute(), data[1:2, 1, 1:3])
        np.testing.assert_array_equal(
            levels[1].compute(), data[1:2, 1, 1:3, ::2, ::2]
        )
        assert reads


def test_no_selection_reads_all_scene_channel_layers(archive):
    """Direct opening returns independent scene layers rather than stacking."""
    layers = read_vzip([str(archive[0])])
    assert len(layers) == 6
    assert layers[0][0][0].shape == (2, 4, 8, 10)


def test_missing_source_and_non_czi_archive(archive):
    """Reject unavailable sources and unrelated archives before adding layers."""
    path, source, root, _ = archive
    source.unlink()
    with pytest.raises(FileNotFoundError, match="Referenced CZI is missing"):
        open_vzip(path)
    root.attrs["refkv_zarrified"] = {"profile": "tiff"}
    with pytest.raises(ValueError, match="Only CZI-derived"):
        open_vzip(path)


@pytest.mark.parametrize(
    "planes", [{"S": (0, 2)}, {"C": (3, 3)}, {"T": (1, 0)}, {"Z": (-1, 2)}]
)
def test_invalid_selections(archive, planes):
    """Out-of-range or reversed positional selections fail explicitly."""
    with pytest.raises(ValueError, match="selection"):
        read_vzip(str(archive[0]), planes)


def test_real_czi_archive(tmp_path):
    """Persist and reopen a bundled CZI using the public czitools exporter."""
    pytest.importorskip("refkv.zarr")
    pytest.importorskip("czitools.export_tools.vzip")
    from czitools.export_tools import create_czi_vzip

    source = (
        Path(__file__).resolve().parents[1]
        / "sample_data"
        / "CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi"
    )
    path = create_czi_vzip(source, tmp_path / "image.vzip")
    layers = read_vzip(str(path))
    assert layers
    data = layers[0][0]
    assert hasattr(data, "compute")
    assert data.shape[-2:] == (200, 300)
    assert data[
        (0,) * (data.ndim - 2) + (slice(0, 8), slice(0, 8))
    ].compute().shape == (8, 8)


def test_reader_registration():
    """Claim archives including uppercase extensions without requiring a source."""
    from napari_czitools import napari_get_reader

    assert napari_get_reader("image.vzip") is read_vzip
    assert napari_get_reader(["image.VZIP"]) is read_vzip
    assert napari_get_reader([]) is None
    assert napari_get_reader("other.file") is None


def test_prepare_reuses_archive_and_checks_source(archive, monkeypatch):
    """Reuse avoids zarrification and rejects archives belonging to another CZI."""
    from czitools import export_tools

    def fail_create(*args, **kwargs):
        pytest.fail("Reuse must not rewrite the archive")

    monkeypatch.setattr(
        export_tools, "create_czi_vzip", fail_create, raising=False
    )
    path, source, _, _ = archive
    _, layers = prepare_vzip(source, path, False, {})
    assert len(layers) == 6
    other_source = source.with_name("other.czi")
    other_source.touch()
    with pytest.raises(ValueError, match="not .*other.czi"):
        prepare_vzip(other_source, path, False, {})


@pytest.mark.parametrize("rebuild", [False, True])
def test_prepare_creates_complete_archive(archive, monkeypatch, rebuild):
    """Forward only the source and overwrite flag, never the display selection."""
    from czitools import export_tools

    path, source, _, _ = archive
    calls = []
    if not rebuild:
        path.unlink()

    def create(source_arg, destination, *, overwrite):
        calls.append((source_arg, destination, overwrite))
        destination.touch()
        return destination

    monkeypatch.setattr(export_tools, "create_czi_vzip", create, raising=False)
    _, layers = prepare_vzip(source, path, rebuild, {"S": (1, 1), "C": (1, 1)})
    assert calls == [(source, path, rebuild)]
    assert len(layers) == 1
    assert "GFP" in layers[0][1]["name"]


@pytest.mark.parametrize(
    "axes",
    [("y", "x"), ("z", "y", "x"), ("c", "z", "y", "x"), ("x", "z", "y")],
)
def test_axis_order_and_optional_dimensions(archive, axes):
    """Handle 2D and channel-less data without assuming five dimensions."""
    path, _, root, _ = archive
    sizes = {"c": 3, "z": 4, "y": 8, "x": 10}
    shape = tuple(sizes[axis] for axis in axes)
    data = np.arange(np.prod(shape), dtype=np.uint16).reshape(shape)
    group = root.get_group("0")
    group.create_array("alternative", data=data)
    group.attrs["ome"] = {
        "multiscales": [
            {
                "axes": [{"name": axis} for axis in axes],
                "datasets": [{"path": "alternative"}],
            }
        ]
    }
    layers = read_vzip(
        str(path), {"S": (0, 0), "Z": (1, 2)} if "z" in axes else {"S": (0, 0)}
    )
    assert len(layers) == (sizes["c"] if "c" in axes else 1)
    actual, kwargs, _ = layers[0]
    selection = tuple(
        0 if axis == "c" else slice(1, 3) if axis == "z" else slice(None)
        for axis in axes
    )
    remaining = tuple(axis for axis in axes if axis != "c")
    permutation = tuple(
        remaining.index(axis) for axis in kwargs["axis_labels"]
    )
    np.testing.assert_array_equal(
        actual.compute(), data[selection].transpose(permutation)
    )
    assert kwargs["multiscale"] is False
    assert kwargs["axis_labels"][-2:] == ("y", "x")


def test_vzip_mode_missing_dependency_guidance(qapp, monkeypatch):
    """Keep the default backend usable and explain missing optional support."""
    from napari_czitools._widget import CziReaderWidget

    monkeypatch.setattr(
        "napari_czitools._widget.vzip_available", lambda: False
    )
    widget = CziReaderWidget(object())
    assert widget.loading_mode.value == "CZI"
    assert widget.vzip_controls.isHidden()
    widget.loading_mode.value = "VZIP"
    assert widget.vzip_controls.isHidden()
    assert not widget.vzip_status.isHidden()
    assert not widget.load_pixeldata.enabled
    assert widget.vzip_status.text() == INSTALL_HINT
    assert not widget.max_coarse_edge_spinbox.isEnabled()
    assert not widget.stack_scenes_checkbox.isEnabled()


@pytest.mark.parametrize("slider_type", ["TwoSliders", "DoubleRangeSlider"])
def test_archive_selection_populates_widget(archive, qapp, slider_type):
    """Selecting an archive switches mode and derives both slider styles from OME."""
    from napari_czitools._widget import CziReaderWidget

    widget = CziReaderWidget(object())
    widget.filename_edit.value = archive[0]
    widget.slidertype_widget.value = slider_type
    assert widget.loading_mode.value == "VZIP"
    assert widget.metadata is None
    assert widget._vzip_archive.source == archive[1]
    assert widget.load_pixeldata.enabled
    assert widget.vzip_controls.isHidden()
    assert widget.vzip_destination_label.isHidden()
    if slider_type == "DoubleRangeSlider":
        assert widget.scene_slider.high() == 1
        assert widget.channel_slider.high() == 2
        assert widget.z_slider.high() == 3
    else:
        assert widget.scene_slider.max_slider.value == 1
        assert widget.channel_slider.max_slider.value == 2
        assert widget.z_slider.max_slider.value == 3


def test_unified_file_controls_and_layout(qapp):
    """Use one source selector and preserve the mode row when metadata changes."""
    from magicgui.widgets import FileEdit

    from napari_czitools._widget import CziReaderWidget

    widget = CziReaderWidget(object())
    selectors = [
        value for value in vars(widget).values() if isinstance(value, FileEdit)
    ]
    assert selectors == [widget.filename_edit]
    assert (
        widget.main_layout.itemAt(0)
        .layout()
        .indexOf(widget.filename_edit.native)
        >= 0
    )
    assert (
        widget.main_layout.itemAt(1)
        .layout()
        .indexOf(widget.loading_mode.native)
        >= 0
    )
    for mode in ("Tree", "Table", "Tree"):
        widget.mdata_widget.value = mode
        assert widget.main_layout.indexOf(widget.current_md_widget) == 4
        assert (
            widget.main_layout.itemAt(1)
            .layout()
            .indexOf(widget.loading_mode.native)
            >= 0
        )


@pytest.mark.parametrize("chosen", ["", "custom", "custom.vzip"])
def test_save_archive_destination_override(archive, qapp, mocker, chosen):
    """Changing the save destination never replaces the selected CZI input."""
    from qtpy.QtWidgets import QFileDialog

    from napari_czitools._widget import CziReaderWidget

    widget = CziReaderWidget(object())
    widget.filename_edit.value = archive[0]
    with widget.filename_edit.line_edit.changed.blocked():
        widget.filename_edit.value = archive[1]
    widget._vzip_destination = archive[0]
    widget._archive_source_path = archive[1]
    widget._sync_vzip_controls()
    selected = str(archive[0].parent / chosen) if chosen else ""
    dialog = mocker.patch(
        "napari_czitools._widget.QFileDialog.getSaveFileName",
        return_value=(selected, "VZIP archives (*.vzip)"),
    )
    assert not widget.vzip_controls.isHidden()
    widget.save_archive_as.click()
    assert Path(widget.filename_edit.value) == archive[1]
    expected = Path(selected).with_suffix(".vzip") if chosen else archive[0]
    assert widget._vzip_destination == expected
    assert widget.vzip_destination_label.text() == f"Archive: {expected.name}"
    assert widget.vzip_destination_label.toolTip() == str(expected.absolute())
    assert (
        dialog.call_args.kwargs["options"]
        == QFileDialog.Option.DontConfirmOverwrite
    )
    mocker.patch(
        "napari_czitools._widget.CziMetadata",
        side_effect=ValueError("Synthetic CZI has no pixel header"),
    )
    widget.loading_mode.value = "CZI"
    assert widget.vzip_controls.isHidden()
    widget.loading_mode.value = "VZIP"
    assert widget._vzip_destination == expected


def test_existing_archive_hides_destination_action(archive, qapp, mocker):
    """Opening an archive offers no creation destination or save dialog."""
    from napari_czitools._widget import CziReaderWidget

    widget = CziReaderWidget(object())
    widget.filename_edit.value = archive[0]
    dialog = mocker.patch(
        "napari_czitools._widget.QFileDialog.getSaveFileName"
    )
    widget._choose_vzip_destination()
    dialog.assert_not_called()
    assert widget.vzip_controls.isHidden()
    assert widget.vzip_destination_label.isHidden()
    assert not hasattr(widget, "vzip_warning")


def test_archive_worker_adds_layers_on_main_thread(
    archive, qtbot, make_napari_viewer, monkeypatch
):
    """Background preparation returns lazy layers to the owning viewer's Qt thread."""
    import threading

    from napari_czitools._widget import CziReaderWidget

    viewer = make_napari_viewer()
    widget = CziReaderWidget(viewer)
    qtbot.addWidget(widget)
    widget.filename_edit.value = archive[0]
    calls = []
    main_thread = threading.get_ident()
    add_image = type(viewer).add_image

    def record(instance, *args, **kwargs):
        calls.append(threading.get_ident())
        return add_image(instance, *args, **kwargs)

    monkeypatch.setattr(type(viewer), "add_image", record)
    widget._loadbutton_pressed()
    assert not widget.isEnabled()
    qtbot.waitUntil(lambda: widget._vzip_worker is None, timeout=10000)
    assert len(viewer.layers) == 6
    assert calls == [main_thread] * 6
    assert widget.isEnabled()
    assert widget.vzip_progress.isHidden()
    assert "Opened archive" in widget.vzip_status.text()


@pytest.mark.parametrize("choice", ["reuse", "rebuild", "cancel"])
def test_existing_archive_widget_choices(archive, qapp, mocker, choice):
    """Each dialog choice forwards the intended overwrite flag or cancels work."""
    from napari_czitools._widget import CziReaderWidget

    widget = CziReaderWidget(object())
    widget.filename_edit.value = archive[0]
    with widget.filename_edit.line_edit.changed.blocked():
        widget.filename_edit.value = archive[1]
    prompt = mocker.patch.object(
        widget, "_existing_vzip_choice", return_value=choice
    )
    create_worker = mocker.patch("napari.qt.threading.create_worker")
    widget._loadbutton_pressed()
    prompt.assert_called_once_with(archive[0])
    if choice == "cancel":
        create_worker.assert_not_called()
        assert widget.isEnabled()
    else:
        args = create_worker.call_args.args
        assert args[1:4] == (archive[1], archive[0], choice == "rebuild")
        create_worker.return_value.start.assert_called_once()


def test_worker_failure_restores_controls(
    archive, qtbot, make_napari_viewer, mocker
):
    """Missing source errors are visible and never fall back to another reader."""
    from napari_czitools._widget import CziReaderWidget

    viewer = make_napari_viewer()
    widget = CziReaderWidget(viewer)
    qtbot.addWidget(widget)
    widget.filename_edit.value = archive[0]
    archive[1].unlink()
    notify = mocker.patch("napari.utils.notifications.show_error")
    fallback = mocker.patch("napari_czitools._widget.reader_function_adv")
    widget._loadbutton_pressed()
    qtbot.waitUntil(lambda: widget._vzip_worker is None, timeout=10000)
    assert widget.isEnabled()
    assert "Referenced CZI is missing" in widget.vzip_status.text()
    assert not viewer.layers
    notify.assert_called_once()
    fallback.assert_not_called()


def test_invalid_destination_does_not_start_worker(archive, qapp, mocker):
    """An empty or invalid destination must not prompt to replace a directory."""
    from napari_czitools._widget import CziReaderWidget

    widget = CziReaderWidget(object())
    widget.filename_edit.value = archive[0]
    with widget.filename_edit.line_edit.changed.blocked():
        widget.filename_edit.value = archive[1]
    widget._vzip_destination = archive[0].parent
    notify = mocker.patch("napari.utils.notifications.show_error")
    prompt = mocker.patch.object(widget, "_existing_vzip_choice")
    worker = mocker.patch("napari.qt.threading.create_worker")
    widget._loadbutton_pressed()
    assert "Choose a .vzip" in widget.vzip_status.text()
    assert widget.isEnabled()
    notify.assert_called_once()
    prompt.assert_not_called()
    worker.assert_not_called()


def test_closed_widget_discards_results(archive, qapp):
    """Do not add layers after the reader widget closes during preparation."""
    from napari_czitools._widget import CziReaderWidget

    widget = CziReaderWidget(object())
    widget.close()
    opened = open_vzip(archive[0])
    widget._vzip_loaded((opened, vzip_layers(opened)))
    assert widget._vzip_closed


@pytest.mark.parametrize("select_source_first", [False, True])
def test_widget_creates_and_reopens_real_archive(
    tmp_path, qtbot, make_napari_viewer, mocker, select_source_first
):
    """Export the full source off-thread, display a subset, then reuse the archive."""
    pytest.importorskip("refkv.zarr")
    pytest.importorskip("czitools.export_tools.vzip")
    if sys.platform.startswith("linux") and (
        os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS")
    ):
        pytest.skip("CZI metadata reading can deadlock in headless Linux CI")
    from napari_czitools._widget import CziReaderWidget

    original = (
        Path(__file__).resolve().parents[1]
        / "sample_data"
        / "CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi"
    )
    source = tmp_path / "sample.czi"
    shutil.copyfile(original, source)
    viewer = make_napari_viewer()
    widget = CziReaderWidget(viewer)
    qtbot.addWidget(widget)
    archive_path = source.with_suffix(".vzip")
    if select_source_first:
        widget.filename_edit.value = source
        assert widget.loading_mode.value == "CZI"
        widget.loading_mode.value = "VZIP"
    else:
        widget.loading_mode.value = "VZIP"
        widget.filename_edit.value = source
    assert not archive_path.exists()
    assert widget.load_pixeldata.enabled
    assert widget._vzip_destination == archive_path
    widget.time_slider.setLow(1)
    widget.time_slider.setHigh(1)
    widget.z_slider.setLow(2)
    widget.z_slider.setHigh(3)
    widget._loadbutton_pressed()
    qtbot.waitUntil(lambda: widget._vzip_worker is None, timeout=30000)
    assert archive_path.is_file()
    assert len(viewer.layers) == 1
    assert viewer.layers[0].data.shape == (1, 2, 200, 300)
    assert open_vzip(archive_path).sizes["T"] == 3
    assert open_vzip(archive_path).sizes["Z"] == 6
    timestamp = archive_path.stat().st_mtime_ns
    prompt = mocker.patch.object(
        widget, "_existing_vzip_choice", return_value="reuse"
    )
    widget._loadbutton_pressed()
    qtbot.waitUntil(lambda: widget._vzip_worker is None, timeout=30000)
    prompt.assert_called_once_with(archive_path)
    assert archive_path.stat().st_mtime_ns == timestamp
    widget.filename_edit.value = archive_path
    widget._loadbutton_pressed()
    qtbot.waitUntil(lambda: widget._vzip_worker is None, timeout=30000)
    assert len(viewer.layers) == 3
    assert viewer.layers[-1].data.shape == (3, 6, 200, 300)
