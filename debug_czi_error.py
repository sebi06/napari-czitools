import sys
import os

sys.path.insert(0, "src")

# Clear headless environment
os.environ.pop("HEADLESS", None)
os.environ.pop("CI", None)
os.environ.pop("GITHUB_ACTIONS", None)

from napari_czitools._sample_data import celldivision_data

try:
    result = celldivision_data()
    print("Success:", type(result))
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    if hasattr(e, "__cause__") and e.__cause__:
        print(f"Caused by: {type(e.__cause__).__name__}: {e.__cause__}")
        print(f"Original error: {e.__cause__}")
