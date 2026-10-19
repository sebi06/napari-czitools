# extract_metadata.py
import argparse
import json
import sys
from pathlib import Path

from czitools.metadata_tools import czi_metadata as czimd


def get_meta(path):
    try:
        md = czimd.CziMetadata(path)
        data = {
            "zx_sf": md.scale.ratio.get("zx_sf", 1.0),
            "names": md.channelinfo.names,
            "colors": md.channelinfo.colors,
            "clims": md.channelinfo.clims,
            "maxvalue": md.image.SizeX,
            "maxvalue_list": md.maxvalue_list,
            "red_dict": czimd.create_md_dict_red(md, sort=True, remove_none=True),
            "nested_dict": czimd.create_md_dict_nested(md, sort=True, remove_none=True),
        }

        print(json.dumps(data, default=str))

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    default_sample = Path(__file__).resolve().parent / "sample_data" / "CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi"
    parser = argparse.ArgumentParser(description="Print CZI metadata as JSON.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=default_sample,
        help="CZI file to inspect (defaults to a bundled sample).",
    )
    get_meta(parser.parse_args().path)
