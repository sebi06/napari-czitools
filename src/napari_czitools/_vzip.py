"""Lazy reading of CZI-derived refkv archives, independent of viewer state."""

import typing
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.request import url2pathname

import numpy as np

INSTALL_HINT = 'Install VZIP support with: pip install "napari-czitools[vzip]"'


def vzip_available() -> bool:
    """Check availability without importing optional refkv modules."""
    return find_spec("refkv") is not None


@dataclass
class VzipImage:
    """One image series with its OME axes, levels, and display metadata."""

    name: str
    axes: typing.Tuple[str, ...]
    arrays: typing.List[Any]
    datasets: typing.List[typing.Dict[str, Any]]
    ome: typing.Dict[str, Any]


@dataclass
class VzipArchive:
    """An open archive whose arrays retain their reference-backed stores."""

    path: Path
    source: Path
    images: typing.List[VzipImage]
    attributes: typing.Dict[str, Any]

    @property
    def sizes(self) -> typing.Dict[str, int]:
        """Return scene count and common selectable T/C/Z ranges."""
        sizes = {"S": len(self.images)}
        for axis in ("t", "c", "z"):
            sizes[axis.upper()] = min(
                (
                    image.arrays[0].shape[image.axes.index(axis)]
                    if axis in image.axes
                    else 1
                )
                for image in self.images
            )
        return sizes


def open_vzip(path: typing.Union[str, Path]) -> VzipArchive:
    """Open a CZI archive's metadata without fetching image pixels.

    Raises:
        ImportError: Optional dependencies are unavailable.
        ValueError: This is not a supported CZI-derived archive.
        FileNotFoundError: The archive or its local CZI source is missing.
    """
    try:
        import refkv.zarr
        import zarr
    except ImportError as error:
        raise ImportError(INSTALL_HINT) from error

    archive_path = Path(path).expanduser().resolve()
    if not archive_path.is_file():
        raise FileNotFoundError(f"Archive does not exist: {archive_path}")
    root = zarr.open_group(refkv.zarr.open(str(archive_path)), mode="r")
    attributes = dict(root.attrs)
    provenance = attributes.get("refkv_zarrified", {})
    if provenance.get("profile") != "czi":
        raise ValueError("Only CZI-derived refkv VZIP archives are supported.")
    url = provenance.get("source", {}).get("url")
    if not isinstance(url, str) or not url:
        raise ValueError("The archive has no CZI source location.")
    parsed = urlsplit(url)
    if parsed.scheme not in ("", "file"):
        raise ValueError(
            "This reader currently supports local CZI sources only."
        )
    location = parsed.path
    if parsed.netloc and parsed.netloc != "localhost":
        location = f"//{parsed.netloc}{location}"
    source = Path(url2pathname(location))
    if not source.is_absolute():
        source = archive_path.parent / source
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(
            f"Referenced CZI is missing: {source}. Restore it to its original "
            "location; the VZIP does not contain its pixels."
        )
    images = []
    groups = sorted(
        root.groups(),
        key=lambda item: (
            not item[0].isdecimal(),
            int(item[0]) if item[0].isdecimal() else item[0],
        ),
    )
    for name, group in groups:
        ome = dict(group.attrs.get("ome", {}))
        for index, multiscale in enumerate(ome.get("multiscales", [])):
            axes = tuple(axis["name"].lower() for axis in multiscale["axes"])
            datasets = multiscale["datasets"]
            arrays = [group.get_array(dataset["path"]) for dataset in datasets]
            if (
                not arrays
                or len(set(axes)) != len(axes)
                or not {"y", "x"}.issubset(axes)
                or any(array.ndim != len(axes) for array in arrays)
                or any(size < 1 for array in arrays for size in array.shape)
            ):
                raise ValueError(f"Unsupported image axes in series {name}.")
            series_name = name if index == 0 else f"{name}/{index}"
            images.append(VzipImage(series_name, axes, arrays, datasets, ome))
    if not images:
        raise ValueError("The archive contains no OME image series.")
    return VzipArchive(archive_path, source, images, attributes)


def _bounds(
    planes: typing.Dict[str, typing.Tuple[int, int]],
    axis: str,
    size: int,
) -> typing.Tuple[int, int]:
    """Validate an inclusive positional selection for one dimension."""
    low, high = planes.get(axis.upper(), (0, size - 1))
    if not 0 <= low <= high < size:
        raise ValueError(
            f"Invalid {axis.upper()} selection {(low, high)} for size {size}."
        )
    return low, high


def vzip_layers(
    archive: VzipArchive,
    planes: typing.Dict[str, typing.Tuple[int, int]] | None = None,
) -> typing.List[typing.Tuple[Any, typing.Dict[str, Any], str]]:
    """Build lazy layer tuples, slicing by OME axis names rather than positions.

    Scenes remain independent layers, including differently sized scenes.
    Embedded contrast windows avoid napari scanning the complete lazy image.
    """
    import dask.array as da
    from napari.utils.colormaps import Colormap

    planes = planes or {}
    scene_low, scene_high = _bounds(planes, "s", len(archive.images))
    layers = []
    for image in archive.images[scene_low : scene_high + 1]:
        axes = image.axes
        base = image.arrays[0]
        for axis in ("t", "z"):
            if axis not in axes:
                _bounds(planes, axis, 1)
        ranges = {
            axis: _bounds(planes, axis, base.shape[index])
            for index, axis in enumerate(axes)
            if axis not in ("y", "x", "c")
        }
        channel_low, channel_high = _bounds(
            planes,
            "c",
            base.shape[axes.index("c")] if "c" in axes else 1,
        )
        display_axes = tuple(
            axis for axis in axes if axis not in ("c", "y", "x")
        ) + ("y", "x")
        remaining_axes = tuple(axis for axis in axes if axis != "c")
        permutation = tuple(
            remaining_axes.index(axis) for axis in display_axes
        )
        scale = np.ones(base.ndim, dtype=float)
        translate = np.zeros(base.ndim, dtype=float)
        for transform in image.datasets[0].get(
            "coordinateTransformations", []
        ):
            if transform["type"] == "scale":
                factor = np.asarray(transform["scale"])
                scale *= factor
                translate *= factor
            elif transform["type"] == "translation":
                translate += np.asarray(transform["translation"])
        for axis, (low, _) in ranges.items():
            translate[axes.index(axis)] += low * scale[axes.index(axis)]
        channels = image.ome.get("omero", {}).get("channels", [])
        fallback = (
            (float(np.iinfo(base.dtype).min), float(np.iinfo(base.dtype).max))
            if np.issubdtype(base.dtype, np.integer)
            else (0.0, 1.0)
        )
        for channel_index in range(channel_low, channel_high + 1):
            levels = []
            for array in image.arrays:
                selection = []
                for index, axis in enumerate(axes):
                    if axis == "c":
                        if array.shape[index] != base.shape[index]:
                            raise ValueError(
                                "Channel counts differ across pyramid levels."
                            )
                        selection.append(channel_index)
                    elif axis in ranges:
                        low, high = ranges[axis]
                        ratio = array.shape[index] / base.shape[index]
                        selection.append(
                            slice(
                                int(np.floor(low * ratio)),
                                int(np.ceil((high + 1) * ratio)),
                            )
                        )
                    else:
                        selection.append(slice(None))
                levels.append(
                    da.from_zarr(array)[tuple(selection)].transpose(
                        permutation
                    )
                )
            channel = (
                channels[channel_index]
                if channel_index < len(channels)
                else {}
            )
            window = channel.get("window", {})
            limits = (
                window.get("start", fallback[0]),
                window.get("end", fallback[1]),
            )
            if not np.all(np.isfinite(limits)) or limits[0] >= limits[1]:
                limits = fallback
            color = channel.get("color", "FFFFFF")
            colormap = "gray"
            if isinstance(color, str) and len(color) == 6:
                try:
                    rgb = [
                        int(color[start : start + 2], 16) / 255
                        for start in (0, 2, 4)
                    ]
                    colormap = Colormap([[0, 0, 0], rgb], name=f"vzip_{color}")
                except ValueError:
                    pass
            label = channel.get("label", f"Channel {channel_index}")
            kwargs = {
                "name": f"{archive.path.stem} | {image.name} | {label}",
                "axis_labels": display_axes,
                "scale": tuple(
                    scale[axes.index(axis)] for axis in display_axes
                ),
                "translate": tuple(
                    translate[axes.index(axis)] for axis in display_axes
                ),
                "contrast_limits": limits,
                "colormap": colormap,
                "blending": "additive",
                "multiscale": len(levels) > 1,
                "rgb": False,
                "metadata": {
                    "vzip": str(archive.path),
                    "czi_source": str(archive.source),
                    "series": image.name,
                    "ome": image.ome,
                },
            }
            layers.append(
                (levels if len(levels) > 1 else levels[0], kwargs, "image")
            )
    return layers


def read_vzip(
    path: typing.Union[str, typing.List[str]],
    planes: typing.Dict[str, typing.Tuple[int, int]] | None = None,
) -> typing.List[typing.Tuple[Any, typing.Dict[str, Any], str]]:
    """Read one or more CZI VZIPs through napari's layer-tuple protocol."""
    paths = path if isinstance(path, list) else [path]
    return [
        layer
        for item in paths
        for layer in vzip_layers(open_vzip(item), planes)
    ]


def prepare_vzip(
    source_path: typing.Union[str, Path],
    output_path: typing.Union[str, Path],
    rebuild: bool,
    planes: typing.Dict[str, typing.Tuple[int, int]],
) -> typing.Tuple[
    VzipArchive, typing.List[typing.Tuple[Any, typing.Dict[str, Any], str]]
]:
    """Create or reuse an archive and prepare layers in a background worker.

    Reuse never rewrites an archive. An existing archive must refer to the
    selected CZI, rather than silently displaying another source's pixels.
    """
    source = Path(source_path).resolve()
    destination = Path(output_path).expanduser().absolute()
    if source.suffix.lower() == ".czi":
        if rebuild or not destination.exists():
            try:
                from czitools.export_tools import create_czi_vzip
            except ImportError as error:
                raise ImportError(
                    "Archive creation requires a czitools build with "
                    'create_czi_vzip. Upgrade with pip install -U "czitools[vzip]".'
                ) from error
            create_czi_vzip(source, destination, overwrite=rebuild)
        archive = open_vzip(destination)
        if archive.source != source:
            raise ValueError(
                f"The archive references {archive.source}, not {source}. "
                "Choose Rebuild or a different destination."
            )
    else:
        archive = open_vzip(source)
    return archive, vzip_layers(archive, planes)
