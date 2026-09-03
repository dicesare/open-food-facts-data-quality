"""Typed profiling and quality-scorecard services."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .domain import QualityDimension


@dataclass(frozen=True, slots=True)
class ColumnProfile:
    name: str
    dtype: str
    rows: int
    missing: int
    distinct: int

    @property
    def missing_ratio(self) -> float:
        return self.missing / self.rows if self.rows else 0.0

    @property
    def distinct_ratio(self) -> float:
        return self.distinct / self.rows if self.rows else 0.0


@dataclass(frozen=True, slots=True)
class QualityMetric:
    dimension: QualityDimension
    score: float
    numerator: int
    denominator: int


@dataclass(frozen=True, slots=True)
class DatasetProfile:
    rows: int
    columns: tuple[ColumnProfile, ...]
    scorecard: tuple[QualityMetric, ...]


class DataProfiler:
    """Single-purpose service producing immutable aggregate evidence."""

    def profile(self, frame: pd.DataFrame, key: str = "code") -> DatasetProfile:
        rows = len(frame)
        columns = tuple(
            ColumnProfile(
                name=str(column),
                dtype=str(frame[column].dtype),
                rows=rows,
                missing=int(frame[column].isna().sum()),
                distinct=int(frame[column].nunique(dropna=True)),
            )
            for column in frame.columns
        )
        cells = rows * len(frame.columns)
        present = cells - int(frame.isna().sum().sum())
        key_present = int(frame[key].notna().sum()) if key in frame else 0
        unique_keys = int(frame[key].nunique(dropna=True)) if key in frame else 0
        return DatasetProfile(
            rows=rows,
            columns=columns,
            scorecard=(
                self._metric(QualityDimension.COMPLETENESS, present, cells),
                self._metric(QualityDimension.UNIQUENESS, unique_keys, key_present),
            ),
        )

    @staticmethod
    def _metric(dimension: QualityDimension, numerator: int, denominator: int) -> QualityMetric:
        score = numerator / denominator if denominator else 1.0
        return QualityMetric(dimension, score, numerator, denominator)
