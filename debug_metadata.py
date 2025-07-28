import sys
import os

sys.path.insert(0, "src")
from napari_czitools._utilities import check_filepath
from czitools.metadata_tools import czi_metadata as czimd

# Clear headless environment
os.environ.pop("HEADLESS", None)
os.environ.pop("CI", None)
os.environ.pop("GITHUB_ACTIONS", None)

filepath = check_filepath("CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi")
print(f"File path: {filepath}")
print(f"File exists: {os.path.exists(filepath) if filepath else False}")

if filepath:
    try:
        # This is what happens inside read_6darray
        mdata = czimd.CziMetadata(filepath)
        print(f"Metadata loaded: {mdata is not None}")
        print(f"Has bbox: {hasattr(mdata, 'bbox')}")
        if hasattr(mdata, "bbox"):
            print(f"bbox is: {mdata.bbox}")
            print(f"bbox type: {type(mdata.bbox)}")
            if hasattr(mdata.bbox, "total_bounding_box"):
                print(f"total_bounding_box is: {mdata.bbox.total_bounding_box}")
                print(f"total_bounding_box type: {type(mdata.bbox.total_bounding_box)}")
    except Exception as e:
        print(f"Error during metadata reading: {type(e).__name__}: {e}")
