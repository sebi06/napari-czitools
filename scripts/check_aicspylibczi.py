import argparse
from pathlib import Path

from aicspylibczi import CziFile

DEFAULT_SAMPLE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "napari_czitools"
    / "sample_data"
    / "CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read CZI subblock metadata with aicspylibczi.")
    parser.add_argument(
        "czi_path",
        nargs="?",
        type=Path,
        default=DEFAULT_SAMPLE,
        help="CZI file to inspect (defaults to a bundled sample).",
    )
    file_path = parser.parse_args().czi_path

    print(f"Attempting to read: {file_path}")
    try:
        czi = CziFile(file_path)
        print("File opened. Reading metadata...")
        print("Reading subblock metadata...")
        print(f"Dimensions: {czi.dims}")
    except Exception as exc:
        print(f"Python captured error: {exc}")

    print("Test finished without hard crash.")


if __name__ == "__main__":
    main()
