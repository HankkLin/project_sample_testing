# Training-data inspection

Development data-inspection record for Part 1 Step 1. This is not Project Report prose. Inspected on 2026-10-28 (UTC); no model was trained and no observations were removed or modified.

## Dataset and the sixth column

`data/train_prices_decisions_2026.csv` contains **50,000 rows and 6 columns**. A row is one customer observation; a column is a field describing that observation.

The six columns are one customer identifier, three customer attributes, an offered price, and a purchase outcome. The additional field is **`user_index`**, the identifier. It is exactly the sequence 0 through 49,999 and should be excluded from the model's predictive features.

The four model inputs are `Covariate1`, `Covariate2`, `Covariate3`, and `price_item`. The target is `item_bought`.

## Column definitions and observed ranges

Types below are those inferred by `pandas.read_csv`. Minimum and maximum values describe this particular CSV; they are not legal price bounds or guarantees about future data. The data helper identifies `Covariate1` as binary but does not document real-world meanings or units for the three covariates. Do not assume they mean age, income, or another particular attribute.

| Column | Role | Loaded dtype | Observed minimum | Observed maximum | Unique values | Missing values |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `user_index` | Customer identifier; exclude from predictors | `int64` | 0 | 49,999 | 50,000 | 0 |
| `Covariate1` | Binary customer attribute; feature | `float64` | 0 | 1 | 2 | 0 |
| `Covariate2` | Numeric customer attribute; feature | `float64` | 0.0001547641640278 | 16.034335151736805 | 50,000 | 0 |
| `Covariate3` | Numeric customer attribute; feature | `float64` | 0.01 | 283.86587729122573 | 49,996 | 0 |
| `price_item` | Price offered to the customer; feature | `float64` | 0.01 | 599.8918752698108 | 49,537 | 0 |
| `item_bought` | Observed purchase decision; target | `bool` | `False` (0) | `True` (1) | 2 | 0 |

## Purchase target and binary attribute

`item_bought` is stored as Boolean `True`/`False`, not as numeric labels in the loaded CSV. For modeling, use **`True` = 1 = purchased** and **`False` = 0 = did not purchase**. The model should estimate the probability of the positive class (purchase = 1), rather than predict a private customer valuation.

| Purchase outcome | Numeric mapping | Count | Percentage |
| --- | ---: | ---: | ---: |
| `True`: purchased | 1 | 21,235 | 42.47% |
| `False`: did not purchase | 0 | 28,765 | 57.53% |
| Total | | 50,000 | 100.00% |

`Covariate1` is nearly balanced: 25,067 observations have value 1 (50.134%), and 24,933 have value 0 (49.866%). Although stored as floating-point values, its observed values are only 0.0 and 1.0.

## Numeric summaries

Values in this table are rounded to five decimal places for readability. Quartiles use pandas' default linear interpolation. Boolean target summaries use its 0/1 mapping for these calculations only.

| Column | Mean | 25th percentile | Median | 75th percentile |
| --- | ---: | ---: | ---: | ---: |
| `user_index` | 24999.50000 | 12499.75000 | 24999.50000 | 37499.25000 |
| `Covariate1` | 0.50134 | 0.00000 | 1.00000 | 1.00000 |
| `Covariate2` | 3.19746 | 1.26908 | 2.69447 | 4.60869 |
| `Covariate3` | 9.94752 | 5.57590 | 7.28461 | 10.35790 |
| `price_item` | 119.50833 | 41.02177 | 62.57092 | 106.33412 |
| `item_bought` (0/1) | 0.42470 | 0.00000 | 0.00000 | 1.00000 |

Identifier summaries are included for completeness, not because `user_index` is a useful model feature. The target mean, 0.42470, equals the overall purchase rate.

## Data-quality checks

| Check | Observed result |
| --- | --- |
| Missing values | 0 in every column |
| Positive or negative infinity | 0 in every numeric column |
| Exact duplicate rows across all six columns | 0 |
| Exact duplicate observations excluding `user_index` | 0 |
| Unique identifiers | 50,000; no repeated identifiers |
| Identifier sequence | Exactly 0 through 49,999, in order |
| Purchase target values | Only `True` and `False` |
| `Covariate1` values | Only 0.0 and 1.0 |

Repeated values within an individual feature are not duplicate rows. No values were dropped, imputed, clipped, or otherwise changed during inspection.

## Recommended next inspection

Plot the distributions of price and each covariate, then examine purchase rates by price bins and the binary attribute with bin counts. `Covariate3` and price have maxima well above their medians and upper quartiles; inspect these upper tails and data coverage before deciding on preprocessing. That observation alone does not justify deleting high values or defining a legal price range. Keep this inspection separate from training, held-out evaluation, and later price optimization.

## Reproducibility and sources

- Inspected file: `data/train_prices_decisions_2026.csv`.
- File size: 3,561,383 bytes.
- SHA256: `d85efca8dba15fe5cf0fa3f0514d51ec42d7e6eaa97507990789a7e25c950a69`.
- Inspection date: 2026-10-28 (UTC).
- Method: `pandas.read_csv`, inferred dtypes, nonmissing unique counts, per-column missing/nonfinite checks, numeric summaries, Boolean value counts, and exact duplicate-row checks both with and without the identifier.
- Column definitions: the supplied `data/data_helpers_2026.ipynb`. No hidden valuation files or simulator internals were inspected.

These statistics describe the identified file version. Recompute them if the CSV changes.
