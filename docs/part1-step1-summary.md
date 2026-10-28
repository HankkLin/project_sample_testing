# Part 1 Step 1 development handoff

Updated 2026-10-28 (UTC). **Technical development documentation, not Project Report content.** This records implementation decisions and measured results for coding handoff; it must not be used as an LLM-written contribution to the Project Report. See [shared instructions](../AGENTS.md).

## Objective and completion state

The [assignment](https://docs.google.com/document/d/1MSqzgD7nfi8dm48dM6qNIZkDNmIZmcag6WWIjUcZ0O4), Step 1 (saved snapshot p. 3), requires estimating purchase probability from offered price and customer covariates, evaluating on held-out purchase decisions, saving a model under `agents/helper_files_here/`, and retaining training/preprocessing code under `model_training/`. Step 1 has no separately numerical turn-in score. See the [requirements and plan](part1-step1-plan.md).

**Completed:** data inspection, faithful starter linear baseline, a fixed logistic comparison, model selection, serialization, and final validation. The selected model is the plain main-effects logistic pipeline. Its output is `Pr(item_bought = 1 | price_item, Covariate1, Covariate2, Covariate3)`. No further models, interactions, tuning, or full-data refit were performed. The saved pipeline remains trained on 40,000 rows, preserving the evaluated 10,000-row holdout.

Static-price optimization/CSV submission is Part 1 Step 2; inventory-constrained pricing is Step 3. Neither was implemented here. Existing pricing agents still load the preserved linear model; logistic integration remains a separate interface change.

## Data inspection

`data/train_prices_decisions_2026.csv` contains **50,000 rows and six columns**:

| Field | Use | Observations |
| --- | --- | --- |
| `user_index` | Identifier; excluded from predictors | Unique sequence 0-49,999 |
| `Covariate1` | Binary feature | Values 0/1; 24,933 zeros and 25,067 ones |
| `Covariate2` | Numeric feature | Observed range 0.0001547641640278-16.034335151736805 |
| `Covariate3` | Numeric feature | Observed range 0.01-283.86587729122573 |
| `price_item` | Offered-price feature | Observed range 0.01-599.8918752698108 |
| `item_bought` | Target | `True` = purchase = 1; `False` = no purchase = 0 |

There are 21,235 purchases (42.47%) and 28,765 non-purchases (57.53%). No missing or infinite values, repeated identifiers, or duplicate observations were found, including when excluding the identifier. No observations were removed or modified. The covariates' real-world meanings/units are undocumented; observed price ranges are not legal price bounds. Full dtypes, unique counts, means, quartiles, and checks are in [data inspection](data-inspection.md).

## Decisions and rationale

| Decision | Technical reason | Basis |
| --- | --- | --- |
| Reproduce the supplied linear model first | Establish a reference before changing the model | Starter notebook |
| Keep the exact split, feature order, and held-out rows | Make the comparison directly comparable | Engineering choice |
| Estimate purchase probability with logistic regression | Match a binary purchase target and produce bounded probabilities | [Lecture 7 pp. 26-27](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture7_AlgorithmicPricing_Intro.pdf#page=26) |
| Start with main effects only | Keep the selected comparison simple and understandable | Engineering choice; lecture also permits interactions |
| Fit standardization only on training rows | Scale inputs without leaking holdout information | Engineering choice |
| Serialize preprocessing and classifier together | Reproduce training-time transformations at inference | Engineering choice |
| Evaluate probability error and calibration, plus fixed-threshold accuracy | A model can classify well while assigning imperfect probabilities | Engineering choice |
| Preserve the linear model and agent interfaces | Keep a valid reference and avoid substituting class labels for probabilities | Existing code contract |

Lecture 7 pp. 23-25 grounds learning in observed offers and purchase decisions rather than private valuations; p. 28 cautions about historical price coverage. The model choices and diagnostics above are not assignment-mandated algorithms. No hidden valuation data or simulator internals were accessed. See [course source mapping](course-knowledge.md).

## Reproducibility

- Features, in order: `Covariate1`, `Covariate2`, `Covariate3`, `price_item`; target mapped to 0/1.
- Split: `train_test_split(data, test_size=.2, random_state=0)`, shuffle enabled, no stratification. Actual sizes: **40,000 train / 10,000 held-out**. Heldout contains 4,361 purchases and 5,639 non-purchases.
- Both models use the same held-out IDs in the same order, verified independently. ID hash and encoding are recorded in [comparison metadata](../model_training/logistic-comparison-results.json).
- Linear baseline: default `LinearRegression()`, no scaling/imputation/feature construction; clip raw predictions to [0, 1].
- Logistic: `StandardScaler` plus `LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=1000, tol=1e-4, random_state=0)`. No interactions, tuning, threshold search, or calibration fitting. Training completed in 12 iterations.
- Environment: isolated `.venv`, Python 3.13.14; all direct pins match `requirements.txt`. Core versions: NumPy 2.1.3, pandas 2.2.3, SciPy 1.16.3, scikit-learn 1.6.1. All 31 installed packages passed compatibility checks. Numerical-library threads limited to one; default system Python was not changed.
- Dataset SHA256: `d85efca8dba15fe5cf0fa3f0514d51ec42d7e6eaa97507990789a7e25c950a69`.
- Selected pipeline SHA256: `98e2b1258fe91986bf3f56835f6a124a4bbfd5af9fcb3160aa5241f418f5f673`.

## Results on the same held-out customers

| Measurement | Clipped linear | Selected logistic |
| --- | ---: | ---: |
| Brier/MSE (lower better) | 0.17095434766778153 | 0.08999814363564312 |
| Log loss (lower better) | 0.531820228556283 | 0.37616485566335417 |
| Calibration error, 10 equal-width bins | 0.11860811267160698 | 0.08564036335609597 |
| Correct buy/no-buy predictions | 7,573 / 10,000 | 8,931 / 10,000 |
| Accuracy at probability >= 0.5 | 75.73% | 89.31% |

Logistic reduces Brier error by **47.36%** and adds **1,358 correct classifications**, a **13.58 percentage-point accuracy gain**. Always predicting no purchase would achieve 56.39% accuracy on this holdout. Accuracy uses a fixed reporting threshold, not a tuned decision rule; it is distinct from the probability-estimation objective. Brier score is mean squared probability error against observed 0/1 purchases. For log loss only, probabilities are clipped to `[1e-15, 1-1e-15]` for numerical safety. The linear baseline also needs its ordinary [0, 1] probability clipping: 1,020 raw held-out predictions were below 0 and 53 above 1.

| Classification outcome | Linear | Logistic |
| --- | ---: | ---: |
| True positive / true negative | 3,243 / 4,330 | 3,881 / 5,050 |
| False positive / false negative | 1,309 / 1,118 | 589 / 480 |
| Buy precision / recall | 71.24% / 74.36% | 86.82% / 88.99% |

## Artifacts and how to verify them

| Purpose | Files |
| --- | --- |
| Planning and data facts | [Plan](part1-step1-plan.md), [data inspection](data-inspection.md) |
| Baseline provenance | [Experiment](../model_training/baseline-experiment.md), [metadata](../model_training/baseline-results.json), [original notebook](../model_training/purchase_model_baseline.ipynb) |
| Comparison implementation and record | [Training script](../model_training/compare_logistic.py), [experiment](../model_training/logistic-experiment.md), [results](../model_training/logistic-comparison-results.json) |
| Frozen prediction diagnostics | [IDs, labels, probabilities](../model_training/logistic-heldout-predictions.csv), [calibration bins](../model_training/logistic-calibration.csv) |
| Saved models | [Selected logistic pipeline](../agents/helper_files_here/purchase_model_logistic.pkl), [preserved linear baseline](../agents/helper_files_here/purchase_model.pkl) |
| Final validation | [Validator](../model_training/validate_purchase_model.py), [validation results](../model_training/logistic-final-validation.json) |

From the repository root, with the existing environment, validate the saved artifacts without fitting anything:

```powershell
uv pip check --python .venv
.\.venv\Scripts\python.exe model_training\validate_purchase_model.py
```

The validator resolves inputs from its own location, so it was also verified from outside the checkout. It rewrites `model_training/logistic-final-validation.json` with the latest timestamp and check results; review that generated change before committing. It does not refit models or overwrite their pickle files. Load only trusted pickle artifacts.

For a deliberate training reproduction, the unchanged baseline is in the linked notebook; it saves `purchase_model.pkl`, so preserve the existing artifact before executing its save cell. The logistic comparison command is:

```powershell
.\.venv\Scripts\python.exe model_training\compare_logistic.py
```

The comparison deliberately refuses to overwrite its four existing outputs: logistic pickle, comparison JSON, held-out prediction CSV, and calibration CSV. Reproduce in a separate scratch copy, preserving/renaming those generated artifacts first; keep the baseline model and metadata available because the script verifies them. No training reproduction is needed merely to use or validate the frozen pipeline. Fresh-machine environment setup is in the [README](../README.md).

## Final validation, limitations, and handoff

Final checks passed in a fresh process: exact hashes and held-out IDs/labels; training-only scaler count/means/variances; four-feature schema; positive-class extraction; finite bounded probabilities; independent reload equality; batch/single-row consistency; recomputed Brier/log-loss/accuracy; all calibration bins; dependency pins; and preserved baseline/notebook. Maximum reload prediction difference was **0.0**.

Calibration is improved but imperfect. For example, the logistic [0.3, 0.4) bin averages 35.12% predicted purchases versus 15.86% observed, while [0.7, 0.8) averages 75.12% predicted versus 92.53% observed. The calibration error is bin-dependent. This is one already-inspected holdout, without uncertainty estimates across splits or evidence of pricing revenue. Future observations outside historical support need caution.

The only captured training warning is a nonblocking SciPy deprecation of L-BFGS-B `disp`/`iprint` options; no convergence warning occurred and pins were not changed. Course PDFs and environments remain local and ignored by public Git.

**Remaining integration contract:** the selected logistic pipeline returns probabilities through `predict_proba(features)[:, index_of_class_1]`; `predict()` returns class labels. Current `agents/agent_part1.py` and `agents/agent_part2.py` still load the linear baseline and have not been switched. Their later integration must explicitly adopt the probability contract. Step 1 evaluation and saving are complete; this handoff does not claim Step 2 pricing, Step 3 capacity control, or submission compatibility is complete.
