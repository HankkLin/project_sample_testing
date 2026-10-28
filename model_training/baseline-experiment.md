# Starter baseline experiment record

Development experiment record for Part 1 Step 1, not Project Report content. Completed and verified 2026-10-28 (UTC).

## Status: completed

The original starter linear-regression baseline ran successfully in an isolated Python 3.13 environment. Its held-out **MSE/Brier score is 0.17095434766778153** (lower is better). This is a probability-error metric, not classification accuracy or pricing revenue.

The initial run completed at `2026-10-28T04:22:28.990169+00:00`. After the project was moved, the environment was recreated and the unchanged fitting cells were rerun at `2026-10-28T04:27:52.858992+00:00`. The rerun reproduced the same score and matched the preserved saved model's predictions exactly. This replaces the earlier pre-installation blocked status; the original result metadata was recovered rather than reconstructed from memory.

## Exact setup

| Setting | Executed baseline |
| --- | --- |
| Source | `model_training/purchase_model_baseline.ipynb`, unchanged |
| Input | `data/train_prices_decisions_2026.csv` |
| Dataset SHA256 | `d85efca8dba15fe5cf0fa3f0514d51ec42d7e6eaa97507990789a7e25c950a69` |
| Notebook SHA256 | `e67a186a93c0191e83cf80c4ba4a56b4ef5e8b5d823542a0096431d92670338c` |
| Rows | 50,000 |
| Feature order | `Covariate1`, `Covariate2`, `Covariate3`, `price_item` |
| Excluded identifier | `user_index` |
| Target | `item_bought.astype(float)`: purchase = 1, no purchase = 0 |
| Split | `train_test_split(data, test_size=.2, random_state=0)`; default shuffle, no stratification |
| Actual split sizes | 40,000 training; 10,000 held-out |
| Positive labels | 16,874 training; 4,361 held-out |
| Estimator | `sklearn.linear_model.LinearRegression()` |
| Estimator parameters | `copy_X=True`, `fit_intercept=True`, `n_jobs=None`, `positive=False` |
| Preprocessing | Select the four named columns; cast target to float; no scaling, imputation, feature engineering, or observation removal |
| Probability handling | `np.clip(model.predict(test[features]), 0, 1)` |
| Execution | Unchanged notebook code cells executed programmatically; notebook file and stored outputs were not rewritten |

Single-thread environment limits were set for numerical libraries. No simulator internals, hidden valuations, pricing optimization, logistic model, or report content were used.

## Measured held-out results

| Measurement | Result |
| --- | ---: |
| Clipped MSE / binary Brier score | 0.17095434766778153 |
| Minimum raw prediction | -0.5081228902227554 |
| Maximum raw prediction | 2.3513276968200336 |
| Predictions below 0, clipped to 0 | 1,020 / 10,000 (10.20%) |
| Predictions above 1, clipped to 1 | 53 / 10,000 (0.53%) |
| Maximum original versus reloaded raw-prediction difference | 0.0 |
| Maximum saved-model versus fresh-fit raw-prediction difference after relocation | 0.0 |
| Model fitting/loading warnings | None captured |

MSE is the mean of `(clipped predicted purchase probability - observed 0/1 purchase outcome)^2` over the 10,000 held-out rows. For binary outcomes this is the Brier score. The raw regression outputs are not constrained probabilities; clipping is necessary to reproduce this starter baseline's probability contract. This single fixed holdout is a comparison reference, not evidence of pricing performance or an estimate of uncertainty across splits.

## Saved artifact and reload checks

- Model: `agents/helper_files_here/purchase_model.pkl`.
- Size: 607 bytes.
- SHA256: `7cc9b32c072c0d2671cdfb1311c3b13d5d7b634a06c0473dc45104fb2e5d9562`.
- The original notebook saved and reloaded the model, then passed `np.testing.assert_allclose` on all held-out raw predictions.
- After relocation, a fresh process loaded the preserved artifact and reproduced the original split and fit. Saved and newly fitted predictions matched exactly; the first-five-row batch check also passed.
- The relocation check skipped the notebook's save cell to avoid replacing the existing artifact. Its bytes and the notebook's bytes were verified unchanged.
- Consumers should pass the four named feature columns to `predict()` and clip the resulting regression scores to [0, 1]. A later classifier would need a coordinated probability-interface change.
- Portable structured results, including initial and relocation verification timestamps, are in `model_training/baseline-results.json`.

## Environment verification

The active project environment is `.venv`, using isolated uv-managed **CPython 3.13.14**. System/default Python remains 3.14.6. The moved environment initially contained old absolute paths in several activation scripts and package launchers; it was preserved as an external backup and recreated in the new checkout. No stale old-checkout paths remained in the recreated scripts.

All 14 direct package pins match `requirements.txt` exactly:

| Package | Installed version |
| --- | --- |
| cryptography | 50.0.2 |
| matplotlib | 3.10.0 |
| numpy | 2.1.3 |
| pandas | 2.2.3 |
| scipy | 1.16.3 |
| seaborn | 0.13.2 |
| scikit-learn | 1.6.1 |
| xgboost | 3.4.1 |
| statsmodels | 0.15.0 |
| joblib | 1.6.0 |
| threadpoolctl | 3.7.0 |
| patsy | 1.0.3 |
| formulaic | 1.2.2 |
| narwhals | 2.26.0 |

`uv pip check --python .venv` passed for all 31 installed packages, including transitive dependencies. There were no direct-pin substitutions. During environment recreation, uv warned that cross-filesystem hardlinking was unavailable and copied package files instead; installation and compatibility checks still succeeded. This affects installation efficiency, not the reported model result. No Jupyter kernel package was needed for programmatic execution; interactive notebook kernel setup is a separate development convenience.

## Scope and next comparison

The baseline reference is now available. A later, separately authorized comparison can evaluate class-grounded logistic regression on the same held-out rows. Keep this score, original split, feature ordering, and clipping convention explicit when comparing models. No commits or pushes were made for this run.
