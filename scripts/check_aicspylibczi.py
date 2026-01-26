from pathlib import Path

from aicspylibczi import CziFile

# Adjust path to point to one of your real sample files
file_path = Path(
    "/datadisk1/Github/napari-czitools/src/napari_czitools/sample_data/CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi"
)

print(f"Attempting to read: {file_path}")
try:
    czi = CziFile(file_path)
    print("File opened. Reading metadata...")
    # This is where your stack trace says it crashes
    print("Reading subblock metadata...")
    # Trigger the specific function from your stack trace if possible,
    # or just read a plane to force internal metadata access
    dims = czi.dims
    print(f"Dimensions: {dims}")
except Exception as e:
    print(f"Python captured error: {e}")

print("Test finished without hard crash.")
