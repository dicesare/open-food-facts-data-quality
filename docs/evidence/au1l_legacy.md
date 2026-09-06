# AU-1L legacy-boundary evidence

- Accepted predecessor: AU-0 at `b84ad148011e2cdbec5d888c3295faaee49a5a32`
- Scope: legacy warning, classification and import-boundary validation only
- State: `VALIDATION`
- Accepting owner: Software Red Team

## Boundary decision

The legacy classification is attached to an operation, not to the Pandas object or
domain value returned by that operation. Existing raw-frame entry points therefore
keep their characterized signatures, return types, values and non-mutation behavior.
Each call records the immutable classification `LEGACY_UNPROVENANCED` and emits a
deprecation warning. A returned `DataFrame`, `Series`, `CleaningReport` or
`DatasetProfile` does not gain an `evidence_status`, `population_ref` or
`run_context` attribute.

This operation-level choice avoids presenting a mutable Pandas result as evidence
and prevents legacy output from acquiring provenance after the fact. The
classification cannot be promoted to `REPRODUCED` or to an E0–E8 result. Future
evidence code must use its own provenance-bearing types and cannot import raw-frame
legacy entry points.

`pipeline.py` remains the sole composition root during AU-1L. This unit does not
create an evidence namespace, a CLI, a second pipeline module or an alternate
runtime path.

## Validation matrix

| Test ID | Contract | Validation state |
|---|---|---|
| T-LEG-01 | Each characterized raw-frame operation emits the legacy deprecation warning with `LEGACY_UNPROVENANCED`. | IN VALIDATION |
| T-LEG-02 | Public signatures, return values, ordering, rejection counts and input non-mutation remain compatible with the AU-0 baseline. | IN VALIDATION |
| T-LEG-03 | Legacy classification is immutable; conversion or promotion to `REPRODUCED` or E0–E8 is rejected. | IN VALIDATION |
| T-LEG-04 | Static import rules reject absolute, relative and re-exported legacy imports from the future evidence namespace while preserving `pipeline.py` as the only composition root. | IN VALIDATION |

PASS requires the complete suite, Ruff, strict mypy, compilation and the independent
Software Red Team decision. Until those receipts are recorded here, AU-1L remains in
validation.

## Limits and authority

This boundary labels compatibility operations; it does not establish source
provenance, historical reproducibility or scientific validity. It produces no E0–E8
result and does not authorize dataset access, notebook execution, dependency changes,
AU-1 implementation, publication or push. A failure is rolled back as the complete
AU-1L commit to the accepted AU-0 state.

**STATUS: VALIDATION**
