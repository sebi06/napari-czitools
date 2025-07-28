from czitools.read_tools import read_tools
from czitools.metadata_tools import czi_metadata as CziMetadata

url = r"https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi"

# return an array with dimension order STCZYX(A)
array6d, mdata = read_tools.read_6darray(url)

print(f"Array shape: {array6d.shape}")

# # What happens internally in czitools when reading from URL:
# mdata = CziMetadata(url)  # This partially works
# # But when it tries to access bounding box information:
# mdata.bbox.total_bounding_box  # This becomes None for URLs
# # Leading to:
# if k in mdata.bbox.total_bounding_box.keys():  # AttributeError!
