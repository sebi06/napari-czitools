import napari
import numpy as np
from czitools.read_tools import read_tools
from czitools.utils import logging_tools
from napari.utils.colormaps import Colormap

logger = logging_tools.set_logging()


def napari_get_reader(path: str):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".czi"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(
    path: str, zoom=1.0, use_dask=False, chunk_zyx=False, use_xarray=True
):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """

    # call the function to add the data to the viewer
    _add_czi_data(
        path,
        zoom=zoom,
        use_dask=use_dask,
        chunk_zyx=chunk_zyx,
        use_xarray=use_xarray,
    )

    # return nothing to allow customizing the viewer after the layers are added
    return [(None,)]


def _add_czi_data(
    path: str,
    zoom: float = 1.0,
    use_dask: bool = False,
    chunk_zyx: bool = False,
    use_xarray: bool = True,
):

    # get napari viewer from current process
    viewer = napari.current_viewer()

    # return an array with dimension order STCZYX(A)
    array6d, metadata = read_tools.read_6darray(
        path,
        use_dask=use_dask,
        chunk_zyx=chunk_zyx,
        zoom=zoom,
        use_xarray=use_xarray,
    )

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

        # add the channel to the viewer
        viewer.add_image(
            sub_array,
            name=chname,
            colormap=ncmap,
            blending="additive",
            scale=scalefactors,
            gamma=0.85,
        )

        # set the axis labels based on the dimensions
        viewer.dims.axis_labels = sub_array.dims
