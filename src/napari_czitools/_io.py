from dataclasses import dataclass, replace

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


def read_stacks_compat(
    path: str,
    use_dask: bool,
    use_xarray: bool,
    planes: dict | None,
) -> tuple[object, czimd.CziMetadata]:
    """Read stacks with compatibility across czitools return signatures."""
    # Convert to list so the type checker does not perform fixed-length
    # tuple narrowing – older czitools returned 3 values, newer ones return 4.
    parts: list[object] = list(
        read_tools.read_stacks(
            path,
            use_dask=use_dask,
            use_xarray=use_xarray,
            stack_scenes=True,
            planes=planes,
        )
    )

    if len(parts) == 4:
        metadata = parts[3]
        assert isinstance(metadata, czimd.CziMetadata)
        return parts[0], metadata

    if len(parts) == 3:
        return parts[0], czimd.CziMetadata(path)

    raise ValueError(f"Unexpected read_stacks return length: {len(parts)}")


def read_stacks_multiscale_compat(
    path: str,
    use_xarray: bool,
    planes: dict | None,
    max_coarse_edge: int = 8192,
) -> tuple[list[object], czimd.CziMetadata, int]:
    """Read a CZI as a multiscale pyramid via czitools.

    Wraps :func:`czitools.read_tools.read_stacks_multiscale` and returns the
    per-level arrays alongside the metadata and the number of detected
    levels. Layer 0 is always present; additional levels appear when the
    CZI stores a pyramid or when the coarsest stored level had to be
    extended by synthetic coarser reads so the top level fits within
    ``max_coarse_edge`` pixels per side. See the czitools docs for details.

    Args:
        path: CZI file path.
        use_xarray: Return ``xarray.DataArray`` levels when True, plain
            dask arrays when False.
        planes: Optional S/T/C/Z subset dict, forwarded to czitools.
        max_coarse_edge: Passed through to control GPU-safety synthesis.

    Returns:
        Tuple ``(levels, metadata, num_levels)``. ``levels`` is a list with
        one element per pyramid level (coarsest last). Each element is
        whatever ``read_stacks(..., stack_scenes=True)`` returns at that
        zoom — usually an xarray/dask array for the whole file, or a list
        of scene arrays when scene shapes differ.
    """
    result_levels, _infos, _dims, _num_stacks, metadata = read_tools.read_stacks_multiscale(
        path,
        use_xarray=use_xarray,
        stack_scenes=True,
        planes=planes,
        max_coarse_edge=max_coarse_edge,
    )
    return list(result_levels), metadata, len(result_levels)


@dataclass
class ChannelLayer:
    """
    Represents a channel layer for visualization in Napari.
    Attributes:
        sub_array (xr.DataArray | list[xr.DataArray]): The channel's image
            data. A single DataArray for standard reads, or a list
            (coarsest last) for multiscale pyramid layers. When a list is
            provided, ``CZIDataLoader.add_to_viewer`` passes
            ``multiscale=True`` to ``viewer.add_image`` so napari renders
            the coarse level immediately and streams finer tiles on zoom.
        metadata (czimd.CziMetadata): Metadata associated with the channel layer.
        name (str): The name of the channel layer.
        scale (list[float]): A list of scaling factors for the layer in each dimension.
        colormap (Colormap): The colormap used for visualizing the channel.
        blending (str): The blending mode for the layer. Defaults to "additive".
        opacity (float): The opacity level of the layer. Defaults to 0.85.
        contrast_limits (tuple[float, float] | None): Pre-computed display
            range forwarded to ``viewer.add_image``. When set, napari skips
            its automatic min/max scan of the array; this is essential for
            large dask-backed arrays where the auto-scan would compute every
            chunk and blow up RAM.
    """

    sub_array: xr.DataArray | list[xr.DataArray]
    metadata: czimd.CziMetadata
    name: str
    scale: list[float]
    colormap: Colormap
    blending: str = "additive"
    opacity: float = 0.85
    contrast_limits: tuple[float, float] | None = None


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
    use_lazy : bool, optional
        Whether to use lazy loading for the image data. Default is True.
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
        planes: dict | None = None,
        show_metadata: MetadataDisplayMode = MetadataDisplayMode.TABLE,
        use_lazy: bool = True,
        use_multiscale: bool = True,
        max_coarse_edge: int = 8192,
    ) -> None:
        self.path: str = path
        self.zoom: float = zoom
        self.use_dask: bool = use_dask
        self.chunk_zyx: bool = chunk_zyx
        self.use_xarray: bool = use_xarray
        self.planes: dict = planes if planes is not None else {}
        self.show_metadata: MetadataDisplayMode = show_metadata
        self.use_lazy: bool = use_lazy
        # When True and lazy mode is on, the plugin asks czitools for a
        # multiscale pyramid so napari can render gigapixel planes from
        # coarse-level tiles instead of materialising the whole 2D image.
        self.use_multiscale: bool = use_multiscale
        # Coarsest pyramid level's longest edge target. Passed to
        # read_stacks_multiscale; smaller values force additional synthetic
        # coarse levels for GPU-safety on files that stop at a large level.
        self.max_coarse_edge: int = max_coarse_edge

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
        viewer: napari.Viewer | None = napari.current_viewer()
        if viewer is None:
            viewer = napari.Viewer()

        if not self.use_lazy:
            # return an array with dimension order STCZYX(A)
            array6d, metadata = read_tools.read_6darray(
                self.path,
                use_dask=self.use_dask,
                chunk_zyx=self.chunk_zyx,
                zoom=self.zoom,
                use_xarray=self.use_xarray,
                planes=self.planes,
            )

        if self.use_lazy and self.use_multiscale:
            # Multiscale path: czitools returns one array per pyramid level.
            # process_channels_multiscale collapses that into per-channel
            # ChannelLayers whose sub_array is a list — the shape napari's
            # multiscale=True renderer expects. When the file has only one
            # level (no on-disk pyramid), the list has length 1 and we still
            # pass multiscale=True; napari treats a single-element list
            # identically to a plain array.
            levels, metadata, num_levels = read_stacks_multiscale_compat(
                self.path,
                use_xarray=self.use_xarray,
                planes=self.planes,
                max_coarse_edge=self.max_coarse_edge,
            )
            logger.info("CZIDataLoader: multiscale mode active with %d level(s).", num_levels)
            array6d = levels  # marker for the multiscale process_channels branch

        if self.use_lazy and not self.use_multiscale:
            # Legacy single-scale lazy path. Kept as an escape hatch for
            # debugging or for files whose pyramid metadata is broken.
            array6d, metadata = read_stacks_compat(
                self.path,
                use_dask=True,
                use_xarray=self.use_xarray,
                planes=self.planes,
            )

        if self.show_metadata == MetadataDisplayMode.TREE:
            # logger.info("Creating Metadata Tree")
            md_dict = czimd.create_md_dict_nested(metadata, sort=True, remove_none=True)
            mdtree = MdTreeWidget(data=md_dict, expandlevel=0)
            viewer.window.add_dock_widget(mdtree, name="MetadataTree", area="right")

        if self.show_metadata == MetadataDisplayMode.TABLE:
            # logger.info("Creating Metadata Table")
            md_dict = czimd.create_md_dict_red(metadata, sort=True, remove_none=True)
            mdtable = MdTableWidget()
            mdtable.update_metadata(md_dict)
            mdtable.update_style()
            viewer.window.add_dock_widget(mdtable, name="MetadataTable", area="right")

        if self.show_metadata == MetadataDisplayMode.NONE:
            # logger.info("No Metadata Display")
            pass

        # get the channel layers. When the loader is in multiscale mode,
        # ``array6d`` is actually a list-of-levels and we build multiscale
        # ChannelLayers; otherwise it is a single array/list as before.
        if self.use_lazy and self.use_multiscale:
            channel_layers = process_channels_multiscale(array6d, metadata)
        else:
            channel_layers = process_channels(array6d, metadata)

        for chl in channel_layers:

            is_multiscale = isinstance(chl.sub_array, list)
            # For multiscale, napari expects the finest level first and uses
            # per-level shape ratios for coarse-level scaling. dims/axis
            # labels come from level 0 either way.
            axis_source = chl.sub_array[0] if is_multiscale else chl.sub_array

            # Passing an explicit ``contrast_limits`` prevents napari's
            # auto-scan, which would otherwise call ``.compute()`` on the
            # whole dask array and allocate the full plane in RAM for
            # gigapixel images.
            viewer.add_image(
                chl.sub_array,
                name=chl.name,
                colormap=chl.colormap,
                blending=chl.blending,
                scale=chl.scale if chl.scale is not None else None,
                gamma=0.85,
                contrast_limits=(list(chl.contrast_limits) if chl.contrast_limits is not None else None),
                multiscale=is_multiscale,
            )

            # set the axis labels based on the dimensions of the finest level
            viewer.dims.axis_labels = tuple(str(d) for d in axis_source.dims)


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

    # Newer czitools versions can return one DataArray per scene (as a list).
    # Keep compatibility with both list and single-array return types.
    stack_arrays = array6d if isinstance(array6d, list) else [array6d]
    if len(stack_arrays) == 0:
        return channel_layers

    for stack_index, stack_array in enumerate(stack_arrays):

        # get the subset planes that were used aka
        # {"S": (0,0), "T": (0,3), "C": (0,1), "Z": (0,4)}
        subset_planes = stack_array.attrs.get("subset_planes", {})
        channel_start = subset_planes.get("C", (0, 0))[0]

        # loop over all channels in the current stack
        for ch in range(stack_array.sizes["C"]):

            # extract channel subarray by position to support string channel
            # coordinates returned by newer czitools/xarray versions.
            sub_array = stack_array.isel(C=ch)

            # get the scaling factors for that channel and adapt Z-axis scaling
            scalefactors = [1.0] * len(sub_array.shape)
            scalefactors[sub_array.get_axis_num("Z")] = metadata.scale.ratio["zx_sf"]

            # remove the last scaling factor in case of an RGB image
            if "A" in sub_array.dims:
                # remove the A axis from the scaling factors
                scalefactors.pop(sub_array.get_axis_num("A"))

            # get colors and channel name
            ch_index = channel_start + ch
            chname = metadata.channelinfo.names[ch_index]
            layer_name = chname
            if len(stack_arrays) > 1:
                layer_name = f"{chname}_S{stack_index}"

            # inside the CZI metadata_tools colors are defined as ARGB hexstring
            rgb = "#" + metadata.channelinfo.colors[ch_index][3:]
            ncmap = Colormap(["#000000", rgb], name="cm_" + layer_name)

            # try to read the display settings embedded in the CZI
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
                logger.warning("Calculation from display setting from CZI failed. " "Use 0-Max instead.")
                lower = 0
                higher = metadata.maxvalue[ch]

            # simple validity check
            if lower >= higher:
                logger.warning("Invalid Display Scaling detected. Use Defaults")
                lower = 0
                higher = np.round(metadata.maxvalue[ch] * 0.25, 0)

            # create a Channel layer and add it to the list of layers
            chl = ChannelLayer(
                sub_array=sub_array,
                metadata=metadata,
                name=layer_name,
                scale=scalefactors,
                colormap=ncmap,
                blending="additive",
                opacity=0.85,
                # napari requires strictly increasing float bounds.
                contrast_limits=(float(lower), float(higher)),
            )

            channel_layers.append(chl)

    return channel_layers


def process_channels_multiscale(levels: list, metadata: czimd.CziMetadata) -> list[ChannelLayer]:
    """Build multiscale ``ChannelLayer`` objects from a list of pyramid arrays.

    ``levels`` is the list returned by
    :func:`read_stacks_multiscale_compat` — one entry per pyramid level,
    coarsest last. Each entry is whatever ``read_stacks(stack_scenes=True)``
    produces at that zoom (typically an ``xarray.DataArray`` for the whole
    file, or a list of per-scene arrays when scenes differ in shape).

    For each level we reuse the existing :func:`process_channels` to slice
    it into per-channel ``ChannelLayer`` objects (identical logic for
    channel names, colormaps, contrast limits, scale, etc.). We then
    align the per-level layers by scene+channel and rewrite ``sub_array``
    on the level-0 layer to be a list ``[level0, level1, ...]``. napari
    picks up the list plus ``multiscale=True`` and renders the coarse
    level immediately while streaming finer tiles on zoom.

    Coarse levels reuse the finest level's ``scale``, ``colormap`` and
    ``contrast_limits`` — the color/contrast metadata is per channel, not
    per resolution, and napari handles per-level scale internally by
    comparing array shapes.

    Args:
        levels: Multiscale list from :func:`read_stacks_multiscale_compat`.
            Must contain at least one entry (layer 0).
        metadata: Parsed :class:`czimd.CziMetadata` shared across levels.

    Returns:
        List of ``ChannelLayer`` objects, one per scene/channel pair,
        whose ``sub_array`` is the multiscale list.
    """
    if not levels:
        return []

    # Extract per-level ChannelLayers. Every level shares the same S/T/C/Z
    # structure, so the returned per-level lists have identical length and
    # order.
    per_level = [process_channels(level, metadata) for level in levels]

    # Guard against empty per-level results (e.g. broken pyramid metadata).
    if not per_level[0]:
        return []

    # For each channel index, take the level-0 ChannelLayer as the template
    # and replace ``sub_array`` with the list of per-level sub_arrays.
    combined: list[ChannelLayer] = []
    n_channels = len(per_level[0])
    for ch_idx in range(n_channels):
        base = per_level[0][ch_idx]
        multiscale_sub = [pl[ch_idx].sub_array for pl in per_level if ch_idx < len(pl)]
        # dataclasses.replace preserves all other fields (name, colormap,
        # scale, contrast_limits, ...) which are level-independent.
        combined.append(replace(base, sub_array=multiscale_sub))

    return combined
