# Changelog



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
* `tox`, because it's a piece of shit and I hate it deeply
* `setup.py` has been removed in favour of `pyproject.toml`

