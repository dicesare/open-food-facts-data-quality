# Historical experiment inventory

## Branches inspected

`master` contains the original `Projet_3.ipynb`. The 15-commit `dev` branch expands the work into the principal notebook, qualitative and quantitative studies, Plotly and Voilà variants, plus an unrelated course exercise that is excluded from the portfolio narrative.

| Notebook | Evidence retained |
|---|---|
| `Projet_3.ipynb` / `P3_01_notebook.ipynb` | end-to-end data preparation workflow |
| `p3_qual.ipynb` | categorical semantics, missingness combinations and field usability |
| `p3_quant.ipynb` | numeric profiling, barcode validation, outliers, correlation and imputation |
| `P3_01_plotly.ipynb` | interactive exploratory charts |
| `P3_01_voila.ipynb` | PCA and dashboard-oriented delivery |
| `cnam_tp.ipynb` | unrelated practice notebook, intentionally omitted |

## Verified scale

The quantitative notebook displays a source dataframe of **320,772 rows and 162 columns**. A missingness threshold and business relevance selection reduce the working representation to **36 columns**. The French subset used in the qualitative notebook contains approximately **98,468 rows**.

Examples of recorded missingness include about **31.0%** for French and UK nutrition-score columns in the full source. Within the French subset, 37,017 nutrition grades and nutrition scores and 33,841 energy values were missing in the displayed checkpoint.

The qualitative study also reports:

- 61,981 populated versus 36,487 missing `main_category_fr` values;
- 37,957 rows with both generic name and main category;
- 36,125 rows missing both fields;
- 24,024 rows with generic name but missing main category.

## Modern interpretation

The strongest current competencies demonstrated are schema discovery, missing-data mechanism analysis, domain validation, defensible feature selection, traceable destructive rules and separation of data-quality logic from presentation.

The public code deliberately does not reproduce the historical dataset or hard-code its snapshot. Reproduction requires documenting the Open Food Facts version, licence, extraction date and checksum.

