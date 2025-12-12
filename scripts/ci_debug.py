"""CI debug helper for napari-czitools

Prints environment variables and package versions helpful when debugging CI issues
such as the Linux threading deadlock involving CZI reading and progress bars.
"""

import os
import sys
import platform
import importlib
from textwrap import indent


def print_heading(title):
    print("=" * 80)
    print(title)
    print("=" * 80)


def getenv(keys):
    out = []
    for k in keys:
        out.append(f"{k}={os.environ.get(k)!r}")
    return "\n".join(out)


def print_env():
    keys = [
        "CI",
        "GITHUB_ACTIONS",
        "RUNNER_OS",
        "GITHUB_RUN_ID",
        "GITHUB_REPOSITORY",
        "QT_QPA_PLATFORM",
        "DISPLAY",
        "TQDM_DISABLE",
        "OMP_NUM_THREADS",
        "NUMBA_NUM_THREADS",
        "MKL_NUM_THREADS",
        "PYTHONUNBUFFERED",
    ]
    print_heading("Environment Variables")
    print(getenv(keys))


def print_platform():
    print_heading("Platform")
    print(f"Python: {platform.python_version()} ({sys.version})")
    print(f"Platform: {platform.platform()}")
    print(f"Implementation: {platform.python_implementation()}")


def version_of(module_name):
    try:
        m = importlib.import_module(module_name)
        return getattr(m, "__version__", str(m))
    except Exception as e:
        return f"not installed ({e})"


def print_packages():
    packages = [
        "pip",
        "setuptools",
        "wheel",
        "numpy",
        "czitools",
        "pylibczirw",
        "tqdm",
        "numba",
        "pyqt5",
        "pyqt6",
        "qtpy",
        "napari",
        "pyqtgraph",
    ]
    print_heading("Package Versions")
    for pkg in packages:
        print(f"{pkg}: {version_of(pkg)}")


def print_path():
    print_heading("Python Path")
    print("\n".join(sys.path))


def main():
    print("CI debug info for napari-czitools")
    print_platform()
    print_env()
    print_packages()
    print_path()


if __name__ == "__main__":
    main()
