# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unrealeased]

### Changed
- Updated all versions to the latest available (courtesy of `dependabot`)
- Added `run_from_dataframe` in `_run.py`, which enables passing dataframe as an input
- Dropped Python 3.7 support (i.e., we no longer test for this version) since `numpy` dropped it

### Fixed
- an update to scipy exposed an issue in rare cases in disambiguation, where choice of meaning for contextless aspects 
only worked accidentally. These are now treated explicitly: we choose the most common meaning.


## [0.3.0]

### Changed
- All, but one inputs to `extra-model` are now options. 

Before, all, but one parameter (`--debug`) that you could provide to CLI version of `extra-model` were arguments, which in `click` 
parlance meant that they were positional. That in turn means that you could only change, e.g., embeddings path by
specifying both output path AND output filename. Well, no longer! From now on all, but one inputs to `extra-model` (input path), are options
which means that they can be set in any order using flags that you can see by running `extra-model --help`.
No need to thank us :).

- Added input validation, so now `extra-model` will throw an error if `CommentId` column is misspelled.
- Added `click` as explicit dependency. It was erroneously removed at some point, but we actually depend on it, so adding it back in.
- Updated all other dependencies to the most up-to-date version (as of October, 22nd 2021)
- Consolidated `adjective_list()` and `acomp_list()` into generic
  `adjective_phrase()` function
- Upgraded default Python version to 3.9

### Removed
- Removed the dependency on `requests` since we don't use it explicitly in our code


## [0.2.1]

### Changed

- Removed `cytoolz` dependency not used by `extra-model`
- Updated from using `pycld2` to `pycld3`
- Added fourth positional command line argument to specify the path to the embeddings
- Fixed a bug with multiple spaces (e.g., "I bought a sturdy and^^^beautiful shelf." sentence would be parsed incorrectly)
- `extra-model` is now tested in Python 3.7, 3.8, 3.9

## [0.2.0] 2021-03-17

- Initial release
