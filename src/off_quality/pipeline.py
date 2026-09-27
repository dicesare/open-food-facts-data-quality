"""SOLID, composable strategies for reproducible product-data cleaning."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd

from .domain import (
    CleaningPolicy,
    CleaningReport,
    RejectionReason,
    _warn_legacy_entry_point,
)


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
        if not result.columns.is_unique:
            raise ValueError("Column normalization produces duplicate names")
        return RuleResult(result)


@dataclass(frozen=True, slots=True)
class DropSparseColumns:
    name: str = "drop_sparse_columns"

    def apply(self, frame: pd.DataFrame, policy: CleaningPolicy) -> RuleResult:
        keep = frame.columns[
            (frame.isna().mean() <= policy.max_missing_ratio)
            | (frame.columns == policy.barcode_column)
        ]
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
        pattern = rf"[0-9]{{{policy.minimum_barcode_length},{policy.maximum_barcode_length}}}"
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
        _warn_legacy_entry_point("QualityPipeline.run")
        return self._run(frame)

    def _run(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
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
        """Process independent chunks; schema selection and deduplication are per chunk.

        This is not equivalent to cleaning the concatenated dataset: callers must
        handle cross-chunk duplicates and global column selection separately.
        """
        _warn_legacy_entry_point("QualityPipeline.run_stream")
        for chunk in chunks:
            yield self._run(chunk)


def verify_config(bundle_path: str | Path, expected_sha256: str) -> bool:
    import hashlib
    import json
    from pathlib import Path

    bundle_path = Path(bundle_path)
    manifest_path = bundle_path / "freeze_manifest.json"

    if not manifest_path.is_file():
        return False

    try:
        manifest_bytes = manifest_path.read_bytes()
        actual_sha256 = hashlib.sha256(manifest_bytes).hexdigest()

        if actual_sha256 != expected_sha256:
            return False

        manifest = json.loads(manifest_bytes)

        manifest_files = manifest.get("files", [])
        expected_paths = {f["path"]: f["sha256"] for f in manifest_files}

        actual_paths = {p.name for p in bundle_path.iterdir() if p.is_file()}
        expected_names = set(expected_paths.keys())
        expected_names.add("freeze_manifest.json")

        if actual_paths != expected_names:
            return False

        for f in manifest_files:
            file_path = bundle_path / f["path"]
            if not file_path.is_file():
                return False
            if hashlib.sha256(file_path.read_bytes()).hexdigest() != f["sha256"]:
                return False

        gov_path = bundle_path / "governance.json"
        if gov_path.is_file():
            gov = json.loads(gov_path.read_bytes())
            if not isinstance(gov.get("privacy", {}).get("forbidden_fields"), list):
                return False

        fl_path = bundle_path / "feature_lineage.json"
        if fl_path.is_file():
            fl = json.loads(fl_path.read_bytes())
            allowlist = fl.get("predictor_allowlist", {})
            if "salt_100g" in allowlist.get("sodium_100g", []):
                return False
            if "sodium_100g" in allowlist.get("salt_100g", []):
                return False

        return True
    except (ValueError, KeyError, FileNotFoundError, json.JSONDecodeError, AttributeError):
        return False
