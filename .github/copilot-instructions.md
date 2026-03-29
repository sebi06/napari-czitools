# Copilot Instructions for napari-czitools

This file provides comprehensive guidance for GitHub Copilot and human contributors working on the napari-czitools repository. It explains repository layout, development and testing workflows, CI quirks (notably the Linux CI threading deadlock introduced when Python 3.13 was added), debugging tips, and release procedures.

## Repository Overview

- Project: napari-czitools
- Language: Python
- Packaging: pyproject.toml (PEP 621)
- Tests: pytest, configured via tox.ini and GitHub Actions workflow .github/workflows/test_and_deploy_pypi.yml

### Top-level layout (key files):

- pyproject.toml - project metadata and dependencies
- tox.ini - test matrix configuration used locally and by CI
- README.md - user-facing documentation
- src/napari_czitools - package source
- src/napari_czitools/_tests - test suite
- .github/workflows/test_and_deploy_pypi.yml - CI workflow used to run tests and deploy

## Python Coding Conventions

## Napari-specific instruction

- Please follow napari's guidelines and instruction: [Napari](https://github.com/napari) when writing code for this project.
- Also check this plugin developer guide: [Napari Plugin Developers](https://napari.org/stable/plugins/index.html#plugin-developers)

### Python Instructions

- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following PEP 257 conventions.
- Use the `typing` module for type annotations (e.g., `List[str]`, `Dict[str, int]`).
- Break down complex functions into smaller, more manageable functions.

### General Instructions

- Always prioritize readability and clarity.
- For algorithm-related code, include explanations of the approach used.
- Write code with good maintainability practices, including comments on why certain design decisions were made.
- Handle edge cases and write clear exception handling.
- For libraries or external dependencies, mention their usage and purpose in comments.
- Use consistent naming conventions and follow language-specific best practices.
- Write concise, efficient, and idiomatic code that is also easily understandable.

### Code Style and Formatting

- Follow the **PEP 8** style guide for Python.
- Maintain proper indentation (use 4 spaces for each level of indentation).
- Ensure lines do not exceed 79 characters.
- Place function and class docstrings immediately after the `def` or `class` keyword.
- Use blank lines to separate functions, classes, and code blocks where appropriate.

### Edge Cases and Testing

- Always include test cases for critical paths of the application.
- Account for common edge cases like empty inputs, invalid data types, and large datasets.
- Include comments for edge cases and the expected behavior in those cases.
- Write unit tests for functions and document them with docstrings explaining the test cases.

### Example of Proper Documentation

```python
def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle given the radius.

    Parameters:
    radius (float): The radius of the circle.

    Returns:
    float: The area of the circle, calculated as π * radius^2.
    """
    import math
    return math.pi * radius ** 2
```

## Development Setup

### Prerequisites:

- Python 3.10+ (3.13 supported)
- pip and virtualenv or a modern Python environment manager

### Quick start (recommended):

1. Create and activate a virtual environment:
   On Windows PowerShell:
       python -m venv .venv
       .\.venv\\Scripts\\Activate.ps1
   On POSIX shells:
       python -m venv .venv
       source .venv/bin/activate

2. Upgrade pip and install testing extras:
       python -m pip install --upgrade pip
       pip install -e '.[testing]'

Run the test suite (local):

1. Run pytest directly:
       pytest -v

2. Or run a tox environment (matrix of envs):
       python -m tox -e py312-linux

## Notes about headless GUI tests:

- The test matrix runs GUI/headless tests; on Linux CI the tests set QT_QPA_PLATFORM=offscreen and DISPLAY=:99 via the workflow.
- To replicate CI locally, set the following environment variables and limit threads:
   On POSIX shells:
       export QT_QPA_PLATFORM=offscreen
       export DISPLAY=:99
       export OMP_NUM_THREADS=1
       export NUMBA_NUM_THREADS=1

CI Quirk: Threading Deadlock on Linux (introduced when Python 3.13 added)

### Background:

- The repository historically supported Python >=3.10, <3.13 without issues. After changing to support Python 3.13, GitHub Actions (Ubuntu) began experiencing intermittent infinite hangs during tests that exercise reading CZI files and creating Napari viewers.
- Root cause is not a Python interpreter bug but a dependency resolution change: allowing 3.13 in pyproject.toml changed the dependency set pulled from PyPI, which introduced a combination of package versions (notably in imaging I/O/optimised libraries and czitools) that interact poorly in headless Linux CI, resulting in threading deadlock issues around subblock metadata reading.

### Symptoms:

- CI test jobs on ubuntu-latest hang indefinitely or until timeout on tests that call into CZI reading.
- Locally, Windows/macOS and Linux with older pinned dependencies may not reproduce the issue.

### Mitigations in repo (what we already do):

- tox.ini sets QT_QPA_PLATFORM=offscreen, OMP_NUM_THREADS=1, and NUMBA_NUM_THREADS=1 for linux envs.
- Tests include detection logic to detect headless Linux CI and skip or run reduced replacement/basic tests when the problematic environment is detected. This is a pragmatic short-term mitigation while the dependency root cause is investigated.

### How to reproduce/troubleshoot locally:

1. Reproduce the CI environment as closely as possible:
   On Linux or WSL run:
       export CI=true
       export GITHUB_ACTIONS=true
       export QT_QPA_PLATFORM=offscreen
       export DISPLAY=:99
       export OMP_NUM_THREADS=1
       export NUMBA_NUM_THREADS=1
       python -m tox -e py313-linux

2. Try pinning czitools to pre-3.13-era versions to see if the issue disappears:
       pip install 'czitools==0.10.3'
       pytest -k io -v

3. If you can reproduce, capture a minimal trace and dependency versions:
   In a Python REPL:
       import czitools, sys
       print('czitools', czitools.__version__)
       print('python', sys.version)

### How to Add Python 3.13 Support Properly

Recommended path to support Python 3.13 without CI flakes:

1. Add 3.13 to the CI matrix (already done) but iterate on dependencies: run the CI matrix locally (or in a dedicated ephemeral runner) and capture failing tests.
2. Narrow down which package versions changed between the previously-working state and now (e.g., czitools, numpy, pylibczirw, numba, pyqtgraph), and try pinning them in pyproject.toml to confirmed working ranges.
3. Open a small PR to pin suspect packages temporarily to a version that is known to work while the upstream bug is fixed in the dependency.
4. Alternatively, apply runtime mitigations (already added in tests) that keep threads limited in headless CI.

### Example pinning strategy (temporary): in pyproject.toml:

dependencies = [
    "numpy",
    "magicgui",
    "qtpy",
    "superqt",
    "scikit-image",
    "pyqtgraph",
    "czitools>=0.13.0,<0.20.0",  # pin to avoid threading deadlock in CI
]

### Tests and Local Debugging Tips

- To run a single test file:
       pytest src/napari_czitools/_tests/test_sample_data.py -q -k test_io

- To run tests with coverage (CI uses this):
       pytest -v --cov=napari_czitools --cov-report=xml

- If a test hangs, run with verbose logging and collect a thread dump (on Linux) to capture the state of threads.

### Recent Changes and Lessons Learned

- Dependency baseline now uses `czitools>=0.14.0`.
- `czitools==0.15.0` changed `read_tools.read_stacks` from returning
       3 values to returning 4 values:
       `(array6d, dims, num_stacks, metadata)`.
       Keep compatibility by supporting both tuple lengths in reader code.
- With newer `czitools`, lazy/stack reading may return a list of
       `xarray.DataArray` objects (one per scene) instead of a single stack.
       Code that processes arrays should accept both shapes.
- Channel coordinates can be string labels (for example `DAPI`, `EGFP`).
       Prefer positional indexing (`isel`) over label indexing (`sel`) when
       iterating channels by integer index.
- GUI tests depend on `pytest-qt`. Keep `pytest-qt` in testing dependencies,
       and if unavailable, use skip-only fallbacks rather than hard failures.
- Do not manually register `pytestqt.plugin` in `conftest.py` when it is
       already auto-discovered, as this can cause duplicate plugin registration
       errors.
- URL metadata tests against remote assets can fail transiently with errors
       like `Error reading FileHeaderSegment`. Prefer retry + graceful skip
       behavior for network-dependent tests.
- The custom `DoubleRangeSlider` (hand-coded `QSlider` subclass with manual
       `paintEvent` / `mousePressEvent` / `mouseMoveEvent`) has been replaced
       with thin wrappers around **superqt**'s `QLabeledRangeSlider` and
       `QRangeSlider`.  The public API (`low()`, `high()`, `setLow()`,
       `setHigh()`, `valueChanged(int, int)`, `setSingleValueMode()`,
       `setProperty("single_value_mode", ...)`) is unchanged, so all
       consumers in `_widget.py` and tests work without modification.
       `superqt` is already a declared dependency.
- superqt's `QRangeSlider` enforces a minimum gap of `singleStep()`
       between handles by default, which prevents single-frame extraction
       (e.g. both handles at value 4).  The helper
       `_allow_handle_overlap()` in `_doublerange_slider.py` patches the
       internal `_neighbor_bound` method to use zero gap so handles can
       sit on the same value.  This patch is applied to every slider
       instance at construction time.
- When modifying slider code, prefer using the superqt wrapper API in
       `_doublerange_slider.py` rather than re-introducing custom QSlider
       painting or mouse-event handling.

### Release Process

1. Ensure pyproject.toml has the new version and requires-python appropriately set (supporting 3.13 is fine, but be conservative with transitive dependency pins if CI is unstable).
2. Create a PR and ensure all CI checks pass (or if Linux CI has known threading flakes, provide evidence in CI logs and use the replacement tests to validate basic functionality).
3. Tag and push a release commit; CI will build and publish according to .github/workflows/test_and_deploy_pypi.yml.

PR Checklist (suggested)

- [ ] Code follows repository style
- [ ] Unit tests added or updated
- [ ] CI green or documented mitigations
- [ ] Version bump in pyproject.toml (if releasing)
- [ ] Update CHANGELOG.md (if present)

### Testing CZI Sample Reading

The CZI file reading tests are automatically skipped on Linux headless/CI environments due to threading deadlock issues. To test sample reading locally:

**On macOS or Windows (no skip):**
```bash
pytest src/napari_czitools/_tests/test_sample_data.py::test_io -v
pytest src/napari_czitools/_tests/test_sample_data.py::test_open_sample -v
```

**On Linux (force test despite threading issues):**
```bash
FORCE_CZI_TESTS=1 pytest src/napari_czitools/_tests/test_sample_data.py::test_io -v
FORCE_CZI_TESTS=1 pytest src/napari_czitools/_tests/test_sample_data.py::test_open_sample -v
```

**Note:** Setting `FORCE_CZI_TESTS=1` may cause the test process to hang or crash on Linux due to known threading deadlock issues with aicspylibczi/czitools. This is expected and not a problem with the plugin code itself.

### Notes for Copilot / Contributors

- When asked to modify tests that involve CZI reading, prefer adding environment detection and minimal mitigations (disable progress bars, limit number of threads) rather than broad Python-version-based skips.
- If adding Python 3.13 to the matrix, add it incrementally and be prepared to pin transitive dependencies if CI starts failing.
- Always reproduce CI issues locally where possible and prefer opening small PRs that pin suspect packages while investigating upstream fixes.

If you'd like, I can:

- open a PR that pins czitools temporarily and run local CI to verify
- create a short README_CONTRIBUTING.md with the commands shown above
- add a small debugging script that prints dependency versions used in CI
