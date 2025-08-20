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
  - [Current Limitations](#current-limitations)
    - [Future plans](#future-plans)
  - [Contributing](#contributing)
  - [License](#license)
  - [Issues](#issues)
- [Disclaimer](#disclaimer)

# napari-czitools

[![License MIT](https://img.shields.io/pypi/l/napari-czitools.svg?color=green)](https://github.com/sebi06/napari-czitools/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-czitools.svg?color=green)](https://pypi.org/project/napari-czitools)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-czitools.svg?color=green)](https://python.org)
[![tests](https://github.com/sebi06/napari-czitools/workflows/tests/badge.svg)](https://github.com/sebi06/napari-czitools/actions)
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

To install latest development version :

    pip install git+https://github.com/sebi06/napari-czitools.git

## Supported Operating Systems

Currently this only tested on:

- Linux
- Windows

MacOS is not supported yet out of the box yet, but [czitools] uses [pylibCZIrw]. But it should be possible to install it manually: [MaxOS wheels for pylibCZIrw] (read and write CZI files on MacOS).

## Usage - Core Functionalities

The plugin provides a reader for CZI files and allows to load the image data into [napari]. It also reads the metadata from the CZI file and displays it in the metadata panel of [napari].

### Open Complete CZI Files

- Open complete CZI Files and display the metadata in Napari using the [czitools] package

![Open complete CZI file](./readme_images/file_open_mdtable_lls7.png)

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
3) The metadata will update the dimension double-range sliders and enable reading the pixel data

<img src="https://github.com/sebi06/napari-czitools/raw/main/readme_images/reader_adv1.png" alt="Advanced CZI Reader - Plugin" style="width:30%; height:auto;">

1) Metadata will be shown as a **table** or as a **tree view**
2) The **Load Pixel Data** button will be enabled once the metadata is read
3) The **Dimension Sliders** will be enabled and allow to select an range to be read for all available dimensions

<img src="https://github.com/sebi06/napari-czitools/raw/main/readme_images/reader_adv2.png" alt="Advanced CZI Reader - Plugin" style="width:80%; height:auto;">

- The dimensions slider allow to define size of CZI subset to be read
- This allows to read parts of a CZI image dataset
- Important - when reading a subset the metadata will still reflects the size of the complete CZI

![Advanced CZI Reader - Plugin](./readme_images/load_pixel1.png)

- Example for reading a subset
  - Timepoints (4-7): 4 slices or T=4
  - Channels (0-0): 1 slice or CH=1
  - Z-Plane (7-10): 4 slices or Z=4

![Advanced CZI Reader - Plugin](./readme_images/load_pixel2.png)

## Current Limitations

The plugin is still in its very early stage, therefor expect bugs and breaking changes

- reading CZI with multiple scenes only works when the scenes have equal size
- opening the sample CZI files will not display the CZI metadata right now

### Future plans

- allow reading individual scenes when scenes have different sizes
- upgrade [pylibCZIrw] to allow use [bioio-czi] for even better reading
- export of metadata table

Feedback is always welcome!

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"napari-czitools" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

# Disclaimer

The software & scripts are free to use for everybody. The author undertakes no warranty concerning the use of this plugins and scripts. Use them on your own risk.

By using this plugin you agree to this disclaimer.

Version: 2025.08.20

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[napari-plugin-template]: https://github.com/napari/napari-plugin-template
[file an issue]: https://github.com/sebi06/napari-czitools/issues
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[czitools]: https://pypi.org/project/czitools/
[pylibCZIrw]: https://pypi.org/project/pylibCZIrw/
[MaxOS wheels for pylibCZIrw]: https://pypi.scm.io/#/package/pylibczirw
[bioio-czi]: https://pypi.org/project/bioio-czi/
