# AU-0 baseline evidence

- Source baseline: `ae5a6b1c6056376cd2cf7e378fa965ece216e33b`
- Scope: tests and documentation only
- Runtime: Python 3.12, Pandas 3.0.5, NumPy 2.5.2
- Environment role: compatibility characterization, not historical reconstruction

## Acceptance results

| Test ID | Command or artifact | Result |
|---|---|---|
| T-BASE-01 | `.venv/bin/pytest -q` before additions | PASS — 18 collected cases |
| T-BASE-02 | public API characterization in full suite | PASS |
| T-BASE-03 | static internal import graph in full suite | PASS |
| T-RAW-01 | cleaning order/threshold/survivor/counts | PASS |
| T-RAW-02 | custom-rule order and aggregation | PASS |
| T-RAW-03 | labelled descending missingness | PASS |
| T-RAW-04 | most-frequent/constant imputation and nonmutation | PASS — 2 cases |
| T-RAW-05 | empty-profile denominators and column order | PASS |
| T-RAW-06 | absence of provenance on raw-frame results | PASS |
| Suite | `.venv/bin/pytest -q` after additions | PASS — 29 collected cases |
| Lint | `.venv/bin/ruff check src tests` | PASS |
| Types | `.venv/bin/mypy src` | PASS — 6 source files |

No production source file, declared dependency, dataset or notebook is changed. These observations characterize compatibility behavior and make no scientific-validity claim.
