## Summary

This PR adapts the plugin to `czitools` `v0.15.0` and resolves sample-data test failures caused by the upstream `read_stacks` signature change.

## Problem

`czitools==0.15.0` changed `read_tools.read_stacks` from returning 3 values to 4 values:

- old: `(array6d, dims, num_stacks)`
- new: `(array6d, dims, num_stacks, metadata)`

The plugin still unpacked 3 values, which raised `ValueError: too many values to unpack (expected 3)`. In sample-data paths this got wrapped into:

`FileNotFoundError: Sample data unavailable in headless/CI environment`

and caused failures in:

- `test_open_sample_with_viewer[unique_id.0]`
- `test_open_sample_with_viewer[unique_id.1]`
- `test_open_sample_with_viewer[unique_id.2]`
- `test_open_sample_with_viewer[unique_id.3]`

## Changes

### Runtime compatibility

- Added `read_stacks_compat(...)` in `src/napari_czitools/_io.py`.
- `read_stacks_compat` accepts both tuple lengths:
  - 4-tuple: uses metadata returned by `czitools`.
  - 3-tuple: reconstructs metadata via `CziMetadata(path)` for backward compatibility.
- Updated `CZIDataLoader.add_to_viewer` in `src/napari_czitools/_io.py` to use compatibility wrapper.
- Updated `reader_function` in `src/napari_czitools/_reader.py` to use compatibility wrapper.

### Documentation

- Updated `README.md` with a note about `czitools==0.15.0` `read_stacks` return signature.
- Updated `.github/copilot-instructions.md` with explicit guidance to keep compatibility for both return shapes.

## Validation

Executed in conda environment `smartmic`:

- `python -m pytest -q`

Result:

- `134 passed, 16 warnings in 57.58s`

## Notes

- Warnings are existing Qt/deprecation warnings and not introduced by this PR.
- Behavior remains backward-compatible for older `czitools` versions while supporting `v0.15.0`.
