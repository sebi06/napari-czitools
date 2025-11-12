from pathlib import Path

import pytest

from napari_czitools import napari_get_reader


@pytest.fixture
def sample_czi_path():
    """Fixture to provide sample CZI file path."""
    return Path("src/napari_czitools/sample_data/CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi")


@pytest.fixture
def sample_czi_path_large():
    """Fixture to provide a larger sample CZI file path."""
    return Path("src/napari_czitools/sample_data/CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi")


# @pytest.mark.skip(
#     reason="This test is temporarily disabled. It does not work robustly yet."
# )
@pytest.mark.qtbot
def test_reader(tmp_path, qtbot, sample_czi_path, cleanup_qt):
    """Test the napari_get_reader plugin function."""
    # Get the reader function
    reader = napari_get_reader(str(sample_czi_path))
    assert callable(reader)

    # Test that reader is returned for CZI files
    assert napari_get_reader("test.czi") is not None

    # Test that non-CZI files return None
    assert napari_get_reader("fake.file") is None

    # Note: We avoid calling reader(str(sample_czi_path)) here because it creates
    # napari viewers which cause Qt cleanup issues in test suite


@pytest.mark.qtbot
def test_reader_non_czi_files(cleanup_qt):
    """Test that non-CZI files return None."""
    test_files = [
        "test.jpg",
        "test.png",
        "test.tiff",
        "test.txt",
        "test.pdf",
        "test.docx",
        "",
        "file_without_extension",
    ]

    for test_file in test_files:
        reader = napari_get_reader(test_file)
        assert reader is None, f"Reader should return None for {test_file}"


@pytest.mark.qtbot
def test_reader_with_file_list(sample_czi_path, cleanup_qt):
    """Test reader with a list of files (should use first file)."""
    file_list = [str(sample_czi_path), "fake.czi", "another.czi"]

    reader = napari_get_reader(file_list)
    if sample_czi_path.exists():
        assert callable(reader)
    else:
        # If file doesn't exist, should still return a reader for .czi extension
        assert callable(reader)


@pytest.mark.qtbot
def test_reader_nonexistent_czi_file(cleanup_qt):
    """Test reader with non-existent CZI file."""
    nonexistent_file = "nonexistent_file.czi"
    reader = napari_get_reader(nonexistent_file)

    # Should return a reader function for .czi files even if they don't exist
    assert callable(reader)


@pytest.mark.qtbot
def test_reader_empty_string(cleanup_qt):
    """Test reader with empty string."""
    reader = napari_get_reader("")
    assert reader is None


@pytest.mark.qtbot
def test_reader_case_sensitivity(sample_czi_path, cleanup_qt):
    """Test reader with different case extensions."""
    if sample_czi_path.exists():
        # Test different cases
        base_path = str(sample_czi_path).replace(".czi", "")

        # These should return a reader
        assert callable(napari_get_reader(base_path + ".czi"))

        # These should not return a reader (case sensitive)
        assert napari_get_reader(base_path + ".CZI") is None
        assert napari_get_reader(base_path + ".Czi") is None
        assert napari_get_reader(base_path + ".czI") is None
