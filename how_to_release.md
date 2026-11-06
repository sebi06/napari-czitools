# Releasing napari-czitools

The package version is derived from Git tags by `setuptools_scm`. The PyPI
workflow runs for tags matching `v*`; its test job must pass before the deploy
job publishes the package through PyPI Trusted Publishing.

## Before tagging

1. Check the latest published version and existing Git tags, then choose the next unused semantic version. Do not reuse an existing version or tag.
2. Move the release entries from the `Unreleased` section in `CHANGELOG.md` into a dated heading for the new version, leaving an empty `Unreleased` section.
3. Create `_release_notes/vX.Y.Z.md` with the release summary, compatibility requirements, installation commands, and relevant limitations. Update the README's release-notes link and compatibility guidance. Preserve historical release notes.
4. Review and commit the release documentation to `main`. Keep `dynamic = ["version"]` in `pyproject.toml`; the annotated tag determines the package version.
5. Confirm `main` is up to date and its CI checks pass. The release workflow runs tox on Python 3.12 and 3.13 across Linux, Windows, and macOS.

## Tag and publish

Create and push an annotated version tag from the release commit:

```bash
git tag -a vX.Y.Z -m "Release napari-czitools X.Y.Z"
git push origin vX.Y.Z
```

Publish a GitHub release using the same source-controlled notes:

```bash
gh release create vX.Y.Z --verify-tag --title "napari-czitools vX.Y.Z" --notes-file _release_notes/vX.Y.Z.md
```

Monitor **Actions > test_and_deploy_pypi**. The tag's tests run first; after
they pass, the workflow builds the distribution and publishes it to
[PyPI](https://pypi.org/project/napari-czitools/). Verify the published version
and release files there.

For a CI-only pre-release test, use the separate `test_and_deploy_testpypi`
workflow and its `testpypi-vX.Y.Z` tag convention. The workflow currently runs
tests but does not build or publish a package to TestPyPI, so it cannot be used
to verify a TestPyPI artifact. Do not use a TestPyPI tag for a production
release.
