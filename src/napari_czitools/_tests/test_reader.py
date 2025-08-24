from pathlib import Path

import numpy as np
import pytest

from napari_czitools import napari_get_reader


@pytest.fixture
def sample_czi_path():
    """Fixture to provide sample CZI file path."""
    return Path(
        "src/napari_czitools/sample_data/CellDivision_T3_Z6_CH1_X300_Y200_DCV_ZSTD.czi"
    )


@pytest.mark.skip(
    reason="This test is temporarily disabled. It does not work robustly yet."
)
@pytest.mark.qtbot
def test_reader(tmp_path, qtbot, sample_czi_path, cleanup_qt):
    """Test the napari_get_reader plugin function."""
    try:
        # Get the reader function
        reader = napari_get_reader(str(sample_czi_path))
        assert callable(reader)

        if sample_czi_path.exists():
            layer_data_list = reader(str(sample_czi_path))
            assert isinstance(layer_data_list, list)
            assert len(layer_data_list) > 0

            layer_data = layer_data_list[0]
            assert isinstance(layer_data, tuple)

            data = layer_data[0]
            if data is not None:
                assert isinstance(data, np.ndarray)
                assert data.ndim >= 2

        assert napari_get_reader("fake.file") is None

    finally:
        # Ensure all Qt events are processed and widgets are cleaned up
        qtbot.wait(200)

        # Force cleanup of any remaining widgets
        for widget in qtbot.app.topLevelWidgets():
            widget.deleteLater()
        qtbot.wait(500)
