"""Open the bundled CellDivision CZI sample with napari-czitools."""

from pathlib import Path

import napari

from napari_czitools._reader import reader_function_adv

# adapt to you needs
SAMPLE_CZI_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "napari_czitools"
    / "sample_data"
    / "CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi"
)


def main() -> None:
    """Open the bundled CZI sample in napari."""
    if not SAMPLE_CZI_PATH.is_file():
        raise FileNotFoundError(f"Bundled CZI sample was not found: {SAMPLE_CZI_PATH}")

    # The reader function accepts `planes`; viewer.open forwards extra kwargs
    # to layer creation instead of to the reader.
    planes = {
        "S": (0, 0),
        "T": (0, 2),
        "C": (1, 1),
        "Z": (4, 8),
    }
    reader_function_adv(
        str(SAMPLE_CZI_PATH),
        planes=planes,
    )

    # start the napari event loop
    napari.run()


if __name__ == "__main__":
    main()
