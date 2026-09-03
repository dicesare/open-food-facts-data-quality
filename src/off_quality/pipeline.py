"""SOLID, composable strategies for reproducible product-data cleaning."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from .domain import CleaningPolicy, CleaningReport, RejectionReason


@dataclass(frozen=True, slots=True)
class RuleResult:
    frame: pd.DataFrame
    reason: RejectionReason | None = None
    rejected_rows: int = 0


class FrameRule(Protocol):
    @property
    def name(self) -> str: ...

    def apply(self, frame: pd.DataFrame, policy: CleaningPolicy) -> RuleResult: ...


@dataclass(frozen=True, slots=True)
class NormalizeColumns:
    name: str = "normalize_columns"

    def apply(self, frame: pd.DataFrame, policy: CleaningPolicy) -> RuleResult:
        result = frame.copy()
        result.columns = result.columns.str.strip().str.replace("-", "_", regex=False)
        return RuleResult(result)


@dataclass(frozen=True, slots=True)
class DropSparseColumns:
    name: str = "drop_sparse_columns"

    def apply(self, frame: pd.DataFrame, policy: CleaningPolicy) -> RuleResult:
        keep = frame.columns[frame.isna().mean() <= policy.max_missing_ratio]
        return RuleResult(frame.loc[:, keep].copy())


@dataclass(frozen=True, slots=True)
class ValidateBarcodes:
    name: str = "validate_barcodes"

    def apply(self, frame: pd.DataFrame, policy: CleaningPolicy) -> RuleResult:
        column = policy.barcode_column
        if column not in frame:
            raise ValueError(f"Missing required column: {column}")
        result = frame.copy()
        result[column] = result[column].astype("string").str.strip()
        pattern = rf"\d{{{policy.minimum_barcode_length},{policy.maximum_barcode_length}}}"
        valid = result[column].str.fullmatch(pattern, na=False)
        return RuleResult(result.loc[valid].copy(), RejectionReason.INVALID_BARCODE, int((~valid).sum()))


@dataclass(frozen=True, slots=True)
class DeduplicateProducts:
    name: str = "deduplicate_products"

    def apply(self, frame: pd.DataFrame, policy: CleaningPolicy) -> RuleResult:
        duplicate = frame.duplicated(subset=[policy.barcode_column], keep="first")
        return RuleResult(
            frame.loc[~duplicate].reset_index(drop=True),
            RejectionReason.DUPLICATE_BARCODE,
            int(duplicate.sum()),
        )


DEFAULT_RULES: tuple[FrameRule, ...] = (
    NormalizeColumns(),
    DropSparseColumns(),
    ValidateBarcodes(),
    DeduplicateProducts(),
)


class QualityPipeline:
    """Orchestrator depending on the FrameRule protocol, not concrete rules."""

    def __init__(self, policy: CleaningPolicy | None = None, rules: Sequence[FrameRule] = DEFAULT_RULES) -> None:
        self._policy = policy or CleaningPolicy()
        self._rules = tuple(rules)

    def run(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        current = frame
        rejected: dict[RejectionReason, int] = {}
        for rule in self._rules:
            outcome = rule.apply(current, self._policy)
            current = outcome.frame
            if outcome.reason is not None:
                rejected[outcome.reason] = rejected.get(outcome.reason, 0) + outcome.rejected_rows
        return current, CleaningReport(
            input_rows=len(frame), output_rows=len(current),
            input_columns=len(frame.columns), output_columns=len(current.columns),
            rejected_by_reason=rejected,
        )

    def run_stream(self, chunks: Iterable[pd.DataFrame]) -> Iterator[tuple[pd.DataFrame, CleaningReport]]:
        for chunk in chunks:
            yield self.run(chunk)
