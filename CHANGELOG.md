# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Removed `cytoolz` dependency not used by `extra-model`
- Updated from using `pycld2` to `pycld3`
- Added fourth positional command line argument to specify the path to the embeddings
- Fixed bug with double spaces (e.g., `I bought a sturdy and  beautiful shelf.` sentence would be parsed incorrectly)

## [0.2.0] 2021-03-17

- Initial release
