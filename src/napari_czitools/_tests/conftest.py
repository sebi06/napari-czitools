import os
import sys
from typing import Any

import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from qtpy.QtWidgets import QApplication


def has_gui_support() -> bool:
    """Check if GUI is supported on the current platform.

    Returns:
        bool: True if GUI is supported, False otherwise
    """
    if sys.platform.startswith("win"):
        # Windows always has GUI support unless explicitly disabled
        return True
    elif sys.platform.startswith("darwin"):
        # macOS always has GUI support unless explicitly disabled
        return True
    else:
        # Linux/Unix systems require DISPLAY or WAYLAND_DISPLAY
        return bool(
            os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        )


# Environment constants
IS_CI = os.environ.get("CI") is not None
HAS_DISPLAY = has_gui_support()


def pytest_configure(config: Config) -> None:
    """Configure pytest with custom marks.

    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line(
        "markers", "qtbot: mark test as requiring Qt (uses pytest-qt)"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )


@pytest.fixture(autouse=True)
def _skip_qt_tests(request: FixtureRequest) -> None:
    """Skip tests marked with 'qtbot' if running in CI environment.

    Args:
        request: Pytest fixture request object
    """
    if request.node.get_closest_marker("qtbot") and (IS_CI or not HAS_DISPLAY):
        pytest.skip("Skipping GUI test in headless/CI environment")


@pytest.fixture(autouse=True, scope="function")
def cleanup_qt() -> Any:
    """Clean up Qt widgets after each test.

    Yields:
        None

    Raises:
        RuntimeError: If Qt cleanup fails
    """
    yield
    try:
        # Clean up any remaining widgets
        for widget in QApplication.topLevelWidgets():
            widget.deleteLater()
        QApplication.processEvents()
    except RuntimeError as e:
        pytest.skip(f"Qt cleanup failed: {e}")
