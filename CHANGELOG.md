# Changelog

## v2.0.0 (2025-07-28)

### Changed
`UndetectedChrome` is now part of a separate package `selenium-wire-undetected-chromedriver-lw`, because undetected_chromedriver is licensed under GPLv3. This should ensure only the undetected-chromedriver bits need to be GPL, and avoids a total relicensing of the preexisting code in this repo.

To get `UndetectedChrome` back:

1. `pip3 install selenium-wire-undetected-chromedriver-lw`
2. `from seleniumwire_gpl import UndetectedChrome`

The GPL'd package is stored in [this repo](https://github.com/LunarWatcher/selenium-wire-undetected-chromedriver)

## v1.1.1 (2025-07-21)

### Fixed
* `UndetectedChrome` had accidental references to `FirefoxOptions`
* Type check exceptions from `UndetectedChrome` and `UndetectedFirefox` to silence `ImportError`, but re-raise anything else

## v1.1.0 (2025-07-10)

### Added 
* `{request,response}.decompress_body()` for automatically decompressing currently four known encodings (deflate, brotli, zstd, gzip). For no encoding, this function is a noop that's identical to `.body`. For unknown encodings, this function throws an exception.
    * Everything except `zstd` has been tested. `httpbin`, which is used for the tests, unfortunately does not support zstd.

### Changed
* `body` and `headers` are now managed by a superclass for both `request` and `response`. This gives some reduced code duplication in common code shared between requests and responses. This should not affect anything external.

### Fixed
* Test-meta: e2e test fixtures moved into a common `e2e_utils.py` for reuse in future tests

## v1.0.2 (2025-07-06)

???, I dropped the ball

## v1.0.1 (2025-07-05)

### Fixed
* os.mkdir -> os.makedirs so it doesn't fail when making nested folders

## v1.0.0 (2025-07-05)

### Added
* `UndetectedFirefox` and `UndetectedChrome` if the appropriate packages (`undetected-geckodriver-lw` and `undetected-chromedriver` respectively) are installed
    * Three different optional variants `[uf]` (undetected firefox), `[uc]` (undetected chrome), `[ud]` (undetected, equivalent to `uf` and `uc`) 
* `requirements.txt`, exclusively used for local development.

### Changed
* `.rst` -> `.md`
    * Except `AUTHORS.rst`, which has been removed. To see the authors, see the special GitHub/Codeberg view, or use the Git log. It's there for a reason, it doesn't need to be duplicated in a special file

### Fixed
* Flaky test_capture_requests test

### Removed
* `tox`, because it's a piece of shit, I hate it deeply, and it single-handedly cost me significant amounts of time while trying an initial refactor of the original selenium-wire (i.e. not selenium-wire-2)
* `setup.py` has been removed in favour of `pyproject.toml`

