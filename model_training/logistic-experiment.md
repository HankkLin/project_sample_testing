# Logistic purchase-probability comparison

Development experiment record for Part 1 Step 1, not Project Report content. Run on 2026-10-28 (UTC). The current plain logistic pipeline is the selected Step 1 model. No additional models, interactions, or tuning are planned in this completion scope.

## Question and class connection

Does logistic regression estimate purchase probabilities more accurately than the starter's clipped linear regression on the **same held-out customers**?

[Lecture 7, PDF pp. 26-27](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture7_AlgorithmicPricing_Intro.pdf#page=26) explicitly suggests a logistic purchase model whose target is the purchase decision and whose inputs include offered price, customer covariates, and possible interactions. Pages 23-25 discuss observing offered prices and purchase decisions rather than valuations; p. 28 cautions about historical price coverage. Full course slides remain local, not in public Git.

This first comparison uses only the four main effects. Interactions are a possible class-taught extension, not a requirement or an implemented feature here. Train-only standardization, L2 regularization, exact solver settings, Brier/log-loss evaluation, and calibration bins are engineering choices, not claimed assignment mandates or lecture-specific prescriptions.

## Reproducible setup

- Script: `model_training/compare_logistic.py`; run with `.venv/Scripts/python.exe model_training/compare_logistic.py` on Windows. The script resolves paths from its own location and refuses to overwrite existing comparison outputs. Preserve existing outputs before a deliberate rerun.
- Data: only `data/train_prices_decisions_2026.csv`, SHA256 `d85efca8dba15fe5cf0fa3f0514d51ec42d7e6eaa97507990789a7e25c950a69`.
- Ordered inputs: `Covariate1`, `Covariate2`, `Covariate3`, `price_item`. Exclude identifier `user_index`.
- Target: `item_bought`, mapped to purchase = 1 and no purchase = 0.
- Original split: `train_test_split(data, test_size=.2, random_state=0)`, default shuffle, no stratification. Exactly 40,000 training rows and 10,000 held-out rows; 4,361 held-out purchases (43.61%).
- Held-out row membership and order independently checked against a split of the original row indices; both models use those same rows. Their IDs, labels, and probabilities are in `model_training/logistic-heldout-predictions.csv`.
- Ordered held-out ID SHA256: `e0442da3f9da1de1c8ee99677506a6b953eaa319709001b736dc0c2ebc03ad79`, computed from UTF-8 integer `user_index` followed by LF for each held-out row, in order.
- Logistic pipeline: `StandardScaler` followed by `LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=1000, tol=1e-4, random_state=0)`; remaining parameters use installed-library defaults recorded in the results JSON. Scaler and classifier are fitted on training rows only and serialized together. No transformations use held-out labels.
- Settings fixed before evaluating the holdout; no search, tuning, interaction selection, or calibration fitting on held-out data.
- Environment: Python 3.13.14, NumPy 2.1.3, pandas 2.2.3, SciPy 1.16.3, scikit-learn 1.6.1; existing approved environment, no new dependencies. Numerical-library thread counts limited to one.

The preserved linear model was reloaded, and a fresh starter-equivalent linear fit reproduced its held-out predictions. Its artifact was not overwritten. No simulator internals or hidden valuations were read.

## Measured comparison

All three error metrics below are better when lower. Values are rounded here; the JSON contains full precision.

| Held-out measurement | Clipped linear baseline | Logistic, main effects |
| --- | ---: | ---: |
| Brier score / MSE | 0.1709543477 | 0.0899981436 |
| Log loss | 0.5318202286 | 0.3761648557 |
| Expected calibration error, 10 fixed bins | 0.1186081127 | 0.0856403634 |
| Mean predicted purchase probability | 0.4396710148 | 0.4271204901 |
| Observed purchase rate | 0.4361000000 | 0.4361000000 |
| Minimum predicted probability | 0.0 | 1.1393304843244519e-15 |
| Maximum predicted probability | 1.0 | 0.9999999999999998 |

Logistic regression reduced Brier score by approximately **47.36%** on this fixed holdout and also reduced log loss. These measure probability error, not classification accuracy or pricing revenue. Linear predictions retain the starter's clipping to [0, 1]; logistic probabilities come directly from the positive-class column of `predict_proba`. For log loss only, both sets of probabilities are numerically clipped to `[1e-15, 1 - 1e-15]` to avoid logarithms of zero. This convention matters when interpreting clipped-linear log loss.

Brier score is the mean squared difference between purchase probability and observed 0/1 outcome. Log loss penalizes confident wrong predictions. Calibration error is the sample-count-weighted absolute difference between average predicted probability and actual purchase rate in 10 fixed equal-width bins; it depends on this bin choice and is not a guarantee of calibration.

## Buy/no-buy accuracy at a fixed threshold

For reporting only, probability >= 0.5 means buy; the threshold was not tuned. On the same 10,000 held-out rows, clipped linear regression classifies 7,573 correctly (75.73%) and logistic regression classifies 8,931 correctly (89.31%): 1,358 additional correct predictions, +13.58 percentage points, or 17.93% relative accuracy improvement. Classification errors fall from 2,427 to 1,069 (55.95% fewer). Always predicting no purchase achieves 56.39% on this holdout.

| Outcome | Clipped linear | Logistic |
| --- | ---: | ---: |
| True positive: correctly predicted buy | 3,243 | 3,881 |
| True negative: correctly predicted no buy | 4,330 | 5,050 |
| False positive: predicted buy, actual no buy | 1,309 | 589 |
| False negative: predicted no buy, actual buy | 1,118 | 480 |
| Buy precision | 71.24% | 86.82% |
| Buy recall | 74.36% | 88.99% |

Probability estimation remains the Step 1 objective; threshold accuracy does not replace the Brier, log-loss, or calibration checks.

## Calibration diagnostics

Logistic results by predicted-probability bin:

| Probability bin | Customers | Mean prediction | Actual purchase rate |
| --- | ---: | ---: | ---: |
| [0.0, 0.1) | 3,008 | 0.01488 | 0.03690 |
| [0.1, 0.2) | 681 | 0.14810 | 0.05727 |
| [0.2, 0.3) | 623 | 0.24981 | 0.07705 |
| [0.3, 0.4) | 637 | 0.35123 | 0.15856 |
| [0.4, 0.5) | 581 | 0.44978 | 0.31153 |
| [0.5, 0.6) | 696 | 0.54851 | 0.53305 |
| [0.6, 0.7) | 721 | 0.65109 | 0.76006 |
| [0.7, 0.8) | 857 | 0.75118 | 0.92532 |
| [0.8, 0.9) | 992 | 0.84988 | 0.98387 |
| [0.9, 1.0] | 1,204 | 0.95256 | 0.99086 |

Probability error improves, but material calibration gaps remain. For example, the [0.3, 0.4) bin predicts 35.12% purchases while observing 15.86%, and the [0.7, 0.8) bin predicts 75.12% while observing 92.53%. Both models' full bin counts, means, rates, and absolute gaps are in `model_training/logistic-calibration.csv`. No post-hoc calibrator was fitted.

## Saved artifacts and checks

- New pipeline: `agents/helper_files_here/purchase_model_logistic.pkl`, SHA256 `98e2b1258fe91986bf3f56835f6a124a4bbfd5af9fcb3160aa5241f418f5f673`.
- Results: `model_training/logistic-comparison-results.json`.
- Held-out IDs and predictions: `model_training/logistic-heldout-predictions.csv`.
- Calibration diagnostics: `model_training/logistic-calibration.csv`.
- Existing linear model preserved: `agents/helper_files_here/purchase_model.pkl`, SHA256 `7cc9b32c072c0d2671cdfb1311c3b13d5d7b634a06c0473dc45104fb2e5d9562`.

Checks passed for exact held-out row IDs/labels, scaler training means, finite probabilities within [0, 1], model save/reload agreement (maximum difference 0.0), single-row versus batch prediction, independent fresh-process reloading and metric recomputation, and preservation of the linear artifact. The optimizer completed in 12 iterations with no convergence warning.

One dependency deprecation warning was captured: SciPy says L-BFGS-B's `disp` and `iprint` options will be removed in SciPy 1.18.0. It did not prevent fitting or verification; no package pins were changed to suppress it.

## Limits and integration

This is one pre-specified main-effects logistic comparison on the original holdout, without uncertainty estimates across splits or evidence about pricing revenue. Further tuning or feature selection should use training-only cross-validation or a separate validation split; do not repeatedly optimize against this observed holdout. Historical price ranges are observations, not legal action bounds or proof of reliable extrapolation.

No pricing-agent code or prediction interface was changed. Existing agents still load the linear baseline and call its `predict()` method. The logistic pipeline must use `predict_proba` and the column for class 1; its `predict()` method returns class labels. Do not replace the baseline artifact or switch agents without a separate reviewed integration change. No pricing optimization or Project Report content was implemented. Publication and final validation are recorded in Git history and the final validation record.
