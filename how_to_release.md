# How to release a new version

* run all test locally on working branch
* make sure the main branch is up-to-date
* re-run test
* Create a new release tag

`git tag -a v0.0.4 -m "Release version 0.0.4 - ...."`

* Push the changes

`git push --follow-tags`

* if all test pass the should be a new version on [PyPi: napari-czitools](https://pypi.org/project/napari-czitools/)