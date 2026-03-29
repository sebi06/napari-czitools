## Summary

This PR replaces the custom hand-coded `DoubleRangeSlider` QSlider subclass (~600 lines of manual `paintEvent`/`mousePressEvent`/`mouseMoveEvent`) with thin wrappers around **superqt**'s `QLabeledRangeSlider` and `QRangeSlider`. It also updates CI workflow actions to Node.js 24-compatible versions.

## Problem

- The custom dual-handle slider was difficult to maintain (~600 lines of low-level Qt painting and mouse-handling code).
- `superqt` was already a declared dependency but its range slider widgets were not used.
- superqt's `QRangeSlider` enforces a minimum gap of `singleStep()` (default 1) between handles, which prevented single-frame extraction (e.g. both handles at value 4).
- GitHub Actions `actions/checkout@v4`, `actions/setup-python@v5`, and `codecov/codecov-action@v3` use deprecated or soon-to-be-deprecated Node.js runtimes (16/20).

## Changes

### Slider refactoring

- **Rewrote** `src/napari_czitools/_doublerange_slider.py`:
  - `LabeledDoubleRangeSliderWidget` now wraps `QLabeledRangeSlider` from superqt with a dimension label + slice readout.
  - `DoubleRangeSlider` now wraps `QRangeSlider` from superqt with `low()`/`high()`/`setLow()`/`setHigh()` API.
  - Added `_allow_handle_overlap()` helper that monkey-patches superqt's internal `_neighbor_bound` method to use zero gap, enabling single-frame extraction (both handles at same value).
  - Full type annotations (`tuple[int, ...]`, `QSlider.TickPosition`, `Qt.Orientation`, `Any`).
  - Public API unchanged — all consumers in `_widget.py` work without modification.
- **Rewrote** `src/napari_czitools/_tests/test_doublerange_slider.py`:
  - 31 tests covering the new wrapper classes (no more mock painting/mouse tests).
  - Includes single-value mode and handle overlap tests.

### CI workflow updates (Node.js 24)

- **Updated** `.github/workflows/test_and_deploy_pypi.yml`:
  - `actions/checkout` v4 → v6 (Node.js 24)
  - `actions/setup-python` v5 → v6 (Node.js 24)
  - `codecov/codecov-action` v3 → v5 (Node.js 20, replaces deprecated Node.js 16)
- **Updated** `.github/workflows/test_and_deploy_testpypi.yml`:
  - Same action version bumps as above.
- `tlambert03/setup-qt-libs@v1` and `aganders3/headless-gui@v2` remain unchanged (already on Node.js 20, no newer major version available).

### Documentation

- **Updated** `README.md` with superqt slider descriptions and compatibility notes.
- **Updated** `.github/copilot-instructions.md` with slider refactoring guidance, handle-overlap patch notes, and preference to use the superqt wrapper API.

## Validation

Executed in conda environment `smartmic` (Python 3.12.12, PyQt5 5.15.11):

- `python -m pytest src/napari_czitools/_tests/test_doublerange_slider.py src/napari_czitools/_tests/test_scene_constraint.py src/napari_czitools/_tests/test_widget.py src/napari_czitools/_tests/test_widget_comprehensive.py -v`

Result:

- `54 passed, 16 warnings in 12.35s`

## Notes

- Warnings are existing Qt/pydantic deprecation warnings and not introduced by this PR.
- `superqt` is already a declared dependency in `pyproject.toml` — no new dependencies added.
- The handle-overlap patch (`_allow_handle_overlap`) is applied at construction time to every slider instance and only overrides one internal method on superqt's `_GenericRangeSlider`.
