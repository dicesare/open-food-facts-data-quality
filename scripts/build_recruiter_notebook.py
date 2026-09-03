"""Build the executed recruiter-facing P3 notebook deterministically."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "00_recruiter_case_study.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


def build_notebook():
    cells = [
        markdown(
            """
# Open Food Facts — from exploratory analysis to an auditable data-quality pipeline

**Recruiter path · 8–10 minutes.** This notebook connects the original 2022 study
(320,772 products and 162 variables) to its current software-engineering redesign.
The full historical notebooks remain available in `notebooks/historical/`.
"""
        ),
        markdown(
            """
## Business question

Can an open, sparse and contributor-maintained food database be transformed into a
defensible analytical dataset without hiding the impact of cleaning decisions?

The answer requires four distinct quality dimensions: **completeness, validity,
uniqueness and consistency**. A row is never removed silently; every rejection is
reported with a stable business reason.
"""
        ),
        code(
            """
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from off_quality import (
    ColumnImputer,
    DataProfiler,
    ImputationMethod,
    QualityPipeline,
)

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
SAMPLE = ROOT / "data" / "sample" / "products.csv"
"""
        ),
        markdown(
            """
## 1. Scale and decisions evidenced by the historical run

These figures come from the preserved executed notebooks. They are not recomputed
from the small deterministic fixture used later for CI.
"""
        ),
        code(
            """
historical_funnel = pd.DataFrame(
    {
        "stage": ["source snapshot", "decision-relevant variables", "French subset"],
        "rows": [320_772, 320_772, 98_468],
        "columns": [162, 36, 36],
    }
)
historical_funnel
"""
        ),
        code(
            """
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
historical_funnel.plot.bar(x="stage", y="rows", legend=False, ax=axes[0], color="#2563eb")
historical_funnel.plot.bar(x="stage", y="columns", legend=False, ax=axes[1], color="#0f766e")
axes[0].set(title="Rows retained by analytical scope", ylabel="products")
axes[1].set(title="Variables retained after relevance/missingness review", ylabel="columns")
for axis in axes:
    axis.tick_params(axis="x", rotation=20)
plt.tight_layout()
"""
        ),
        markdown(
            """
The reduction from 162 to 36 variables is a **feature-governance decision**, not a
claim that sparse columns are intrinsically useless. Thresholds alter the represented
population and therefore belong in a validated policy object and in the audit report.
"""
        ),
        markdown(
            """
## 2. Deterministic executable contract

The repository does not redistribute the full dataset. This versioned fixture contains
duplicates, invalid identifiers, missing values and an implausible numeric value. It
tests behaviour; it is **not** used to manufacture portfolio findings.
"""
        ),
        code("raw = pd.read_csv(SAMPLE, dtype={\"code\": \"string\"})\nraw"),
        code(
            """
before = DataProfiler().profile(raw)
pd.DataFrame(
    {
        "dimension": [metric.dimension.value for metric in before.scorecard],
        "score": [metric.score for metric in before.scorecard],
        "evidence": [f"{metric.numerator}/{metric.denominator}" for metric in before.scorecard],
    }
)
"""
        ),
        markdown(
            """
## 3. Composable cleaning strategies

`QualityPipeline` depends on a `FrameRule` protocol. Normalisation, sparse-column
selection, barcode validation and deduplication are independent strategies. New domain
rules can therefore be added without modifying the orchestrator (Open/Closed and
Dependency Inversion principles).
"""
        ),
        code("clean, report = QualityPipeline().run(raw)\nreport"),
        code(
            """
pd.DataFrame(
    {
        "reason": [reason.value for reason in report.rejected_by_reason],
        "rows": list(report.rejected_by_reason.values()),
    }
)
"""
        ),
        markdown(
            """
The intentionally implausible energy value remains visible: format validation and
domain plausibility are separate concerns. Automatically deleting it would conceal a
business decision that needs domain agreement.
"""
        ),
        code(
            """
missing = pd.DataFrame(
    {
        "before": raw.isna().mean(),
        "after": clean.isna().mean(),
    }
).sort_values("before", ascending=False)
missing.head(8).plot.barh(figsize=(8, 4), title="Missingness before and after structural cleaning")
plt.xlabel("missing ratio")
plt.tight_layout()
"""
        ),
        markdown(
            """
## 4. Leakage-aware imputation

Imputation is fitted on a training partition and only then applied to unseen rows.
The held-out value cannot influence the learned median. This corrects a common weakness
of exploratory notebooks while preserving the original investigation of imputation.
"""
        ),
        code(
            """
training = clean.iloc[:-2].copy()
holdout = clean.iloc[-2:].copy()
imputer = ColumnImputer(("energy_100g", "sugars_100g"), ImputationMethod.MEDIAN)
fitted = imputer.fit(training)
comparison = holdout[["code", "energy_100g", "sugars_100g"]].copy()
transformed = fitted.transform(holdout)
comparison[["energy_imputed", "sugars_imputed"]] = transformed[["energy_100g", "sugars_100g"]]
comparison
"""
        ),
        markdown(
            """
## 5. What this proves — and what it does not

**Demonstrated:** wide-table profiling, qualitative and quantitative auditing,
categorical exploration, missing-data reasoning, iterative experimentation, PCA,
interactive visualisation, and a modern typed implementation with immutable reports,
strategies, streaming support and tests.

**Not claimed:** medical validity, causal nutritional conclusions, or generalisation
from the CI fixture. Historical outputs describe a dated snapshot; current Open Food
Facts data may differ.
"""
        ),
        markdown(
            """
## Deep-dive map

- `historical/P3_01_notebook.ipynb` — full end-to-end study;
- `historical/p3_quant.ipynb` — quantitative profiling, outliers, correlations and PCA;
- `historical/p3_qual.ipynb` — categorical semantics and text exploration;
- `historical/P3_01_plotly.ipynb` — interactive visual experiments;
- `historical/P3_01_voila.ipynb` — dashboard delivery experiment;
- `src/off_quality/` — maintained typed implementation;
- `tests/` — executable behavioural evidence.
"""
        ),
    ]
    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    return notebook


def main() -> None:
    notebook = build_notebook()
    client = NotebookClient(notebook, timeout=120, kernel_name="python3", resources={"metadata": {"path": ROOT}})
    client.execute()
    nbf.write(notebook, OUTPUT)


if __name__ == "__main__":
    main()
