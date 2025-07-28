import sys
import os

sys.path.insert(0, "src")

# Set headless environment
os.environ["HEADLESS"] = "1"

from napari_czitools._sample_data import celldivision_data

try:
    result = celldivision_data()
    print(f"Unexpected success: {result}")
except Exception as e:
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {e}")
    print("This is expected behavior - sample data should raise exception in headless environment")
