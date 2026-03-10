"""Test URL metadata reading functionality for CZI files."""

import time

import pytest
from czitools.metadata_tools.boundingbox import CziBoundingBox
from czitools.metadata_tools.czi_metadata import CziMetadata


def _create_url_metadata_with_retry(url: str, retries: int = 3, delay_seconds: float = 1.0) -> CziMetadata:
    """Create URL metadata with retry and skip on transient network errors."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return CziMetadata(url)
        except RuntimeError as exc:
            # czitools can raise a RuntimeError for transient header reads.
            if "FileHeaderSegment" in str(exc):
                last_error = exc
            else:
                raise
        except OSError as exc:
            # Network/file retrieval failures should not fail local CI runs.
            last_error = exc

        if attempt < retries:
            time.sleep(delay_seconds)

    pytest.skip("Skipping URL metadata test due to transient remote read failure: " f"{last_error}")


class TestUrlMetadata:
    """Test class for URL-based CZI metadata operations."""

    @pytest.fixture(scope="class")
    def sample_url(self):
        """GitHub raw URL for a sample CZI file."""
        return "https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi"

    @pytest.fixture(scope="class")
    def sample_metadata(self, sample_url):
        """Create sample URL metadata once to minimize network flakiness."""
        return _create_url_metadata_with_retry(sample_url)

    def test_url_metadata_creation(self, sample_metadata):
        """Test that CziMetadata can be created from a URL."""
        mdata = sample_metadata

        # Verify metadata object was created successfully
        assert mdata is not None
        assert isinstance(mdata, CziMetadata)

    def test_url_metadata_has_bbox(self, sample_metadata):
        """Test that metadata from URL contains bounding box information."""
        mdata = sample_metadata

        # Verify bounding box exists and is correct type
        assert hasattr(mdata, "bbox")
        assert mdata.bbox is not None
        assert isinstance(mdata.bbox, CziBoundingBox)

    def test_url_metadata_total_bounding_box(self, sample_metadata):
        """Test that total_bounding_box is accessible and properly formatted."""
        mdata = sample_metadata

        # Verify total_bounding_box exists and is a dictionary
        assert mdata.bbox.total_bounding_box is not None
        assert isinstance(mdata.bbox.total_bounding_box, dict)

        # Verify it contains expected dimensions
        bbox = mdata.bbox.total_bounding_box
        expected_dimensions = ["T", "Z", "C", "X", "Y"]

        for dim in expected_dimensions:
            assert dim in bbox, f"Dimension '{dim}' not found in bounding box"
            assert isinstance(bbox[dim], tuple), f"Dimension '{dim}' should be a tuple"
            assert len(bbox[dim]) == 2, f"Dimension '{dim}' should have 2 values (min, max)"

    def test_url_metadata_specific_dimensions(self, sample_metadata):
        """Test specific dimension values match expected sample data."""
        mdata = sample_metadata
        bbox = mdata.bbox.total_bounding_box

        # Test specific dimensions based on filename expectations
        # CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi
        assert bbox["T"][1] == 3, f"Expected T dimension max of 3, got {bbox['T'][1]}"
        assert bbox["Z"][1] == 6, f"Expected Z dimension max of 6, got {bbox['Z'][1]}"
        assert bbox["C"][1] == 1, f"Expected C dimension max of 1, got {bbox['C'][1]}"
        assert bbox["X"][1] == 300, f"Expected X dimension max of 300, got {bbox['X'][1]}"
        assert bbox["Y"][1] == 200, f"Expected Y dimension max of 200, got {bbox['Y'][1]}"

    def test_url_metadata_dimension_access(self, sample_metadata):
        """Test that individual dimensions can be accessed without errors."""
        mdata = sample_metadata
        bbox = mdata.bbox.total_bounding_box

        # Test accessing each dimension
        for dim in ["T", "Z", "C", "X", "Y"]:
            assert dim in bbox
            min_val, max_val = bbox[dim]
            assert isinstance(min_val, int)
            assert isinstance(max_val, int)
            assert min_val >= 0
            assert max_val > min_val

    @pytest.mark.network
    def test_url_metadata_network_dependency(self, sample_metadata):
        """Test marked as requiring network access."""
        # This test is marked with @pytest.mark.network
        # It can be skipped in environments without network access
        # using: pytest -m "not network"
        mdata = sample_metadata
        assert mdata is not None

    # TODO: Adapt CziMetadata error handling
    # def test_url_metadata_error_handling(self):
    #     """Test that invalid URLs are handled gracefully."""
    #     invalid_url = "https://github.com/invalid/nonexistent/file.czi"

    #     # This should raise an appropriate exception
    #     with pytest.raises((OSError, FileNotFoundError, ValueError)):
    #         CziMetadata(invalid_url)


class TestUrlMetadataIntegration:
    """Integration tests for URL metadata with napari-czitools functionality."""

    def test_url_metadata_consistent_with_local_file(self):
        """Test that URL metadata is consistent with local file metadata (if available)."""
        # This test could compare URL vs local file metadata if both are available
        # For now, we'll just verify the URL version works
        url = "https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi"

        mdata = _create_url_metadata_with_retry(url)
        bbox = mdata.bbox.total_bounding_box

        # Verify basic structure is consistent
        assert isinstance(bbox, dict)
        assert len(bbox) >= 5  # At least T, Z, C, X, Y

        for _dim, (min_val, max_val) in bbox.items():
            assert min_val >= 0
            assert max_val > min_val


if __name__ == "__main__":
    # Allow running the test directly for development
    import sys

    # Simple test runner for development
    print("Running URL metadata tests...")

    url = "https://github.com/sebi06/napari-czitools/raw/main/src/napari_czitools/sample_data/CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi"

    try:
        print("Creating CziMetadata from URL...")
        mdata = CziMetadata(url)
        print("✓ Metadata created successfully")

        print("Checking bounding box...")
        assert hasattr(mdata, "bbox")
        print(f"✓ Has bbox: {type(mdata.bbox)}")

        print("Checking total_bounding_box...")
        bbox = mdata.bbox.total_bounding_box
        print(f"✓ total_bounding_box: {bbox}")

        print("Testing dimension access...")
        for dim in ["T", "Z", "C", "X", "Y"]:
            if dim in bbox:
                print(f"✓ {dim}: {bbox[dim]}")
            else:
                print(f"✗ {dim}: not found")

        print("\n🎉 All basic tests passed!")

    except (OSError, FileNotFoundError, ValueError) as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
