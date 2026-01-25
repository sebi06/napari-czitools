#!/bin/bash

# 1. Path to your Conda environment
CONDA_ENV_PATH="/home/sebi06/miniconda3/envs/zenpy"

# 2. Use the Conda-specific library (This is usually the culprit)
LIB_PATH="$CONDA_ENV_PATH/lib/libstdc++.so.6"

echo "--- Starting Napari with Conda-Specific Memory Fix ---"
echo "Using library: $LIB_PATH"

# 3. Launch with extra stability flags
# We add MALLOC_CHECK_=3 to force the allocator to be more strict
LD_PRELOAD=$LIB_PATH \
MALLOC_CHECK_=3 \
AIOCP_MAX_WORKERS=1 \
$CONDA_ENV_PATH/bin/napari "$@"
