import os

import validators
from czitools.utils import logging_tools

logger = logging_tools.set_logging()

GITHUB_BASE_URL = r"https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/"
# GITHUB_BASE_URL = r"https://github.com/sebi06/napari-czitools/blob/main/src/napari_czitools/sample_data/"
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
