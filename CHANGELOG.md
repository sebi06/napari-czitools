# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Removed the **Lazy Loading** checkbox from the advanced reader. Pixel data
	now always uses the recommended lazy multiscale path; eager loading remains
	available through the Python API.
- Increased the advanced reader dock's horizontal expansion limit to 8192
	pixels for wide metadata tables and controls.
- Prevented the reader controls from jumping downward when metadata hides
	single-position dimension sliders.
- Kept the **Slider Type** selector above the metadata area when switching
	between table and tree views.

## [0.12.2] - 2026-08-27

### Added

- Added drag-and-drop support for one local `.czi` file in the advanced
	reader's file selector.
- Added a persistent **3D preview size** setting to control the maximum edge of
	generated coarse pyramid levels.
- Added `pytest-mock` to the testing dependencies and activated the file-change
	tests.

### Changed

- Updated the minimum required `czitools` version to `>=0.22.1`.
- Centralized the conservative 2048-pixel coarse-edge default and documented
	how Python callers can override it.

### Fixed

- Fixed 3D rendering for large Z-stacks by generating coarse pyramid levels
	that fit broadly supported OpenGL 3D texture limits.
- Single-level pyramids are now passed to napari as single-scale data so
	napari can apply its own downsampling fallback.

## [0.12.1] - 2026-08-24

### Added
- Added Mermaid diagram instructions for architecture documentation.

### Changed
- Updated required `czitools` version to >= 0.21.0 for improved compatibility.
- Refactored lazy-loading implementation in `_io.py` and `_reader.py` for better performance and reliability.
- Improved documentation in README with clarifications on lazy-loading behavior and usage patterns.
- Enhanced `copilot-instructions.md` with additional guidance for contributors and maintainers.

### Fixed
- Fixed lazy-loading bug in `_io.py` and `_widget.py` to ensure proper data streaming and display updates.

### Dependencies
- czitools >= 0.21.0

## [0.12.0] - 2026-08-21

### Added
- Updated the plugin to align with `czitools>=0.20.0`.

### Changed
- Clarified lazy-loading behavior in the reader and documentation.
- Fixed README rendering issues for PyPI by switching to absolute GitHub image URLs and current badge URLs.
- Expanded compatibility notes and contributor guidance for Python 3.12/3.13 and CI behavior.

### Documentation
- Fixed README badges and image links so they render correctly on GitHub and PyPI.
- Added a user-facing explanation of the `Lazy Loading` checkbox and what happens behind the scenes.
- Removed outdated compatibility notes from earlier `czitools` versions.

## [0.0.11] - 2026-04-10

### Added
- Replaced the custom hand-coded `DoubleRangeSlider` (~600 lines) with thin wrappers around **superqt**'s `QLabeledRangeSlider` and `QRangeSlider`.

### Changed
- Fixed single-frame extraction: both slider handles can now sit on the same value (e.g. 4–4).
- Updated CI workflow actions to Node.js 24-compatible versions.

### Fixed
- Fixed slider API to work with superqt wrappers while maintaining backward compatibility.

## [0.0.10] - 2026-03-29

### Added
- Initial release with napari plugin for CZI file reading and metadata extraction.

### Changed
- Replaced the custom hand-coded `DoubleRangeSlider` (~600 lines) with thin wrappers around **superqt**'s `QLabeledRangeSlider` and `QRangeSlider`.
- Updated CI workflow actions to Node.js 24-compatible versions.

### Documentation
- Updated `README.md` with superqt slider descriptions and compatibility notes.
- Updated `.github/copilot-instructions.md` with slider refactoring guidance and handle-overlap patch documentation.

## [0.0.9] - 2026-03-12

### Added
- Initial plugin development and setup.

---

[Unreleased]: https://github.com/sebi06/napari-czitools/compare/v0.12.1...HEAD
[0.12.1]: https://github.com/sebi06/napari-czitools/compare/v0.12.0...v0.12.1
[0.12.0]: https://github.com/sebi06/napari-czitools/compare/v0.0.11...v0.12.0
[0.0.11]: https://github.com/sebi06/napari-czitools/compare/v0.0.10...v0.0.11
[0.0.10]: https://github.com/sebi06/napari-czitools/compare/v0.0.9...v0.0.10
[0.0.9]: https://github.com/sebi06/napari-czitools/releases/tag/v0.0.9
