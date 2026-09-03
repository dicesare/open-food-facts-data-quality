# P3 implementation ledger

## Authority and scope

- Frozen source baseline: `ae5a6b1c6056376cd2cf7e378fa965ece216e33b`.
- Planning authority: parent infrastructure commit `a6fafb0` and normative implementation-plan amendment `05b`.
- Current atomic unit: `AU-0`, baseline characterization only.
- No production behavior, dataset, notebook, dependency declaration or experiment is changed by AU-0.

## Baseline receipt

| Check | AU-0 evidence | Result |
|---|---|---|
| T-BASE-01 | `.venv/bin/pytest -q` before AU-0 additions | PASS — 18 tests |
| T-BASE-02 | `tests/test_public_api_characterization.py` | PASS — full 29-case suite |
| T-BASE-03 | `tests/test_import_graph_characterization.py` | PASS — full 29-case suite |
| Lint | `.venv/bin/ruff check src tests` before AU-0 additions | PASS |
| Types | `.venv/bin/mypy src` before AU-0 additions | PASS — 6 source files |

Characterization ran on Python 3.12 with Pandas 3.0.5 and NumPy 2.5.2 from the local isolated `.venv`. This is compatibility evidence only. It is not the candidate Python 3.12/Pandas 2.2.3 historical reconstruction environment and proves no E0/E8 result.

## Characterized public boundary

The package exports 14 names through `off_quality.__all__`. Current evidence-adjacent entry points `clean_products`, `QualityPipeline.run`, `DataProfiler.profile`, `missingness`, `ColumnImputer.fit` and `FittedColumnImputer.transform` accept or return raw Pandas objects. Their outputs carry no `evidence_status`, `population_ref` or `run_context`. AU-0 records this behavior without endorsing it; AU-1L must isolate it as `LEGACY_UNPROVENANCED` before any evidence API is introduced.

The current internal import graph has one orchestration implementation module, `pipeline.py`. There is no `cli.py` or `pipelines.py`. This snapshot is the comparison point for T-LEG-04 and T-ROOT-01 in later units.

## AU-0 acceptance ledger

| Requirement | Atomic unit | Baseline commit | Contract | Test IDs | Evidence path | Implementation owner | Accepting owner | Status |
|---|---|---|---|---|---|---|---|---|
| BASE-SUITE | AU-0 | `ae5a6b1` | Existing behavior remains green | T-BASE-01 | `docs/evidence/au0_baseline.md` | ML Quality Engineer | ML Quality Engineer | PASS |
| PUBLIC-API | AU-0 | `ae5a6b1` | Fourteen top-level exports and raw signatures remain observable | T-BASE-02 | `docs/evidence/au0_baseline.md` | ML Quality Engineer | Software Architect | PENDING REVIEW |
| IMPORT-GRAPH | AU-0 | `ae5a6b1` | Current edges and sole `pipeline.py` root are recorded | T-BASE-03 | `docs/evidence/au0_baseline.md` | ML Quality Engineer | Software Architect | PENDING REVIEW |
| LEGACY-RAW | AU-0 | `ae5a6b1` | Cleaning, extension seam, missingness, imputation and profiling behavior is characterized without provenance claims | T-RAW-01..06 | `docs/evidence/au0_baseline.md` | ML Quality Engineer | Software Architect | PENDING REVIEW |

## SRT implementation ledger

Status meanings: `PLANNED` is architecture-only; `ACTIVE` is the current unit; `PASS` requires immutable test evidence and the accepting owner; `BLOCKED` prevents successor work.

| SRT | Atomic unit | Test IDs | Evidence path | Accepting owner | Status |
|---|---|---|---|---|---|
| 01 | AU-1 | T-TRUST-01..04 | `docs/evidence/au1_trust.md` | Software Red Team | PLANNED |
| 02 | AU-6 | T-LOCK-01..07 | `docs/evidence/au6_fixture_custody.md` | Release Custodian + Software Red Team | PLANNED |
| 03 | AU-2B | T-SRC-01..04 | `docs/evidence/au2b_source.md` | Reproducibility Reviewer | PLANNED |
| 04 | AU-3 | T-PARSE-01..05 | `docs/evidence/au3_parser.md` | Historical Integrity Reviewer | PLANNED |
| 05 | AU-1L | T-LEG-01..04 | `docs/evidence/au1l_legacy.md` | Software Red Team | PLANNED |
| 06 | AU-5A | T-ART-01..08 | `docs/evidence/au5a_transactions.md` | Software Red Team | PLANNED |
| 07 | AU-0..10 | T-MOD-01 | `docs/evidence/module_callers.md` | Software Architect + Software Red Team | ACTIVE |
| 08 | AU-1, AU-10A..C | T-ROOT-01..04, T-CLI-01..03 | `docs/evidence/composition_root.md` | Software Red Team | PLANNED |
| 09 | AU-2A | T-ENV-01..03 | `docs/evidence/au2a_environments.md` | Reproducibility Reviewer | PLANNED |
| 10 | AU-7 | T-RES-01..06 | `docs/evidence/au7_supervisor.md` | ML Quality Engineer + Software Red Team | PLANNED |
| 11 | AU-5B | T-PRIV-01..06 | `docs/evidence/au5b_privacy.md` | Privacy Reviewer | PLANNED |
| 12 | AU-11 | all above + T-ID-05/T-LOCK-03 | `docs/evidence/au11_scorecard.md` | Independent Software Red Team | PLANNED |

## E0–E8 implementation map

| Experiment | First implementation unit | Current state |
|---|---|---|
| E0 | AU-3 | BLOCKED by AU-0 → AU-1L → AU-1 → AU-2A/B |
| E1–E3 | AU-4A/B | BLOCKED by E0 implementation gates |
| E4–E5 | AU-8A/B | BLOCKED by fixture partitions, artifacts/privacy and resource gates |
| E6–E8 logic | AU-9A/B | BLOCKED by preceding fixture-only gates |
| Real E0–E8 execution | later execution plan | BLOCKED; outside implementation authority |

## AU-0 exit gate

AU-0 passes only when the original 18 tests plus T-BASE-02/T-BASE-03 pass, Ruff and mypy remain green, the diff contains no production source change, and an independent reviewer confirms that the tests characterize rather than redefine behavior. The next possible handoff is AU-1L; it is not authorized until AU-0 receives PASS.
