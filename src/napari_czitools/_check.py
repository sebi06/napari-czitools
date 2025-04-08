import napari

from napari_czitools._io import CZIDataLoader

path = r"src/napari_czitools/sample_data/RatBrain_Z79_ZSTD.czi"

# call the function to add the data to the viewer
czi = CZIDataLoader(
    path,
    zoom=1.0,
    use_dask=False,
    chunk_zyx=False,
    use_xarray=True,
    show_metadata="table",
)

# add the data to the viewer
czi.add_to_viewer()

napari.run()
