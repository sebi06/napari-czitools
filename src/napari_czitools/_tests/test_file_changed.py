# File: _test/test_file_changed.py

from napari_czitools._widget import CziReaderWidget, SliderType


def _patch_metadata_loading(mocker, widget, metadata):
    metadata.scene_shape_is_consistent = True
    mocker.patch(
        "napari_czitools._widget.CziMetadata",
        return_value=metadata,
    )
    mocker.patch.object(widget, "_update_scene_diff_ui")
    mocker.patch(
        "napari_czitools._widget.czimd.create_md_dict_nested",
        return_value={},
    )
    mocker.patch(
        "napari_czitools._widget.czimd.create_md_dict_red",
        return_value={},
    )


def test_file_changed_updates_sliders_correctly(qtbot, mocker):
    widget = CziReaderWidget(mocker.Mock(), sliders=SliderType.TwoSliders)
    mock_metadata = mocker.Mock()
    mock_metadata.image.SizeS = 5
    mock_metadata.image.SizeT = 10
    mock_metadata.image.SizeC = 3
    mock_metadata.image.SizeZ = 15
    _patch_metadata_loading(mocker, widget, mock_metadata)

    widget.filename_edit.value = "test_file.czi"

    assert widget.scene_slider.enabled
    assert widget.scene_slider.min_slider.min == 0
    assert widget.scene_slider.max_slider.max == 4

    assert widget.time_slider.enabled
    assert widget.time_slider.min_slider.min == 0
    assert widget.time_slider.max_slider.max == 9

    assert widget.channel_slider.enabled
    assert widget.channel_slider.min_slider.min == 0
    assert widget.channel_slider.max_slider.max == 2

    assert widget.z_slider.enabled
    assert widget.z_slider.min_slider.min == 0
    assert widget.z_slider.max_slider.max == 14


def test_file_changed_resets_sliders_when_metadata_is_none(qtbot, mocker):
    widget = CziReaderWidget(mocker.Mock(), sliders=SliderType.TwoSliders)
    mock_metadata = mocker.Mock()
    mock_metadata.image.SizeS = None
    mock_metadata.image.SizeT = None
    mock_metadata.image.SizeC = None
    mock_metadata.image.SizeZ = None
    _patch_metadata_loading(mocker, widget, mock_metadata)

    widget.filename_edit.value = "test_file.czi"

    assert not widget.scene_slider.enabled
    assert widget.scene_slider.min_slider.min == 0
    assert widget.scene_slider.max_slider.max == 0

    assert not widget.time_slider.enabled
    assert widget.time_slider.min_slider.min == 0
    assert widget.time_slider.max_slider.max == 0

    assert not widget.channel_slider.enabled
    assert widget.channel_slider.min_slider.min == 0
    assert widget.channel_slider.max_slider.max == 0

    assert not widget.z_slider.enabled
    assert widget.z_slider.min_slider.min == 0
    assert widget.z_slider.max_slider.max == 0


def test_file_changed_enables_load_pixeldata_button(qtbot, mocker):
    widget = CziReaderWidget(mocker.Mock(), sliders=SliderType.TwoSliders)
    mock_metadata = mocker.Mock()
    mock_metadata.image.SizeS = 5
    mock_metadata.image.SizeT = None
    mock_metadata.image.SizeC = None
    mock_metadata.image.SizeZ = None
    _patch_metadata_loading(mocker, widget, mock_metadata)

    widget.filename_edit.value = "test_file.czi"

    assert widget.load_pixeldata.enabled
