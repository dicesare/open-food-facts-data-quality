"""Typed domain objects for the data-quality pipeline."""

from __future__ import annotations

import warnings
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType


class LegacyEvidenceStatus(StrEnum):
    LEGACY_UNPROVENANCED = "LEGACY_UNPROVENANCED"


class LegacyEvidenceTransitionError(ValueError):
    """Raised when a raw-frame call requests a non-legacy classification."""


class LegacyUnprovenancedWarning(DeprecationWarning):
    """Marks a compatible raw-frame call as unsuitable for evidence."""

    @property
    def evidence_status(self) -> LegacyEvidenceStatus:
        return LegacyEvidenceStatus.LEGACY_UNPROVENANCED


def _warn_legacy_entry_point(
    entry_point: str,
    *,
    requested_status: LegacyEvidenceStatus = LegacyEvidenceStatus.LEGACY_UNPROVENANCED,
) -> None:
    if requested_status is not LegacyEvidenceStatus.LEGACY_UNPROVENANCED:
        raise LegacyEvidenceTransitionError(
            f"{entry_point} cannot produce evidence or change its "
            "LEGACY_UNPROVENANCED classification"
        )
    warnings.warn(
        LegacyUnprovenancedWarning(
            f"{entry_point} is a raw-frame compatibility API classified as "
            "LEGACY_UNPROVENANCED; it cannot produce E0-E8 evidence or "
            "REPRODUCED status"
        ),
        stacklevel=3,
    )


class QualityDimension(StrEnum):
    COMPLETENESS = "completeness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    CONSISTENCY = "consistency"


class RejectionReason(StrEnum):
    INVALID_BARCODE = "invalid_barcode"
    DUPLICATE_BARCODE = "duplicate_barcode"


@dataclass(frozen=True, slots=True)
class CleaningPolicy:
    barcode_column: str = "code"
    max_missing_ratio: float = 0.60
    minimum_barcode_length: int = 8
    maximum_barcode_length: int = 18

    def __post_init__(self) -> None:
        if not 0 <= self.max_missing_ratio <= 1:
            raise ValueError("max_missing_ratio must be between 0 and 1")
        if self.minimum_barcode_length < 1:
            raise ValueError("minimum_barcode_length must be positive")
        if self.minimum_barcode_length > self.maximum_barcode_length:
            raise ValueError("minimum_barcode_length cannot exceed maximum_barcode_length")


@dataclass(frozen=True, slots=True)
class CleaningReport:
    input_rows: int
    output_rows: int
    input_columns: int
    output_columns: int
    rejected_by_reason: Mapping[RejectionReason, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rejected_by_reason", MappingProxyType(dict(self.rejected_by_reason)))

    @property
    def rejected_rows(self) -> int:
        return self.input_rows - self.output_rows

    @property
    def duplicate_rows_removed(self) -> int:
        return self.rejected_by_reason.get(RejectionReason.DUPLICATE_BARCODE, 0)

    @property
    def retention_rate(self) -> float:
        return self.output_rows / self.input_rows if self.input_rows else 1.0
