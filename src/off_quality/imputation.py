"""Leakage-aware imputation strategies with explicit fit/transform phases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

import pandas as pd


class ImputationMethod(StrEnum):
    MEDIAN = "median"
    MEAN = "mean"
    MOST_FREQUENT = "most_frequent"
    CONSTANT = "constant"


class FittedImputer(Protocol):
    def transform(self, frame: pd.DataFrame) -> pd.DataFrame: ...


class Imputer(Protocol):
    def fit(self, frame: pd.DataFrame) -> FittedImputer: ...


@dataclass(frozen=True, slots=True)
class FittedColumnImputer:
    """Immutable learned state; values must originate from the training split."""

    fill_values: dict[str, object]

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        unknown = set(self.fill_values).difference(frame.columns)
        if unknown:
            raise ValueError(f"Missing columns required by imputer: {sorted(unknown)}")
        return frame.fillna(self.fill_values)


@dataclass(frozen=True, slots=True)
class ColumnImputer:
    columns: tuple[str, ...]
    method: ImputationMethod
    constant: object = "unknown"

    def fit(self, frame: pd.DataFrame) -> FittedColumnImputer:
        missing = set(self.columns).difference(frame.columns)
        if missing:
            raise ValueError(f"Cannot fit imputer; missing columns: {sorted(missing)}")
        values: dict[str, object] = {}
        for column in self.columns:
            series = frame[column]
            if self.method is ImputationMethod.MEDIAN:
                values[column] = series.median()
            elif self.method is ImputationMethod.MEAN:
                values[column] = series.mean()
            elif self.method is ImputationMethod.MOST_FREQUENT:
                modes = series.mode(dropna=True)
                if modes.empty:
                    raise ValueError(f"Cannot infer a mode for empty column: {column}")
                values[column] = modes.iloc[0]
            else:
                values[column] = self.constant
        return FittedColumnImputer(values)

