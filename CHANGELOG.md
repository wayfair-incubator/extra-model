# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

**Final release. This project is archived and will receive no further updates.**

### Changed
- **`extra-model` now requires Python 3.12 or 3.13.** Support for 3.8 through 3.11 is
  dropped. Python 3.14 is not supported and cannot be: `gensim` and `spacy` publish no
  wheels for it, and both are load-bearing dependencies.
- Every dependency moved to the highest version installable on 3.12/3.13:
  `click` 8.4.2, `numpy` 2.5.2, `nltk` 3.10.2, `scikit-learn` 1.9.0, `pandas` 3.0.5,
  `networkx` 3.6.1, `gensim` 4.4.0, `scipy` 1.18.0, `spacy` 3.8.15. `langdetect` and
  `vaderSentiment` are unmaintained upstream and stay at 1.0.9 and 3.3.2.
  The `gensim` bump is what unblocked `scipy`: 4.3.3 imported `scipy.linalg.triu`,
  removed in scipy 1.13.
- Dependencies are now declared as `>=X,<next-major` ranges instead of exact `==` pins,
  so the archived package can still resolve alongside other libraries. `requirements.txt`
  keeps exact pins for reproducible builds.
- The `en_core_web_sm` 3.8.0 spacy pipeline is now a pinned dependency. It used to be
  fetched unversioned with `python -m spacy download`, which meant the model could change
  underneath a fixed release. Installing `extra-model` no longer requires a separate
  download step.
- Packaging consolidated into `pyproject.toml`; `setup.py`, `setup.cfg`, `pytest.ini`,
  `mypy.ini` and `.isort.cfg` are gone. Versioning moved from `bump2version` to
  `bump-my-version`.
- Docker image moved from `python:3.10-slim-buster` to `python:3.13-slim-bookworm`.
  Debian buster is EOL and its apt repositories are archived, so the old image could no
  longer be built at all.
- Dropped Python 3.8 support because multiple major packages dropped support for it
- Removed codecov support as it now requires paying for it if you are part of an organization

### Fixed
- **Published wheels now declare `Requires-Python`.** `setup.cfg` contained
  `python_requires >=3.9,<3.11` with the `=` missing after the key, so configparser
  parsed it as a key named `python_requires >` and the constraint was silently dropped.
  Every previous release, including 0.4.0 on PyPI, shipped with empty `Requires-Python`
  metadata, so pip would install this package on any interpreter.
- **`pip install extra-model` was broken.** `nltk` 3.8.2 moved `word_tokenize` to the
  `punkt_tab` resource, but the Dockerfile, CI and installation docs all downloaded
  `punkt`. Since the package required `nltk` 3.9.1, a correct installation raised
  `LookupError` at runtime. CI did not catch this because its test job installed
  `requirements.txt` (which pinned `nltk` 3.8.1) and never installed the package itself.
- The API Reference documentation page is restored. `mkdocs.yml` still used the
  pre-0.19 `mkdocstrings` `selection:`/`rendering:` schema, which broke rendering; the
  page had been commented out of the navigation.
- The CI `isort` job passed `--recursive`, a flag removed in isort 5, so it had not been
  running correctly.
- Embeddings are downloaded over HTTPS instead of plain HTTP.

### Notes on behavior
- Output is effectively unchanged by the upgrade. On the 100-comment reference corpus,
  13 of 14 output columns are bit-identical to 0.4.0 — all aspects, descriptors, topics,
  wordnet nodes, sentiments and counts. Only `TopicImportance` differs, by at most
  1.1e-09 absolute (2.5e-08 relative), which is floating-point accumulation noise.
- In particular, the `networkx` `steiner_tree` default method change from `kou` to
  `mehlhorn` did not alter topic structure.
- `pandas` 3.0 changes the in-memory dtype of text columns from `object` to `str`. The
  CSV output and the `predict()` return value are unaffected.
- Internal dataframe helpers no longer mutate their arguments in place.
  `_summarize.link_aspects_to_topics` now returns both dataframes rather than adding a
  column to the topic frame as a side effect. This is internal API, not part of the
  documented public surface.

## [0.4.0]

### Changed
- Updated all versions to the latest available (courtesy of `dependabot`)
- Added `run_from_dataframe` in `_run.py`, which enables passing dataframe as an input
- Dropped Python 3.7 support (i.e., we no longer test for this version) since `numpy` dropped it
- Added support for Python 3.10
- Replaced `pycld3` with `langdetect`. `pycld3` is unlikely to be supported in 3.10 and it recently started failing to build in 3.9. Since `pycld3` was only used in one place and given that `langdetect` looks like a reasonable replacement, we've decided to replace it.

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
