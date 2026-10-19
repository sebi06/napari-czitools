#!/bin/bash

CONDA_ENV_PATH="${NAPARI_ENV_PATH:-${CONDA_PREFIX:-}}"
if [ -z "$CONDA_ENV_PATH" ]; then
	echo "Set NAPARI_ENV_PATH or activate the Conda environment first." >&2
	exit 2
fi

LIB_PATH="$CONDA_ENV_PATH/lib/libstdc++.so.6"
NAPARI_BIN="$CONDA_ENV_PATH/bin/napari"
if [ ! -f "$LIB_PATH" ]; then
	echo "Conda C++ runtime library not found: $LIB_PATH" >&2
	exit 2
fi
if [ ! -x "$NAPARI_BIN" ]; then
	echo "Napari executable not found: $NAPARI_BIN" >&2
	exit 2
fi

echo "--- Starting Napari with Conda-Specific Memory Fix ---"
echo "Using library: $LIB_PATH"

LD_PRELOAD="$LIB_PATH" \
MALLOC_CHECK_=3 \
AIOCP_MAX_WORKERS=1 \
"$NAPARI_BIN" "$@"
