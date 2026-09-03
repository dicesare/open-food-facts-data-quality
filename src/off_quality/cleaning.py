import pandas as pd

from .domain import CleaningPolicy, CleaningReport
from .pipeline import QualityPipeline


def missingness(data: pd.DataFrame) -> pd.Series:
    return data.isna().mean().sort_values(ascending=False)


def clean_products(
    data: pd.DataFrame, max_missing: float = 0.60
) -> tuple[pd.DataFrame, CleaningReport]:
    return QualityPipeline(CleaningPolicy(max_missing_ratio=max_missing)).run(data)
