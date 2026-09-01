from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class CleaningReport:
    input_rows: int
    output_rows: int
    duplicate_rows_removed: int


def missingness(data: pd.DataFrame) -> pd.Series:
    return data.isna().mean().sort_values(ascending=False)


def clean_products(data: pd.DataFrame, max_missing: float = 0.60):
    if "code" not in data:
        raise ValueError("Missing required column: code")
    clean = data.copy()
    clean.columns = clean.columns.str.replace("-", "_", regex=False)
    keep = clean.columns[clean.isna().mean() <= max_missing]
    clean = clean.loc[:, keep]
    clean["code"] = clean["code"].astype("string").str.strip()
    clean = clean[clean["code"].str.fullmatch(r"\d{8,18}", na=False)]
    before = len(clean)
    clean = clean.drop_duplicates(subset=["code"], keep="first").reset_index(drop=True)
    report = CleaningReport(len(data), len(clean), before - len(clean))
    return clean, report
