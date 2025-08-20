import napari

from napari_czitools._io import CZIDataLoader
from napari_czitools._metadata_widget import MetadataDisplayMode

path = r"src/napari_czitools/sample_data/Tumor_HE_Orig_small.czi"
# path = r"src/napari_czitools/sample_data/RatBrain_Z79_ZSTD.czi"
# path = r"F:\Github\napari-czitools\src\napari_czitools\sample_data\CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi"
#path = r"https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi"


# call the function to add the data to the viewer
czi = CZIDataLoader(
    path,
    zoom=1.0,
    use_dask=False,
    chunk_zyx=False,
    use_xarray=True,
    show_metadata=MetadataDisplayMode.TABLE,
)

# add the data to the viewer
czi.add_to_viewer()

napari.run()
