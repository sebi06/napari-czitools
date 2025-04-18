from dataclasses import dataclass
from typing import Literal, Optional

import napari
import numpy as np
import xarray as xr
from czitools.metadata_tools import czi_metadata as czimd
from czitools.read_tools import read_tools
from czitools.utils import logging_tools
from napari.utils.colormaps import Colormap

from ._metadata_widget import MdTableWidget, MdTreeWidget

MetaDataDisplay = Optional[Literal["tree", "table"]]

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
        show_metadata: MetaDataDisplay = "table",
    ) -> None:
        self.path: str = path
        self.zoom: float = zoom
        self.use_dask: bool = use_dask
        self.chunk_zyx: bool = chunk_zyx
        self.use_xarray: bool = use_xarray
        self.show_metadata: MetaDataDisplay = show_metadata

    def add_to_viewer(self) -> None:
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
        )

        if self.show_metadata == "tree":
            md_dict = czimd.create_md_dict_nested(
                metadata, sort=True, remove_none=True
            )
            mdtree = MdTreeWidget(data=md_dict, expandlevel=0)
            viewer.window.add_dock_widget(
                mdtree, name="MetadataTree", area="right"
            )

            # add QTableWidget DataTreeWidget to Napari viewer to show the metadata_tools
        if self.show_metadata == "table":
            md_dict = czimd.create_md_dict_red(
                metadata, sort=True, remove_none=True
            )
            mdtable = MdTableWidget()
            mdtable.update_metadata(md_dict)
            mdtable.update_style()
            viewer.window.add_dock_widget(
                mdtable, name="MetadataTable", area="right"
            )

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

    channel_layers = []

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
        chname = metadata.channelinfo.names[ch]

        # inside the CZI metadata_tools colors are defined as ARGB hexstring
        rgb = "#" + metadata.channelinfo.colors[ch][3:]
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
        except IndexError as e:
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
