Copilot Instructions for napari-czitools

This file provides comprehensive guidance for GitHub Copilot and human contributors working on the napari-czitools repository. It explains repository layout, development and testing workflows, CI quirks (notably the Linux CI threading deadlock introduced when Python 3.13 was added), debugging tips, and release procedures.

Repository Overview

- Project: napari-czitools
- Language: Python
- Packaging: pyproject.toml (PEP 621)
- Tests: pytest, configured via tox.ini and GitHub Actions workflow .github/workflows/test_and_deploy_pypi.yml

Top-level layout (key files):

- pyproject.toml - project metadata and dependencies
- tox.ini - test matrix configuration used locally and by CI
- README.md - user-facing documentation
- src/napari_czitools - package source
- src/napari_czitools/_tests - test suite
- .github/workflows/test_and_deploy_pypi.yml - CI workflow used to run tests and deploy

Development Setup

Prerequisites:

- Python 3.10+ (3.13 supported)
- pip and virtualenv or a modern Python environment manager

Quick start (recommended):

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

Notes about headless GUI tests:

- The test matrix runs GUI/headless tests; on Linux CI the tests set QT_QPA_PLATFORM=offscreen and DISPLAY=:99 via the workflow.
- To replicate CI locally, set the following environment variables and limit threads:
   On POSIX shells:
       export QT_QPA_PLATFORM=offscreen
       export DISPLAY=:99
       export TQDM_DISABLE=1
       export OMP_NUM_THREADS=1
       export NUMBA_NUM_THREADS=1

CI Quirk: Threading Deadlock on Linux (introduced when Python 3.13 added)

Background:

- The repository historically supported Python >=3.10, <3.13 without issues. After changing to support Python 3.13, GitHub Actions (Ubuntu) began experiencing intermittent infinite hangs during tests that exercise reading CZI files and creating Napari viewers.
- Root cause is not a Python interpreter bug but a dependency resolution change: allowing 3.13 in pyproject.toml changed the dependency set pulled from PyPI, which introduced a combination of package versions (notably in imaging I/O/optimised libraries and czitools) that interact poorly in headless Linux CI, resulting in a threading deadlock around progress bars and subblock metadata reading.

Symptoms:

- CI test jobs on ubuntu-latest hang indefinitely or until timeout on tests that call into CZI reading or use progress bars.
- Locally, Windows/macOS and Linux with older pinned dependencies may not reproduce the issue.

Mitigations in repo (what we already do):

- tox.ini sets TQDM_DISABLE=1, QT_QPA_PLATFORM=offscreen, OMP_NUM_THREADS=1, and NUMBA_NUM_THREADS=1 for linux envs.
- Tests include detection logic to detect headless Linux CI and skip or run reduced replacement/basic tests when the problematic environment is detected. This is a pragmatic short-term mitigation while the dependency root cause is investigated.

How to reproduce/troubleshoot locally:

1. Reproduce the CI environment as closely as possible:
   On Linux or WSL run:
       export CI=true
       export GITHUB_ACTIONS=true
       export QT_QPA_PLATFORM=offscreen
       export DISPLAY=:99
       export TQDM_DISABLE=1
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

How to Add Python 3.13 Support Properly

Recommended path to support Python 3.13 without CI flakes:

1. Add 3.13 to the CI matrix (already done) but iterate on dependencies: run the CI matrix locally (or in a dedicated ephemeral runner) and capture failing tests.
2. Narrow down which package versions changed between the previously-working state and now (e.g., czitools, numpy, pylibczirw, tqdm, numba, pyqtgraph), and try pinning them in pyproject.toml to confirmed working ranges.
3. Open a small PR to pin suspect packages temporarily to a version that is known to work while the upstream bug is fixed in the dependency.
4. Alternatively, apply runtime mitigations (already added in tests) that keep threads limited and disable progress bars in headless CI.

Example pinning strategy (temporary): in pyproject.toml:

dependencies = [
    "numpy",
    "magicgui",
    "qtpy",
    "superqt",
    "scikit-image",
    "pyqtgraph",
    "czitools>=0.11.0,<0.11.2"
]

Tests and Local Debugging Tips

- To run a single test file:
       pytest src/napari_czitools/_tests/test_sample_data.py -q -k test_io

- To run tests with coverage (CI uses this):
       pytest -v --cov=napari_czitools --cov-report=xml

- If a test hangs, run with verbose logging and collect a thread dump (on Linux) to capture the state of threads.

Release Process

1. Ensure pyproject.toml has the new version and requires-python appropriately set (supporting 3.13 is fine, but be conservative with transitive dependency pins if CI is unstable).
2. Create a PR and ensure all CI checks pass (or if Linux CI has known threading flakes, provide evidence in CI logs and use the replacement tests to validate basic functionality).
3. Tag and push a release commit; CI will build and publish according to .github/workflows/test_and_deploy_pypi.yml.

PR Checklist (suggested)

- [ ] Code follows repository style
- [ ] Unit tests added or updated
- [ ] CI green or documented mitigations
- [ ] Version bump in pyproject.toml (if releasing)
- [ ] Update CHANGELOG.md (if present)

Notes for Copilot / Contributors

- When asked to modify tests that involve CZI reading, prefer adding environment detection and minimal mitigations (disable progress bars, limit number of threads) rather than broad Python-version-based skips.
- If adding Python 3.13 to the matrix, add it incrementally and be prepared to pin transitive dependencies if CI starts failing.
- Always reproduce CI issues locally where possible and prefer opening small PRs that pin suspect packages while investigating upstream fixes.

If you'd like, I can:

- open a PR that pins czitools temporarily and run local CI to verify
- create a short README_CONTRIBUTING.md with the commands shown above
- add a small debugging script that prints dependency versions used in CI