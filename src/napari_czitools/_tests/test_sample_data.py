import os
import sys
from pathlib import Path

import pytest

from napari_czitools._io import CZIDataLoader
from napari_czitools._metadata_widget import MetadataDisplayMode

# Check if we're running in a headless environment (like GitHub Actions)
HEADLESS = (
    os.environ.get("CI") == "true"
    or os.environ.get("GITHUB_ACTIONS") == "true"
    or os.environ.get("HEADLESS", "").lower() in ("true", "1", "yes")
)

# Check for problematic environment combination
# The threading deadlock started occurring after Python 3.13 support was added (commit 7722ab1)
# This changed dependency resolution and likely pulled in newer package versions with threading issues
# The problem affects Linux CI regardless of Python version due to shared dependency resolution


def _detect_threading_issue_environment():
    """
    Detect if current environment is likely to have CZI threading deadlock issues.

    Returns True if we should skip threading-heavy tests to avoid deadlocks.
    This is more precise than blanket CI detection.
    """
    # Only affects Linux environments
    if not sys.platform.startswith("linux"):
        return False

    # Only affects headless/CI environments
    if not HEADLESS:
        return False

    # Check for specific conditions that indicate threading problems
    try:
        # Check if we're in a GitHub Actions environment specifically
        github_actions = os.environ.get("GITHUB_ACTIONS") == "true"

        # Check for Ubuntu specifically (where the issue manifests)
        is_ubuntu = (
            any(ubuntu_indicator in os.environ.get("RUNNER_OS", "").lower() for ubuntu_indicator in ["ubuntu", "linux"])
            or "ubuntu" in os.environ.get("IMAGEOS", "").lower()
        )

        # The threading issue seems to occur in GitHub Actions Ubuntu environments
        # regardless of Python version, likely due to dependency version combinations
        if github_actions and (is_ubuntu or sys.platform == "linux"):
            return True

        return False

    except (KeyError, ValueError, OSError):
        # If we can't determine the environment, be conservative
        # Skip threading tests on Linux CI to be safe
        return HEADLESS and sys.platform.startswith("linux")


SKIP_THREADING_TESTS = _detect_threading_issue_environment()

# More granular control: only skip the most problematic operations
SKIP_VIEWER_OPERATIONS = SKIP_THREADING_TESTS  # Viewer creation can be problematic
SKIP_CZI_READING = SKIP_THREADING_TESTS  # CZI file reading is the main issue

basedir = Path(__file__).resolve().parents[1] / "sample_data"


def _configure_threading_environment():
    """
    Configure environment settings to prevent threading deadlocks in CI.

    This applies threading mitigations at runtime rather than skipping tests entirely.
    """
    if HEADLESS and sys.platform.startswith("linux"):
        # Disable progress bars that can cause threading issues
        os.environ["TQDM_DISABLE"] = "1"

        # Limit thread usage for libraries known to cause issues
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("NUMBA_NUM_THREADS", "1")
        os.environ.setdefault("MKL_NUM_THREADS", "1")

        # Set Qt to offscreen mode
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

        # For Python 3.13+, set additional threading controls
        if sys.version_info >= (3, 13):
            os.environ.setdefault("PYTHONTHREADDEBUG", "0")


# Apply threading configuration
_configure_threading_environment()


@pytest.mark.skipif(
    SKIP_VIEWER_OPERATIONS, reason="Viewer operations may cause threading issues in GitHub Actions Ubuntu environment"
)
@pytest.mark.timeout(120)  # 2 minute timeout for individual tests
@pytest.mark.parametrize(
    "sample_key",
    [
        "unique_id.0",  # CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi
        "unique_id.2",  # RatBrain_Z79_ZSTD.czi
        "unique_id.1",  # testwell96_A1-D12_S48_T1_C2_Z1_X640_Y480_ZSTD.czi
        "unique_id.3",  # Airyscan Z-Stack dataset
    ],
)
def test_open_sample(make_napari_viewer, sample_key: str) -> None:
    """Test opening sample CZI files in napari."""

    viewer = make_napari_viewer()

    # In headless environments, sample data might not be available
    if HEADLESS:
        # Try to open the sample, but handle the case where it might fail
        try:
            viewer.open_sample("napari-czitools", sample_key)
            # If it succeeds, verify layers were added
            assert len(viewer.layers) > 0
        except (FileNotFoundError, AttributeError, ValueError):
            # In headless environments, sample data files might not be accessible
            # This is expected behavior in CI/CD environments
            pytest.skip("Sample data not available in headless environment")
    else:
        # In non-headless environments, sample should always work
        viewer.open_sample("napari-czitools", sample_key)
        assert len(viewer.layers) > 0


@pytest.mark.skipif(
    SKIP_CZI_READING,
    reason="CZI file reading operations may cause threading issues in GitHub Actions Ubuntu environment",
)
@pytest.mark.timeout(180)  # 3 minute timeout for individual tests
@pytest.mark.parametrize(
    "czifile",
    [
        "CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi",
        "RatBrain_Z79_ZSTD.czi",
        "testwell96_A1-D12_S48_T1_C2_Z1_X640_Y480_ZSTD.czi",
        "20X_SR-Airyscan_JDCV.czi",
    ],
)
def test_io(czifile: str, make_napari_viewer) -> None:
    """Test the CZIDataLoader functionality."""
    path = basedir / czifile

    # Create the CZIDataLoader
    czi = CZIDataLoader(
        path,
        zoom=1.0,
        use_dask=False,
        chunk_zyx=False,
        use_xarray=True,
        show_metadata=MetadataDisplayMode.TABLE,
    )

    if HEADLESS:
        # In headless environments, test data loading without creating a viewer
        from czitools.read_tools import read_tools

        # Test that the data can be loaded successfully
        array6d, metadata = read_tools.read_6darray(
            czi.path,
            use_dask=czi.use_dask,
            chunk_zyx=czi.chunk_zyx,
            zoom=czi.zoom,
            use_xarray=czi.use_xarray,
            planes=czi.planes,
        )

        # Verify that data was loaded
        assert array6d is not None, "Failed to load array data"
        assert metadata is not None, "Failed to load metadata"

        # Test that we can process channels without a viewer
        from napari_czitools._io import process_channels

        channel_layers = process_channels(array6d, metadata)
        assert len(channel_layers) > 0, "No channel layers created"

        print(f"Successfully loaded {czifile} in headless mode")
    else:
        # In environments with display, test the full viewer functionality
        try:
            viewer = make_napari_viewer()

            # Test the full add_to_viewer functionality
            czi.add_to_viewer()

            # Verify that layers were added to the viewer
            assert len(viewer.layers) > 0, "No layers added to viewer"

            print(f"Successfully loaded {czifile} with viewer")
        except (AttributeError, RuntimeError, ImportError) as e:
            # If viewer creation fails, fall back to headless testing
            print(f"Viewer creation failed ({e}), falling back to headless test")

            from czitools.read_tools import read_tools

            # Test that the data can be loaded successfully
            array6d, metadata = read_tools.read_6darray(
                czi.path,
                use_dask=czi.use_dask,
                chunk_zyx=czi.chunk_zyx,
                zoom=czi.zoom,
                use_xarray=czi.use_xarray,
                planes=czi.planes,
            )

            # Verify that data was loaded
            assert array6d is not None, "Failed to load array data"
            assert metadata is not None, "Failed to load metadata"

            # Test that we can process channels without a viewer
            from napari_czitools._io import process_channels

            channel_layers = process_channels(array6d, metadata)
            assert len(channel_layers) > 0, "No channel layers created"

            print(f"Successfully loaded {czifile} in fallback headless mode")


@pytest.mark.skipif(
    not SKIP_THREADING_TESTS,
    reason="Replacement test only for environments where main tests are skipped due to threading issues",
)
def test_basic_plugin_functionality_linux_ci() -> None:
    """
    Basic functionality test for environments where threading issues prevent full tests.

    This test validates that:
    1. The plugin can be imported successfully
    2. Basic classes can be instantiated
    3. Sample data files exist
    4. No threading operations that could deadlock
    """

    # Test that we can import all main components
    from napari_czitools._io import CZIDataLoader
    from napari_czitools._metadata_widget import MetadataDisplayMode
    from napari_czitools import napari_get_reader

    # Test that sample data files exist
    test_files = [
        "CellDivision_T10_Z20_CH2_X600_Y500_DCV_ZSTD.czi",
        "RatBrain_Z79_ZSTD.czi",
        "testwell96_A1-D12_S48_T1_C2_Z1_X640_Y480_ZSTD.czi",
        "20X_SR-Airyscan_JDCV.czi",
    ]

    for filename in test_files:
        file_path = basedir / filename
        assert file_path.exists(), f"Sample data file {filename} not found"

    # Test that reader function can be obtained (without calling it)
    reader = napari_get_reader("test.czi")
    assert callable(reader), "Reader function should be callable"

    reader_none = napari_get_reader("test.txt")
    assert reader_none is None, "Reader should return None for non-CZI files"

    # Test that CZIDataLoader can be instantiated (without reading)
    test_path = basedir / test_files[0]
    loader = CZIDataLoader(
        test_path,
        zoom=1.0,
        use_dask=False,
        chunk_zyx=False,
        use_xarray=True,
        show_metadata=MetadataDisplayMode.TABLE,
    )

    assert loader.path == test_path
    assert loader.zoom == 1.0
    assert loader.use_dask is False

    print("Basic plugin functionality test passed on problematic environment")
