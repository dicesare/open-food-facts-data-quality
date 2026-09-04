import pandas as pd

from .domain import CleaningPolicy, CleaningReport, _warn_legacy_entry_point
from .pipeline import QualityPipeline


def missingness(data: pd.DataFrame) -> pd.Series:
    _warn_legacy_entry_point("missingness")
    return data.isna().mean().sort_values(ascending=False)


def clean_products(
    data: pd.DataFrame, max_missing: float = 0.60
) -> tuple[pd.DataFrame, CleaningReport]:
    _warn_legacy_entry_point("clean_products")
    return QualityPipeline(CleaningPolicy(max_missing_ratio=max_missing))._run(data)
