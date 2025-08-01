import os
from unittest.mock import MagicMock, patch

import pytest

from napari_czitools._utilities import check_filepath

TESTDATA_BASE_PATH = "src/napari_czitools/sample_data"
GITHUB_BASE_URL = r"https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/"


@pytest.fixture
def mock_logger():
    with patch("napari_czitools._utilities.logger") as mock_logger:
        yield mock_logger


def test_check_filepath_local_file_exists(mock_logger):
    filepath = "test_file.txt"
    local_path = os.path.join(TESTDATA_BASE_PATH, filepath)

    with patch("os.path.exists", return_value=True):
        result = check_filepath(filepath)

    assert result == local_path
    mock_logger.info.assert_called_once_with(f"File: {local_path} exists. Start reading pixel data ...")


def test_check_filepath_file_not_local_but_valid_url(mock_logger):
    filepath = "test_file.txt"
    github_url = os.path.join(GITHUB_BASE_URL, filepath)

    with patch("os.path.exists", return_value=False), patch("validators.url", return_value=True):
        result = check_filepath(filepath)

    assert result == github_url
    mock_logger.warning.assert_called_once_with("File does not exist locally. Trying to read from repo.")


def test_check_filepath_invalid_url(mock_logger):
    filepath = "test_file.txt"
    github_url = os.path.join(GITHUB_BASE_URL, filepath)

    with patch("os.path.exists", return_value=False), patch("validators.url", return_value=False):
        result = check_filepath(filepath)

    assert result is None
    mock_logger.error.assert_called_once_with(f"Invalid link: {github_url}")
