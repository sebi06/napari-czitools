#!/usr/bin/env python
"""Test script to verify lazy loading fix for threading issue."""

import sys

# Clear any cached modules
for mod in list(sys.modules.keys()):
    if "napari_czitools" in mod:
        del sys.modules[mod]

print("Testing lazy loading fix...")
print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")
print()

try:
    from napari_czitools._sample_data import celldivision_data

    print("✓ Module imports successful")

    print("Loading sample data with lazy loading...")
    result = celldivision_data()

    if result and len(result) == 2:
        print(f"✓ Successfully loaded {len(result)} layers")
        print(f"  Layer 1: {result[0][1]['name']}")
        print(f"  Layer 2: {result[1][1]['name']}")
        print()
        print("✅ Lazy loading fix is working! No threading crash.")
        sys.exit(0)
    else:
        print(f"✗ Unexpected result: {result}")
        sys.exit(1)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
