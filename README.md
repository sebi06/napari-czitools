- [napari-czitools](#napari-czitools)
  - [Installation](#installation)
  - [Supported Operating Systems](#supported-operating-systems)
  - [Usage - Core Functionalities](#usage---core-functionalities)
    - [Open Complete CZI Files](#open-complete-czi-files)
    - [Open CZI Sample Data](#open-czi-sample-data)
      - [CellDivision 5D Stack](#celldivision-5d-stack)
      - [Neurons 3D Stack](#neurons-3d-stack)
      - [AiryScan 3D Stack](#airyscan-3d-stack)
      - [Wellplate Data](#wellplate-data)
    - [Advanced CZI Reader (CziReadTools) plugin](#advanced-czi-reader-czireadtools-plugin)
      - [Lazy Loading](#lazy-loading)
  - [Current Limitations](#current-limitations)
    - [Future plans](#future-plans)
  - [Contributing](#contributing)
    - [Running Tests](#running-tests)
    - [Recent Compatibility Notes](#recent-compatibility-notes)
  - [License](#license)
  - [Issues](#issues)
- [Disclaimer](#disclaimer)

# napari-czitools

[![License MIT](https://img.shields.io/pypi/l/napari-czitools.svg?color=green)](https://github.com/sebi06/napari-czitools/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-czitools.svg?color=green)](https://pypi.org/project/napari-czitools)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-czitools.svg?color=green)](https://python.org)
[![tests](https://github.com/sebi06/napari-czitools/actions/workflows/test_and_deploy_pypi.yml/badge.svg)](https://github.com/sebi06/napari-czitools/actions/workflows/test_and_deploy_pypi.yml)
[![codecov](https://codecov.io/gh/sebi06/napari-czitools/branch/main/graph/badge.svg)](https://codecov.io/gh/sebi06/napari-czitools)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-czitools)](https://napari-hub.org/plugins/napari-czitools)
[![npe2](https://img.shields.io/badge/plugin-npe2-blue?link=https://napari.org/stable/plugins/index.html)](https://napari.org/stable/plugins/index.html)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)

Plugin to read CZI image file and metadata

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template].

![napari-czitools - Read CZI Metadata and load image Data](https://github.com/sebi06/napari-czitools/raw/main/readme_images/title_pic.png)

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/napari-plugin-template#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->

## Installation

You can install `napari-czitools` via [pip]:

    pip install napari-czitools

The current release requires Python 3.12 or 3.13 and `czitools>=0.20.0`.

To install latest development version :

    pip install git+https://github.com/sebi06/napari-czitools.git

## Supported Operating Systems

The test suite runs on Python 3.12 and 3.13 for:

- Linux
- Windows
- macOS

## Usage - Core Functionalities

The plugin provides a reader for CZI files and allows to load the image data into [napari]. It also reads the metadata from the CZI file and displays it in the metadata panel of [napari].

### Open Complete CZI Files

- Open complete CZI Files and display the metadata in Napari using the [czitools] package

![Open complete CZI file](https://github.com/sebi06/napari-czitools/raw/main/readme_images/file_open_mdtable_lls7.png)

- Open different CZI Image sample data
- if not found locally in current directory `../src/napari_czitools/sample_data` it will be opened from remote repository (might be slow)

![Open sample data](https://github.com/sebi06/napari-czitools/raw/main/readme_images/open_sample1.png)

### Open CZI Sample Data

#### CellDivision 5D Stack

![Sample Data - 5D Stack](https://github.com/sebi06/napari-czitools/raw/main/readme_images/open_sample_5D.png)

#### Neurons 3D Stack

![Sample Data - 3D Stack](https://github.com/sebi06/napari-czitools/raw/main/readme_images/open_sample_3D.png)

#### AiryScan 3D Stack

![Sample Data - AiryScan 3D Stack](https://github.com/sebi06/napari-czitools/raw/main/readme_images/open_sample_airyscan.png)

#### Wellplate Data

![Sample Data - Wellpate](https://github.com/sebi06/napari-czitools/raw/main/readme_images/open_sample_wellplate.png)

### Advanced CZI Reader (CziReadTools) plugin

Select the plugin to show the UI in the right panel of the Napari UI via "Plugins > Advanced CZI Reader (CziReadTools)"

1) Select the CZI file to read its metadata
2) Once the metadata are read the display can be toggled between a **table** and a **tree view**
3) The metadata will update the dimension range sliders (powered by [superqt]'s `QLabeledRangeSlider`) and enable reading the pixel data

<img src="https://github.com/sebi06/napari-czitools/raw/main/readme_images/reader_adv1.png" alt="Advanced CZI Reader - Plugin" style="width:30%; height:auto;">

1) Metadata will be shown as a **table** or as a **tree view**
2) The **Load Pixel Data** button will be enabled once the metadata is read
3) The **Dimension Sliders** (using [superqt]'s dual-handle range slider) will be enabled and allow to select a range to be read for all available dimensions. Both handles can be set to the same value for single-slice selection (e.g. 3-3)

<img src="https://github.com/sebi06/napari-czitools/raw/main/readme_images/reader_adv2.png" alt="Advanced CZI Reader - Plugin" style="width:80%; height:auto;">

- The dimension range sliders (from [superqt]) allow to define the size of a CZI subset to be read
- This allows to read parts of a CZI image dataset
- Important - when reading a subset the metadata will still reflects the size of the complete CZI

![Advanced CZI Reader - Plugin](https://github.com/sebi06/napari-czitools/raw/main/readme_images/load_pixel1.png)

- Example for reading a subset
  - Timepoints (4-7): 4 slices or T=4
  - Channels (0-0): 1 slice or CH=1
  - Z-Plane (7-10): 4 slices or Z=4

![Advanced CZI Reader - Plugin](https://github.com/sebi06/napari-czitools/raw/main/readme_images/load_pixel2.png)

#### Lazy Loading

The **Lazy Loading** checkbox is enabled by default. It controls which
`czitools` reader is used after **Load Pixel Data** is pressed:

- **Enabled:** the plugin calls `read_tools.read_stacks` with `use_dask=True`
  and the selected scene, time, channel, and Z ranges. This scene-aware path
  returns Dask-backed xarray stacks — one per equal-sized scene group, or a
  list when scene shapes differ. Pixel planes are read only when napari asks
  for them. The plugin creates one napari image layer per channel and appends
  a scene suffix to layer names when separate scene stacks are returned.
- **Disabled:** the plugin calls `read_tools.read_6darray` and constructs one
  regular NumPy array in `STCZYX(A)` order. This eager path loads every
  selected plane into RAM and requires the selected scenes to have compatible
  shapes.

##### Gigapixel CZIs (whole-slide, large 2D scans)

For files whose individual 2D planes are larger than about 256 MB uncompressed
(for example a `93,555 × 138,996` `uint16` plane ≈ 24 GB), `czitools`
automatically switches to spatial Y/X tiling: each Dask chunk becomes one
ROI-based read via `pylibCZIrw`, so napari only fetches the tiles that
intersect the current viewport instead of full planes. Small planes keep the
faster whole-plane path.

On top of tiling, lazy mode also enables **multiscale rendering**. The plugin
calls `czitools.read_tools.read_stacks_multiscale` to detect the CZI's stored
pyramid levels (via `pylibCZIrw` subblock enumeration) and hands napari one
lazy Dask array per level as `viewer.add_image(..., multiscale=True)`. This
lets napari render the coarsest level immediately from a single GPU texture
and stream finer tiles on zoom. If the coarsest stored level is still larger
than the GPU texture limit (~16k px per edge), extra synthetic coarser
levels are added on the fly using libCZI's C++ resampler. Files without any
on-disk pyramid degrade transparently to a single-level "pyramid" and behave
as before.

To keep opening these files usable, the plugin also passes an explicit
`contrast_limits` argument to `viewer.add_image` (derived from the CZI's
embedded display settings). Without this, napari would auto-scan every chunk
of the Dask array to determine the display range and materialize the entire
plane in RAM before the first pixel is shown.

##### Advanced Python usage

The Python reader API forwards the same lazy behaviour:

```python
from napari_czitools._reader import reader_function_adv

reader_function_adv(
    "image.czi",
    use_lazy=True,        # widget checkbox — read_stacks path
    use_dask=True,        # required for on-demand reads
    use_multiscale=True,  # napari renders coarse-level tiles first
    max_coarse_edge=8192, # coarsest pyramid edge target (px)
)
```

With `use_lazy=True`, `czitools` reads the CZI metadata and builds Dask task
graphs first — individual pixel planes are not loaded at that point. When
`use_multiscale=True` (the default) the plugin also constructs a per-level
pyramid so napari can render gigapixel planes without materialising layer 0.
Disabling `use_lazy`, even with `use_dask=True`, still reads all pixels
eagerly before wrapping the result in a Dask array.

## Current Limitations

The plugin is still in its early stages; expect bugs and breaking changes.

- opening the sample CZI files will not display the CZI metadata right now

### Future plans

- upgrade [pylibCZIrw] to allow use [bioio-czi] for even better reading
- export of metadata table

Feedback is always welcome!

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

### Running Tests

Install test dependencies first (recommended for full local coverage):

    pip install -e ".[testing]"

This installs `pytest-qt`, which provides the `qtbot` fixture used by
napari/Qt tests.

**Windows/macOS:**

    pytest

**Linux (recommended - use tox):**

    tox -e py312-linux

(Replace `py312` with your Python version: `py312` or `py313`)

**Linux (direct pytest):**

    pytest -v --forked --color=yes

Note: The `--forked` flag is required on Linux to prevent CZI + Qt crashes by running each test in its own process. This flag is not available on Windows.

### Recent Compatibility Notes

- `czitools>=0.20.0` is required.
- `read_tools.read_stacks` returns
  `(arrays_or_list, dims, num_stacks, metadata)`. The plugin handles both a
  single stacked xarray object and a list containing one xarray stack per
  scene.
- Channel extraction uses positional indexing to support channel coordinates
  represented by names (for example `"DAPI"`, `"EGFP"`) instead of numeric
  labels.
- URL metadata tests can be affected by transient remote read failures (for
  example GitHub/network hiccups). The test suite retries and skips these
  network-dependent checks if remote headers cannot be read reliably.
- The custom dual-handle `DoubleRangeSlider` has been replaced with wrappers
  around [superqt]'s `QLabeledRangeSlider` and `QRangeSlider`, reducing
  custom painting/mouse handling code and using a well-tested community
  component. The public slider API (`low()`, `high()`, `setLow()`,
  `setHigh()`, single-value mode) is unchanged.
- A small internal patch (`_allow_handle_overlap`) is applied to every
  superqt range slider so that both handles can sit on the same value,
  enabling single-frame extraction (e.g. T=4-4 to read one timepoint).

## License

Distributed under the terms of the [MIT] license,
"napari-czitools" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

# Disclaimer

The software & scripts are free to use for everybody. The author undertakes no warranty concerning the use of this plugins and scripts. Use them on your own risk.

By using this plugin you agree to this disclaimer.

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[MIT]: http://opensource.org/licenses/MIT
[napari-plugin-template]: https://github.com/napari/napari-plugin-template
[file an issue]: https://github.com/sebi06/napari-czitools/issues
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[czitools]: https://pypi.org/project/czitools/
[pylibCZIrw]: https://pypi.org/project/pylibCZIrw/
[MaxOS wheels for pylibCZIrw]: https://pypi.scm.io/#/package/pylibczirw
[bioio-czi]: https://pypi.org/project/bioio-czi/
[superqt]: https://pyapp-kit.github.io/superqt/
