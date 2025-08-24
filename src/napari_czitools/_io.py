from dataclasses import dataclass
from typing import Optional

import napari
import numpy as np
import xarray as xr
from czitools.metadata_tools import czi_metadata as czimd
from czitools.read_tools import read_tools
from czitools.utils import logging_tools
from napari.utils.colormaps import Colormap

from ._metadata_widget import MdTableWidget, MdTreeWidget, MetadataDisplayMode

# MetaDataDisplay = Optional[Literal["tree", "table"]]

logger = logging_tools.set_logging()


@dataclass
class ChannelLayer:
    """
    Represents a channel layer for visualization in Napari.
    Attributes:
        sub_array (xr.DataArray): The data array representing the channel's image data.
        metadata (czimd.CziMetadata): Metadata associated with the channel layer.
        name (str): The name of the channel layer.
        scale (list[float]): A list of scaling factors for the layer in each dimension.
        colormap (Colormap): The colormap used for visualizing the channel.
        blending (str): The blending mode for the layer. Defaults to "additive".
        opacity (float): The opacity level of the layer. Defaults to 0.85.
    """

    sub_array: xr.DataArray
    metadata: czimd.CziMetadata
    name: str
    scale: list[float]
    colormap: Colormap
    blending: str = "additive"
    opacity: float = 0.85


class CZIDataLoader:
    """
    A class to load and visualize CZI (Carl Zeiss Image) data in Napari.
    Parameters
    ----------
    path : str
        The file path to the CZI file.
    zoom : float, optional
        The zoom factor to apply to the image data. Default is 1.0.
    use_dask : bool, optional
        Whether to use Dask for lazy loading of the image data. Default is False.
    chunk_zyx : bool, optional
        Whether to chunk the data along the ZYX axes when using Dask. Default is False.
    use_xarray : bool, optional
        Whether to use xarray for handling the image data. Default is True.
    planes : dict, optional
        A dictionary specifying which planes to read from the CZI file. Default is None, which
        means all planes will be read.
    show_metadata : bool, optional
        Whether to display metadata information. Default is False.
    Methods
    -------
    add_to_viewer():
        Loads the CZI data and adds it to the current Napari viewer.
    """

    def __init__(
        self,
        path: str,
        zoom: float = 1.0,
        use_dask: bool = False,
        chunk_zyx: bool = False,
        use_xarray: bool = True,
        planes: dict = None,
        show_metadata: MetadataDisplayMode = MetadataDisplayMode.TABLE,
    ) -> None:
        self.path: str = path
        self.zoom: float = zoom
        self.use_dask: bool = use_dask
        self.chunk_zyx: bool = chunk_zyx
        self.use_xarray: bool = use_xarray
        self.planes: dict = planes if planes is not None else {}
        self.show_metadata: MetadataDisplayMode = show_metadata

    def add_to_viewer(self) -> None:
        """
        Adds image data and metadata to a napari viewer.
        This method reads a 6D array from the specified file path, processes the data,
        and adds it to a napari viewer. It also displays metadata in the viewer as either
        a tree or a table, based on the user's preference.
        Parameters:
            None
        Behavior:
            - Retrieves the current napari viewer or creates a new one if none exists.
            - Reads a 6D array and associated metadata from the file specified by `self.path`.
            - Displays metadata in the viewer:
                - As a tree if `self.show_metadata` is set to "tree".
                - As a table if `self.show_metadata` is set to "table".
            - Processes the 6D array into channel layers and adds them to the viewer as images.
            - Sets axis labels for the viewer based on the dimensions of the image data.
        Notes:
            - The method uses external tools for reading the 6D array and metadata,
              as well as for processing the channel layers.
            - Metadata widgets are added to the viewer's dock area on the right.
            - Image layers are added with specific properties such as colormap, blending,
              scale, and gamma correction.
        """
        # get napari viewer from current process
        viewer: Optional[napari.Viewer] = napari.current_viewer()
        if viewer is None:
            viewer = napari.Viewer()

        # return an array with dimension order STCZYX(A)
        array6d, metadata = read_tools.read_6darray(
            self.path,
            use_dask=self.use_dask,
            chunk_zyx=self.chunk_zyx,
            zoom=self.zoom,
            use_xarray=self.use_xarray,
            planes=self.planes,
        )

        if self.show_metadata == MetadataDisplayMode.TREE:
            # logger.info("Creating Metadata Tree")
            md_dict = czimd.create_md_dict_nested(
                metadata, sort=True, remove_none=True
            )
            mdtree = MdTreeWidget(data=md_dict, expandlevel=0)
            viewer.window.add_dock_widget(
                mdtree, name="MetadataTree", area="right"
            )

        if self.show_metadata == MetadataDisplayMode.TABLE:
            # logger.info("Creating Metadata Table")
            md_dict = czimd.create_md_dict_red(
                metadata, sort=True, remove_none=True
            )
            mdtable = MdTableWidget()
            mdtable.update_metadata(md_dict)
            mdtable.update_style()
            viewer.window.add_dock_widget(
                mdtable, name="MetadataTable", area="right"
            )

        if self.show_metadata == MetadataDisplayMode.NONE:
            # logger.info("No Metadata Display")
            pass

        # get the channel layers
        channel_layers = process_channels(array6d, metadata)

        for chl in channel_layers:

            # add the channel to the viewer
            viewer.add_image(
                chl.sub_array,
                name=chl.name,
                colormap=chl.colormap,
                blending=chl.blending,
                scale=chl.scale if chl.scale is not None else None,
                gamma=0.85,
            )

            # set the axis labels based on the dimensions
            viewer.dims.axis_labels = chl.sub_array.dims


def process_channels(array6d, metadata) -> list[ChannelLayer]:
    """
    Processes a 6D array and metadata to generate a list of ChannelLayer objects.
    This function extracts individual channels from a 6D array, applies scaling factors,
    assigns colors and names based on metadata, and creates ChannelLayer objects for each channel.
    Args:
        array6d: An xarray DataArray representing the 6D image data. The dimensions are expected
                 to include "C" (channels) and optionally "Z" (depth) and "A" (alpha for RGB).
        metadata: An object containing metadata about the image, including scaling factors,
                  channel names, colors, and display settings.
    Returns:
        list[ChannelLayer]: A list of ChannelLayer objects, each representing a processed channel
                            with associated metadata, scaling, colormap, and display settings.
    Raises:
        IndexError: If the metadata does not contain valid display settings for the channels.
    Notes:
        - The function adapts Z-axis scaling based on the metadata's scale ratio.
        - If the image contains an alpha channel ("A"), it is excluded from the scaling factors.
        - Colors are extracted from the metadata as ARGB hex strings and converted to RGB.
        - Display settings are guessed from metadata, with fallback defaults if unavailable or invalid.
    """

    channel_layers = []

    # get the planes
    subset_planes = array6d.attrs["subset_planes"]

    # loop over all channels
    for ch in range(array6d.sizes["C"]):

        # extract channel subarray
        sub_array = array6d.sel(C=ch)

        # get the scaling factors for that channel and adapt Z-axis scaling
        scalefactors = [1.0] * len(sub_array.shape)
        scalefactors[sub_array.get_axis_num("Z")] = metadata.scale.ratio[
            "zx_sf"
        ]

        # remove the last scaling factor in case of an RGB image
        if "A" in sub_array.dims:
            # remove the A axis from the scaling factors
            scalefactors.pop(sub_array.get_axis_num("A"))

        # get colors and channel name
        ch_index = subset_planes["C"][0] + ch
        chname = metadata.channelinfo.names[ch_index]

        # inside the CZI metadata_tools colors are defined as ARGB hexstring
        rgb = "#" + metadata.channelinfo.colors[ch_index][3:]
        ncmap = Colormap(["#000000", rgb], name="cm_" + chname)

        # guess an appropriate scaling from the display setting embedded in the CZI
        try:
            lower = np.round(
                metadata.channelinfo.clims[ch][0] * metadata.maxvalue_list[ch],
                0,
            )
            higher = np.round(
                metadata.channelinfo.clims[ch][1] * metadata.maxvalue_list[ch],
                0,
            )
        except IndexError:
            logger.warning(
                "Calculation from display setting from CZI failed. Use 0-Max instead."
            )
            lower = 0
            higher = metadata.maxvalue[ch]

        # simple validity check
        if lower >= higher:
            logger.warning("Fancy Display Scaling detected. Use Defaults")
            lower = 0
            higher = np.round(metadata.maxvalue[ch] * 0.25, 0)

        chl = ChannelLayer(
            sub_array=sub_array,
            metadata=metadata,
            name=chname,
            scale=scalefactors,
            colormap=ncmap,
            blending="additive",
            opacity=0.85,
        )

        channel_layers.append(chl)

    return channel_layers
