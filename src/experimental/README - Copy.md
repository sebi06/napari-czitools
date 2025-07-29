# napari-czann-segment

[![License](https://img.shields.io/pypi/l/napari-czann-segment.svg?color=green)](https://github.com/sebi06/napari-czann-segment/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-czann-segment.svg?color=green)](https://pypi.org/project/napari-czann-segment)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-czann-segment.svg?color=green)](https://python.org)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-czann-segment)](https://napari-hub.org/plugins/napari-czann-segment)

Semantic Segmentation of multidimensional images using Deep Learning ONNX models packaged as *.czann files.

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

![Train on APEER and use model in Napari](https://github.com/sebi06/napari-czann-segment/raw/main/readme_images/Train_APEER_run_Napari_CZANN_no_highlights_small.gif)

## Installation

Before installing, please setup a conda environment. If you have never worked with conda environments, go through [this tutorial](https://biapol.github.io/blog/johannes_mueller/anaconda_getting_started/) first.

You can then install `napari-czann-segment` via [pip]:

    pip install napari-czann-segment

## What does the plugin do

The plugin allows you to:

- Use a *.czann file containing the Deep Neural Network (ONNX) for semantic segmentation and metadata
- Segmentation will be applied per 2D plane for all dimensions
- Processing larger multidimensional images it uses the [cztile] package to chunk the individual 2d arrays using a specific overlap.
- multidimensional images will be processed plane-by-plane

## What does the plugin NOT do

**Before one can actually use a model it needs to be trained, which is NOT done by this plugin**.

There are two main ways hwo such a model can be created:

- Train the segmentation model fully automated on [APEER] and download the *.czann file
- Train your model in a Jupyter notebook etc. and package it using the [czmodel] python package as an *.czann

## Using this plugin

### Sample Data

A test image and a *.czann model file can be downloaded [here](https://github.com/sebi06/napari-czann-segment/tree/main/src/napari_czann_segment/_data).

- `PGC_20X.ome.tiff` --> use `PGC_20X_nucleus_detector.czann` to segment

In order to use this plugin the user has to do the following things:

- Open the image using "File - Open Files(s)" (requires [napari-aicsimageio] plugin).
- Click **napari-czann-segment: Segment with CZANN model** in the "Plugins" menu.
- **Select a czann file** to use the model for segmentation.
- metadata of the model will be shown (see example below)

| Parameter    | Value                                        | Explanation                                             |
| :----------- | :------------------------------------------- | ------------------------------------------------------- |
| model_type   | ModelType.SINGLE_CLASS_SEMANTIC_SEGMENTATION | see: [czmodel] for details                              |
| input_shape  | [1024, 1024, 1]                              | tile dimensions of model input                          |
| output_shape | [1024, 1024, 3]                              | tile dimensions of model output                         |
| model_id     | ba32bc6d-6bc9-4774-8b47-20646c7cb838         | unique GUID for that model                              |
| min_overlap  | [128, 128]                                   | tile overlap used during training (for this model)      |
| classes      | ['background', 'grains', 'inclusions']       | available classes                                       |
| model_name   | APEER-trained model                          | name of the model                                       |

![Napari - Image loaded and czann selected](https://github.com/sebi06/napari-czann-segment/raw/main/readme_images/napari_czann1.png)

- Adjust the **minimum overlap** for the tiling (optional, see [cztile] for details).
- Select the **layer** to be segmented.
- Toggle **Use GPU for inference** checkbox to enable / disable using a GPU (Nvidia) for the segmentation (experimental feature).
- Press **Segment Selected Image Layer** to run the segmentation.

![Napari - Image successfully segmented](https://github.com/sebi06/napari-czann-segment/raw/main/readme_images/napari_czann3.png)

A successful is obviously only the starting point for further image analysis steps to extract the desired numbers from the segmented image.
Another example is shown below demonstrating a simple "Grain Size Analysis" using a deep-learning model trained on [APEER] used in [napari]

![Napari - Simple Grain Size Analysis](https://github.com/sebi06/napari-czann-segment/raw/main/readme_images/grainsize_czann_napari.png)

### Remarks

> **IMPORTANT**: Currently the plugin only supports using models trained on a **single channel** image. Therefore, make sure that during the training on [APEER] or somewhere else the correct inputs images are used.
> It is quite simple to train a single RGB image, which actually has three channels, load this image in [napari] and notice only then that the model will not work, because the image will 3 channels inside [napari].

- Only the CPU will be used for the inference using the ONNX runtime for the [ONNX-CPU] runtime
- GPUs are supported but require the [ONNX-GPU] runtime and the respective CUDA libraries.
- Please check the [YAML](env_napari_czann_segment.yml) for an example environment with GPU support.
- See also [pytorch] for instruction on how to install pytorch

## For developers

- **Please clone this repository first using your favorite tool.**

- **Ideally one creates a new [conda] environment or use an existing environment that already contains [Napari].**

Feel free to create a new environment using the [YAML](env_napari_czann_segment.yml) file at your own risk:

    cd the-github-repo-with-YAML-file
    conda env create --file conda_env_napari_czann_segment.yml
    conda activate napari_czmodel

- **Install the plugin locally**

Please run the following command:

    pip install -e .

To install latest development version:

    pip install git+https://github.com/sebi06/napari_czann_segment.git

## Contributing

Contributions and Feedback are very welcome.

## License

Distributed under the terms of the [BSD-3] license,
"napari-czann-segment" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/sebi06/napari-czann-segment/issues
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
[czmodel]: https://pypi.org/project/czmodel/
[cztile]: https://pypi.org/project/cztile/
[APEER]: https://www.apeer.com
[napari-aicsimageio]: https://github.com/AllenCellModeling/napari-aicsimageio
[ONNX-GPU]: https://pypi.org/project/onnxruntime-gpu/
[ONNX-CPU]: https://pypi.org/project/onnxruntime/
[conda]: https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html
[pytorch]: https://pytorch.org/get-started/locally
