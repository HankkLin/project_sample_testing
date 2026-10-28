"""Compare a pre-specified logistic model with the unchanged saved linear baseline.

Run from any directory with the project's Python 3.13 environment. No hidden
valuation data or pricing-agent interfaces are used. Existing outputs are preserved.
"""
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import os
import pickle
import warnings
from datetime import datetime, timezone

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["Covariate1", "Covariate2", "Covariate3", "price_item"]
EPSILON = 1e-15


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive_probability(model, features):
    """Select purchase-class probabilities explicitly; predict() returns labels."""
    positive = np.flatnonzero(model.classes_ == 1)
    if len(positive) != 1:
        raise ValueError("Expected exactly one positive purchase class")
    return model.predict_proba(features)[:, positive[0]]


def calibration_rows(name, probability, outcome):
    # Fixed equal-width bins, including p=1 in the final bin. No refitting.
    bins = np.minimum((probability * 10).astype(int), 9)
    rows = []
    for index in range(10):
        mask = bins == index
        rows.append({
            "model": name, "bin_lower": index / 10, "bin_upper": (index + 1) / 10,
            "count": int(mask.sum()),
            "mean_probability": float(probability[mask].mean()) if mask.any() else None,
            "purchase_rate": float(outcome[mask].mean()) if mask.any() else None,
            "absolute_gap": float(abs(probability[mask].mean() - outcome[mask].mean())) if mask.any() else None,
        })
    return rows


def main():
    data_path = ROOT / "data/train_prices_decisions_2026.csv"
    baseline_path = ROOT / "agents/helper_files_here/purchase_model.pkl"
    prior = json.loads((ROOT / "model_training/baseline-results.json").read_text())
    assert sha256(data_path) == prior["dataset_sha256"]
    baseline_hash = sha256(baseline_path)
    assert baseline_hash == prior["artifact_sha256"]
    paths = {
        "model": ROOT / "agents/helper_files_here/purchase_model_logistic.pkl",
        "results": ROOT / "model_training/logistic-comparison-results.json",
        "predictions": ROOT / "model_training/logistic-heldout-predictions.csv",
        "calibration": ROOT / "model_training/logistic-calibration.csv",
    }
    for path in paths.values():
        if path.exists():
            raise FileExistsError(f"Preserving existing output: {path.name}")
    data = pd.read_csv(data_path)
    # Exactly the starter's row ordering, split parameters, and target mapping.
    train, test = train_test_split(data, test_size=.2, random_state=0)
    assert (len(train), len(test)) == (40000, 10000)
    y_train = train.item_bought.astype(int)
    y_test = test.item_bought.astype(int).to_numpy()
    # Independently reproduce starter row membership and preserved-model predictions.
    _, heldout_indices = train_test_split(np.arange(len(data)), test_size=.2, random_state=0)
    np.testing.assert_array_equal(test.index.to_numpy(), heldout_indices)
    with baseline_path.open("rb") as stream:
        baseline = pickle.load(stream)
    fresh = LinearRegression().fit(train[FEATURES], train.item_bought.astype(float))
    linear_raw = baseline.predict(test[FEATURES])
    np.testing.assert_allclose(linear_raw, fresh.predict(test[FEATURES]))
    linear_probability = np.clip(linear_raw, 0, 1)
    assert float(np.mean((linear_probability - y_test) ** 2)) == prior["clipped_mse_brier"]

    # Pre-specified first comparison: main effects only, no interactions or tuning.
    # Lecture 7 pp. 26-27 motivates logistic purchase probabilities with price and
    # covariates; scaling, regularization and diagnostic choices are engineering.
    logistic = Pipeline([
        ("scale", StandardScaler()),
        ("logistic", LogisticRegression(C=1.0, penalty="l2", solver="lbfgs",
                                        max_iter=1000, tol=1e-4, random_state=0)),
    ])
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        logistic.fit(train[FEATURES], y_train)
    np.testing.assert_allclose(logistic.named_steps["scale"].mean_, train[FEATURES].mean())
    probability = positive_probability(logistic, test[FEATURES])
    assert np.isfinite(probability).all() and ((probability >= 0) & (probability <= 1)).all()
    with paths["model"].open("wb") as stream:
        pickle.dump(logistic, stream)
    with paths["model"].open("rb") as stream:
        loaded = pickle.load(stream)
    reloaded = positive_probability(loaded, test[FEATURES])
    np.testing.assert_allclose(probability, reloaded)
    np.testing.assert_allclose(positive_probability(loaded, test[FEATURES].iloc[:1]), probability[:1])
    calibration = []
    metrics = {}
    for name, prediction in [("clipped_linear", linear_probability), ("logistic_main_effects", probability)]:
        rows = calibration_rows(name, prediction, y_test)
        calibration.extend(rows)
        metrics[name] = {
            "brier_mse": float(brier_score_loss(y_test, prediction)),
            "accuracy_at_0_5": float(np.mean((prediction >= .5) == y_test)),
            "correct_at_0_5": int(np.sum((prediction >= .5) == y_test)),
            "log_loss": float(log_loss(y_test, np.clip(prediction, EPSILON, 1 - EPSILON), labels=[0, 1])),
            "ece_10_equal_width_bins": sum(row["count"] * (row["absolute_gap"] or 0) for row in rows) / len(test),
            "mean_probability": float(prediction.mean()),
            "observed_purchase_rate": float(y_test.mean()),
            "probability_min": float(prediction.min()), "probability_max": float(prediction.max()),
        }
    pd.DataFrame({"user_index": test.user_index.to_numpy(), "item_bought": y_test,
                  "linear_probability": linear_probability, "logistic_probability": probability}).to_csv(paths["predictions"], index=False)
    pd.DataFrame(calibration).to_csv(paths["calibration"], index=False)
    ordered_ids = "".join(f"{int(value)}\n" for value in test.user_index).encode()
    results = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "python": __import__("platform").python_version(),
        "versions": {name: metadata.version(name) for name in ["numpy", "pandas", "scipy", "scikit-learn"]},
        "dataset_sha256": sha256(data_path), "features": FEATURES,
        "split": {"test_size": .2, "random_state": 0, "shuffle": True, "stratify": None,
                  "train_rows": len(train), "heldout_rows": len(test),
                  "ordered_heldout_ids_sha256": hashlib.sha256(ordered_ids).hexdigest(),
                  "id_hash_encoding": "UTF-8 integer user_index followed by LF in held-out order"},
        "preprocessing": "StandardScaler fitted on training rows only; serialized with classifier",
        "logistic_parameters": logistic.named_steps["logistic"].get_params(),
        "transformed_feature_order": FEATURES, "interactions": "none in this first comparison",
        "tuning": "none; settings fixed before held-out evaluation",
        "accuracy_threshold": "probability >= 0.5 means buy; fixed reporting convention, not tuned",
        "log_loss_epsilon": EPSILON, "calibration_bins": "10 fixed equal-width probability bins; last includes 1",
        "metrics": metrics, "warnings": [str(w.message) for w in captured],
        "iterations": logistic.named_steps["logistic"].n_iter_.tolist(),
        "scaled_coefficients": logistic.named_steps["logistic"].coef_.tolist(),
        "intercept": logistic.named_steps["logistic"].intercept_.tolist(),
        "reload_max_abs_difference": float(np.max(np.abs(probability - reloaded))),
        "baseline_sha256": baseline_hash, "baseline_preserved": sha256(baseline_path) == baseline_hash,
        "artifacts": {key: path.relative_to(ROOT).as_posix() for key, path in paths.items()},
        "logistic_model_sha256": sha256(paths["model"]),
    }
    assert results["baseline_preserved"]
    paths["results"].write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
