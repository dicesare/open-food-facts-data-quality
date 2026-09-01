# Open Food Facts — Data Quality Pipeline

A reproducible data-cleaning case study built on the public Open Food Facts dataset. It demonstrates schema validation, missing-value analysis, duplicate handling and defensible filtering rules on real-world product data.

## What this project demonstrates

- profiling a wide, sparse dataset;
- separating reusable cleaning logic from notebook exploration;
- detecting invalid barcodes and duplicate products;
- documenting every row-removal rule;
- testing transformations on synthetic fixtures;
- avoiding redistribution of the large raw dataset.

## Quick start

```bash
python -m venv .venv
pip install -e .[dev]
pytest
jupyter lab notebooks/open_food_facts_quality.ipynb
```

Place a legally obtained Open Food Facts CSV in `data/raw/`; this directory is ignored by Git. The notebook deliberately contains no local absolute path or embedded data.

## Case-study gallery

The original `master` notebook and six `dev` experiments are represented by five complementary views:

| Study | Focus |
|---|---|
| [01 — Qualitative audit](notebooks/01_qualitative_audit.ipynb) | semantics, units, categories and suspicious values |
| [02 — Quantitative profile](notebooks/02_quantitative_profile.ipynb) | missingness, distributions, cardinality and correlations |
| [03 — Cleaning decisions](notebooks/03_cleaning_decisions.ipynb) | traceable rules and before/after impact |
| [04 — Quality scorecard](notebooks/04_quality_scorecard.ipynb) | completeness, validity, uniqueness and consistency |
| [05 — Interactive delivery](notebooks/05_interactive_delivery.ipynb) | Plotly/Voilà design translated into a lightweight reporting contract |
| [End-to-end pipeline](notebooks/open_food_facts_quality.ipynb) | executable synthetic example |

The unrelated course-practice notebook is not presented as project evidence; the public story stays focused on health-data preparation.

## Architecture

```text
src/off_quality/       validation and cleaning functions
notebooks/             concise narrative analysis
tests/                 synthetic, deterministic fixtures
data/README.md         data provenance instructions
```

## Responsible use

Cleaning thresholds change the population represented by the dataset. The notebook reports before/after row counts and treats nutrition analysis as exploratory, not medical advice.

## License

Code is released under the [MIT License](LICENSE). Open Food Facts data remains governed by its own terms and is not redistributed here.

