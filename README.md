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
