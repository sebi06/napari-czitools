from napari_czitools._reader import reader_function


def celldivision_data():
    """Opens 5D CZI image dataset"""

    filepath = "src/napari_czitools/sample_data/CellDivision_T15_Z20_CH2_X600_Y500_DCV_ZSTD.czi"

    return reader_function(filepath)


def wellplate_data():
    """Opens 6D CZI image dataset"""

    filepath = "src/napari_czitools/sample_data/testwell96_A1-D12_S48_T1_C2_Z1_X640_Y480_ZSTD.czi"

    return reader_function(filepath)
