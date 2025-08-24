from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import xarray as xr
from napari.utils.colormaps import Colormap

from napari_czitools._io import (
    ChannelLayer,
    CZIDataLoader,
    MetadataDisplayMode,
)

# ----------------- Pytest Fixtures -----------------
# (Fixtures are correct, no changes needed here)


@pytest.fixture
def mock_xarray_data() -> xr.DataArray:
    """Creates a simple 2D xarray.DataArray for testing."""
    return xr.DataArray(np.random.rand(10, 10), dims=("y", "x"))


@pytest.fixture
def mock_metadata_object() -> MagicMock:
    """Creates a MagicMock object to stand in for CziMetadata."""
    return MagicMock()


@pytest.fixture
def sample_colormap() -> Colormap:
    """Creates a sample Colormap object."""
    return Colormap(colors=["#FF0000", "#00FF00"], name="red_green")


# ----------------- Pytest Test Functions -----------------
# (ChannelLayer and __init__ tests are correct, no changes needed)


def test_channel_layer_initialization_with_defaults(
    mock_xarray_data, mock_metadata_object, sample_colormap
):
    layer = ChannelLayer(
        sub_array=mock_xarray_data,
        metadata=mock_metadata_object,
        name="Channel_1",
        scale=[1.0, 1.0],
        colormap=sample_colormap,
    )
    assert layer.name == "Channel_1"
    assert layer.scale == [1.0, 1.0]
    assert layer.colormap.name == "red_green"
    assert isinstance(layer.sub_array, xr.DataArray)
    assert layer.blending == "additive"
    assert layer.opacity == 0.85


def test_channel_layer_initialization_with_custom_values(
    mock_xarray_data, mock_metadata_object, sample_colormap
):
    layer = ChannelLayer(
        sub_array=mock_xarray_data,
        metadata=mock_metadata_object,
        name="Channel_2_Custom",
        scale=[0.5, 2.0],
        colormap=sample_colormap,
        blending="translucent",
        opacity=0.5,
    )
    assert layer.name == "Channel_2_Custom"
    assert layer.blending == "translucent"
    assert layer.opacity == 0.5
    assert layer.scale == [0.5, 2.0]


def test_czidataloader_init_defaults():
    loader = CZIDataLoader(path="test.czi")
    assert loader.path == "test.czi"
    assert loader.zoom == 1.0
    assert loader.use_dask is False
    assert loader.chunk_zyx is False
    assert loader.use_xarray is True
    assert loader.planes == {}
    assert loader.show_metadata == MetadataDisplayMode.TABLE


def test_czidataloader_init_custom_params():
    custom_planes = {"C": (0, 1)}
    loader = CZIDataLoader(
        path="another.czi",
        zoom=0.5,
        use_dask=True,
        chunk_zyx=True,
        planes=custom_planes,
        show_metadata="none",
    )
    assert loader.path == "another.czi"
    assert loader.zoom == 0.5
    assert loader.use_dask is True
    assert loader.chunk_zyx is True
    assert loader.planes == custom_planes
    assert loader.show_metadata == "none"


## Test add_to_viewer Method ##
# -----------------------------
# THIS IS THE CORRECTED SECTION


@patch("napari_czitools._io.process_channels")
@patch("napari_czitools._io.read_tools.read_6darray")
@patch("napari_czitools._io.napari.current_viewer")
@patch(
    "napari_czitools._io.MdTableWidget"
)  # Change to actual widget being used
def test_add_to_viewer_logic(
    mock_table_widget,
    mock_current_viewer,
    mock_read_6darray,
    mock_process_channels,
):
    """Tests the main logic of add_to_viewer by mocking its dependencies."""
    # 1. --- Setup Mocks ---
    mock_viewer = MagicMock()
    mock_current_viewer.return_value = mock_viewer
    mock_array = MagicMock()
    mock_metadata = MagicMock()
    mock_read_6darray.return_value = (mock_array, mock_metadata)
    mock_channel = MagicMock()
    mock_channel.name = "TestChannel"
    mock_channel.colormap = "gray"
    mock_channel.blending = "additive"
    mock_channel.scale = [1.0, 2.0, 2.0]
    mock_channel.sub_array.dims = ("Z", "Y", "X")
    mock_process_channels.return_value = [mock_channel]

    # Mock the MdTableWidget instance
    mock_table_instance = MagicMock()
    mock_table_widget.return_value = mock_table_instance

    # 2. --- Instantiate and Run ---
    loader = CZIDataLoader(
        path="test.czi",
        zoom=0.8,
        use_dask=True,
        show_metadata=MetadataDisplayMode.TABLE,
    )
    loader.add_to_viewer()

    # 3. --- Assertions ---
    mock_read_6darray.assert_called_once_with(
        "test.czi",
        use_dask=True,
        chunk_zyx=False,
        zoom=0.8,
        use_xarray=True,
        planes={},
    )
    mock_process_channels.assert_called_once_with(mock_array, mock_metadata)

    # Verify MdTableWidget was created and configured
    mock_table_widget.assert_called_once()
    mock_table_instance.update_metadata.assert_called_once()
    mock_table_instance.update_style.assert_called_once()
    mock_viewer.window.add_dock_widget.assert_called_once_with(
        mock_table_instance, name="MetadataTable", area="right"
    )

    mock_viewer.add_image.assert_called_once_with(
        mock_channel.sub_array,
        name="TestChannel",
        colormap="gray",
        blending="additive",
        scale=[1.0, 2.0, 2.0],
        gamma=0.85,
    )
    assert mock_viewer.dims.axis_labels == ("Z", "Y", "X")
