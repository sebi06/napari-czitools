import numpy as np

from napari_czitools import napari_get_reader


# tmp_path is a pytest fixture
def test_reader(tmp_path):
    """An example of how you might test your plugin."""

    # try to read it back in
    # reader = napari_get_reader(reader = napari_get_reader(r"src\napari_czitools\sample_data\CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi"))
    # assert callable(reader)
    pass

    # # make sure we're delivering the right format
    # layer_data_list = reader(my_test_file)
    # assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    # layer_data_tuple = layer_data_list[0]
    # assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) > 0
    #
    # # make sure it's the same as it started
    # np.testing.assert_allclose(original_data, layer_data_tuple[0])


# def test_get_reader_pass():
#     reader = napari_get_reader("fake.file")
#     assert reader is None
