from czitools.metadata_tools.czi_metadata import CziMetadata

from napari_czitools._utilities import check_filepath

url = r"https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi"


out = check_filepath(url)

# What happens internally in czitools when reading from URL:
print("Creating CziMetadata from URL...")
mdata = CziMetadata(url)  # This partially works
print(f"Metadata created successfully: {mdata}")
print(f"Has bbox: {hasattr(mdata, 'bbox')}")
print(f"bbox type: {type(mdata.bbox)}")
print(f"total_bounding_box: {mdata.bbox.total_bounding_box}")
print(f"total_bounding_box type: {type(mdata.bbox.total_bounding_box)}")

# Leading to:
k = "T"
print(f"\nTesting access to key '{k}'...")
if mdata.bbox.total_bounding_box is not None:
    if k in mdata.bbox.total_bounding_box:  # This should work!
        print(f"SUCCESS: {mdata.bbox.total_bounding_box[k]}")
    else:
        print(f"Key '{k}' not found in bounding box")
else:
    print("ERROR: total_bounding_box is None!")
