from czitools.utils import logging_tools

from napari_czitools._reader import reader_function
from napari_czitools._utilities import check_filepath

logger = logging_tools.set_logging()


def celldivision_data():
    """Opens 5D CZI image dataset"""

    filepath = check_filepath(
        "CellDivision_T15_Z20_CH2_X600_Y500_DCV_ZSTD.czi"
    )

    return reader_function(filepath)


def wellplate_data():
    """Opens 6D CZI image dataset"""

    filepath = check_filepath(
        "testwell96_A1-D12_S48_T1_C2_Z1_X640_Y480_ZSTD.czi"
    )

    return reader_function(filepath)


def zstack_data():
    """Opens 3D CZI image dataset"""

    filepath = check_filepath("RatBrain_Z79_ZSTD.czi")

    return reader_function(filepath)
