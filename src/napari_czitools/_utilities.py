import os
from typing import Any
from urllib.parse import urlparse

import validators
from czitools.utils import logging_tools

logger = logging_tools.set_logging()

GITHUB_BASE_URL = r"https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/"
TESTDATA_BASE_PATH = "src/napari_czitools/sample_data"


def check_filepath(filepath: str) -> str | None:
    """
    Verify the existence of a file locally or in the GitHub repository.

    This function first checks if the specified file exists in the local
    filesystem under the predefined `TESTDATA_BASE_PATH`. If the file is
    found locally, it logs an informational message and returns the local
    file path. If the file does not exist locally, it constructs a URL
    pointing to the file in the GitHub repository and validates the URL.
    If the URL is valid, it returns the constructed URL. Otherwise, it logs
    an error message and returns None.

    Args:
        filepath (str): The relative path to the file to check.

    Returns:
        str | None: The local file path if the file exists locally, the
        GitHub URL if the file exists in the repository, or None if the
        file cannot be found.
    """
    filepath_to_read = os.path.join(TESTDATA_BASE_PATH, filepath)

    if os.path.exists(filepath_to_read):
        logger.info(f"File: {filepath_to_read} exists. Start reading pixel data ...")  # noqa: G004

        return filepath_to_read

    else:
        logger.warning("File does not exist locally. Trying to read from repo.")
        filepath_to_read = os.path.join(GITHUB_BASE_URL, filepath)

        if validators.url(filepath_to_read):
            return filepath_to_read  # noqa: G004
        else:
            logger.error(f"Invalid link: {filepath_to_read}")  # noqa: G004
            return None


def extract_base_path_and_filename(url):
    # Parse the URL into components
    parsed_url = urlparse(url)

    # Extract the directory part of the path
    base_path = os.path.dirname(parsed_url.path) + "/"

    # Extract the filename from the path
    filename = os.path.basename(parsed_url.path)

    # Reconstruct the full base URL
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{base_path}"

    return base_url, filename


def _convert_numpy_types(obj: Any) -> Any:
    """
    Recursively convert numpy types to native Python types.

    This function handles numpy scalars, arrays, dictionaries, lists, and tuples.
    It converts numpy scalars to their native Python equivalents, numpy arrays
    to Python lists, and recursively processes dictionaries, lists, and tuples.

    Args:
        obj (Any): The object to convert. Can be a numpy scalar, numpy array,
                   dictionary, list, tuple, or any other type.

    Returns:
        Any: The converted object with numpy types replaced by native Python types.
    """
    if hasattr(obj, "dtype"):  # numpy scalar or array
        if obj.ndim == 0:  # scalar
            return obj.item()  # Convert to native Python type
        else:
            return obj.tolist()  # Convert array to list
    elif isinstance(obj, dict):
        return {key: _convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list | tuple):
        return type(obj)(_convert_numpy_types(item) for item in obj)
    else:
        return obj
