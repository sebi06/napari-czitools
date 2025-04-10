from czitools.read_tools import read_tools
from czitools.utils import logging_tools

from ._io import CZIDataLoader, process_channels

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
    return reader_function_adv


# this function is called when using Open -> Files(s) directly from the menu
def reader_function_adv(
    path: str, zoom=1.0, use_dask=False, chunk_zyx=False, use_xarray=True
):
    """Take a path, add layers and metadata to the viewer.

    This function reads a CZI file and adds its data to the viewer. It uses
    the CZIDataLoader class to handle the file loading and processing.

    Parameters
    ----------
    path : str
        Path to the CZI file.
    zoom : float, optional
        Zoom factor to apply to the image data. Default is 1.0.
    use_dask : bool, optional
        Whether to use dask for lazy loading of the data. Default is False.
    chunk_zyx : bool, optional
        Whether to chunk the data in the ZYX dimensions. Default is False.
    use_xarray : bool, optional
        Whether to use xarray for data representation. Default is True.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples. Each tuple contains (data, metadata, layer_type),
        where data is a numpy array or None, metadata is a dict of keyword arguments
        for the corresponding viewer.add_* method in Napari, and layer_type is a
        lower-case string naming the type of layer. In this implementation, it
        returns [(None,)] to allow customizing the viewer after the layers are added.
    """

    # call the function to add the data to the viewer
    czi = CZIDataLoader(
        path,
        zoom=zoom,
        use_dask=use_dask,
        chunk_zyx=chunk_zyx,
        use_xarray=use_xarray,
        show_metadata="table",
    )

    # add the data to the viewer
    czi.add_to_viewer()

    # return nothing to allow customizing the viewer after the layers are added
    return [(None,)]


# this one is use to show the provided sample data
# it does not allow to show the metadata because in order to work we need to return a
# layerdata tuple.
#
# See also: https://forum.image.sc/t/file-open-vs-open-sample-using-my-own-napari-plugin/111123/8?u=sebi06
#
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

    # # call the function to add the data to the viewer
    # layers = _add_czi_data(
    #     path,
    #     zoom=zoom,
    #     use_dask=use_dask,
    #     chunk_zyx=chunk_zyx,
    #     use_xarray=use_xarray,
    # )

    sample_data = []

    # return an array with dimension order STCZYX(A)
    array6d, metadata = read_tools.read_6darray(
        path,
        use_dask=use_dask,
        chunk_zyx=chunk_zyx,
        zoom=zoom,
        use_xarray=use_xarray,
    )

    # get the channel layers
    channel_layers = process_channels(array6d, metadata)

    for chl in channel_layers:

        sample_data.append(
            (
                chl.sub_array,
                {
                    "name": chl.name,
                    "scale": chl.scale,
                    "colormap": chl.colormap,
                    "blending": "additive",
                    "opacity": 0.85,
                },
                "image",
            )
        )

    # add the list of layers to th viewer
    return sample_data
    # return layers


# def _add_czi_data(
#     path: str,
#     zoom: float = 1.0,
#     use_dask: bool = False,
#     chunk_zyx: bool = False,
#     use_xarray: bool = True,
# ):

#     sample_data = []

#     # return an array with dimension order STCZYX(A)
#     array6d, metadata = read_tools.read_6darray(
#         path,
#         use_dask=use_dask,
#         chunk_zyx=chunk_zyx,
#         zoom=zoom,
#         use_xarray=use_xarray,
#     )

#     # get the channel layers
#     channel_layers = process_channels(array6d, metadata)

#     for chl in channel_layers:

#         sample_data.append(
#             (
#                 chl.sub_array,
#                 {
#                     "name": chl.name,
#                     "scale": chl.scale,
#                     "colormap": chl.colormap,
#                     "blending": "additive",
#                     "opacity": 0.85,
#                 },
#                 "image",
#             )
#         )

#     return sample_data
