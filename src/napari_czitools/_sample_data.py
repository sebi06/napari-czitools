from __future__ import annotations

from czitools.read_tools import read_tools
from czitools.metadata_tools.czi_metadata import CziMetadata
from napari.utils.colormaps import Colormap
import numpy as np
from typing import Dict, Tuple, Optional, Union, Annotated, List
from typing import Literal, Protocol, Sequence
from numpy.typing import ArrayLike, NDArray

# LayerTypeName = Literal[
#     "image", "labels", "points", "shapes", "surface", "tracks", "vectors"
# ]
# LayerProps = Dict
# DataType = Union[ArrayLike, Sequence[ArrayLike]]
# FullLayerData = Tuple[DataType, LayerProps, LayerTypeName]
# LayerData = Union[Tuple[DataType], Tuple[DataType, LayerProps], FullLayerData]


def celldivision_data():
    # def make_sample_data():
    """Opens 5D CZI image dataset"""
    # Return list of tuples
    # [(data1, add_image_kwargs1, "image")]
    # Check the documentation for more information about the
    # add_image_kwargs
    # https://napari.org/stable/api/napari.Viewer.html#napari.Viewer.add_image

    # Create a 5D array with shape (4, 2, 5, 3, 150, 100) and random integers between 0 and 256
    # array6d = np.random.randint(0, 256, size=(4, 2, 5, 3, 150, 100), dtype=np.uint8)

    filepath = "src/napari_czitools/sample_data/CellDivision_T15_Z20_CH2_X600_Y500_DCV_ZSTD.czi"

    layer_sample_data = read_and_create_sample_data(filepath)

    return layer_sample_data


def wellplate_data():
    """Opens 6D CZI image dataset"""

    filepath = "src/napari_czitools/sample_data/testwell96_A1-D12_S48_T1_C2_Z1_X640_Y480_ZSTD.czi"

    return read_and_create_sample_data(filepath)


def read_and_create_sample_data(filepath: str):

    sample_data = []

    # return an array with dimension order STCZYX(A)
    array6d, mdata = read_tools.read_6darray(
        filepath,
        use_dask=False,
        chunk_zyx=False,
        zoom=1.0,
        use_xarray=True,
    )

    # loop over all channels
    for ch in range(array6d.sizes["C"]):

        # extract channel subarray
        sub_array = array6d.sel(C=ch)

        # get the scaling factors for that channel and adapt Z-axis scaling
        scalefactors = [1.0] * len(sub_array.shape)
        scalefactors[sub_array.get_axis_num("Z")] = (
            mdata.scale.ratio["zx_sf"] * 1.00001
        )

        # remove the last scaling factor in case of an RGB image
        if "A" in sub_array.dims:
            # remove the A axis from the scaling factors
            scalefactors.pop(sub_array.get_axis_num("A"))

        # get colors and channel name
        chname = mdata.channelinfo.names[ch]

        # inside the CZI metadata_tools colors are defined as ARGB hexstring
        rgb = "#" + mdata.channelinfo.colors[ch][3:]
        ncmap = Colormap(["#000000", rgb], name="cm_" + chname)

        sample_data.append(
            (
                sub_array,
                {
                    "name": chname,
                    "scale": scalefactors,
                    "colormap": ncmap,
                    "blending": "additive",
                    "opacity": 1.0,
                    "gamma": 0.85,
                    # "axis_labesl": sub_array.dims,
                },
                "image",
            )
        )

    return sample_data
