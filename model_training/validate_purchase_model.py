"""Validate the frozen Step 1 logistic pipeline without fitting or tuning.

Run with the project environment from any working directory. Only load pickles
from this reviewed repository; pickle is not safe for untrusted input files.
"""
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import os
import pickle
from datetime import datetime, timezone

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = json.loads((ROOT / "model_training/logistic-comparison-results.json").read_text())
    baseline = json.loads((ROOT / "model_training/baseline-results.json").read_text())
    features = result["features"]
    data_path = ROOT / "data/train_prices_decisions_2026.csv"
    model_path = ROOT / "agents/helper_files_here/purchase_model_logistic.pkl"
    baseline_path = ROOT / "agents/helper_files_here/purchase_model.pkl"
    assert digest(data_path) == result["dataset_sha256"]
    assert digest(model_path) == result["logistic_model_sha256"]
    assert digest(baseline_path) == result["baseline_sha256"]
    assert digest(ROOT / "model_training/purchase_model_baseline.ipynb") == baseline["notebook_sha256"]
    for line in (ROOT / "requirements.txt").read_text().splitlines():
        if "==" in line and not line.startswith("#"):
            name, version = line.split("==")
            assert metadata.version(name) == version
    data = pd.read_csv(data_path)
    train, test = train_test_split(data, test_size=.2, random_state=0)
    predictions = pd.read_csv(ROOT / "model_training/logistic-heldout-predictions.csv")
    np.testing.assert_array_equal(predictions.user_index, test.user_index)
    np.testing.assert_array_equal(predictions.item_bought, test.item_bought.astype(int))
    ids = "".join(f"{int(value)}\n" for value in test.user_index).encode()
    assert hashlib.sha256(ids).hexdigest() == result["split"]["ordered_heldout_ids_sha256"]
    with model_path.open("rb") as stream:
        model = pickle.load(stream)
    with model_path.open("rb") as stream:
        second_load = pickle.load(stream)
    assert list(model.feature_names_in_) == features
    assert list(model.named_steps) == ["scale", "logistic"]
    scaler = model.named_steps["scale"]
    assert int(scaler.n_samples_seen_) == len(train) == 40000
    np.testing.assert_allclose(scaler.mean_, train[features].mean())
    np.testing.assert_allclose(scaler.var_, train[features].var(ddof=0))
    positive = np.flatnonzero(model.classes_ == 1)
    assert len(positive) == 1
    probability = model.predict_proba(test[features])[:, positive[0]]
    repeat = second_load.predict_proba(test[features])[:, positive[0]]
    np.testing.assert_array_equal(probability, repeat)
    np.testing.assert_allclose(probability, predictions.logistic_probability, rtol=1e-12, atol=1e-15)
    np.testing.assert_allclose(model.predict_proba(test[features].iloc[:5])[:, positive[0]], probability[:5])
    assert np.isfinite(probability).all() and ((probability >= 0) & (probability <= 1)).all()
    y = test.item_bought.astype(int).to_numpy()
    calibration = pd.read_csv(ROOT / "model_training/logistic-calibration.csv")
    metrics = {}
    with baseline_path.open("rb") as stream:
        linear = pickle.load(stream)
    linear_probability = np.clip(linear.predict(test[features]), 0, 1)
    np.testing.assert_allclose(linear_probability, predictions.linear_probability, rtol=1e-12, atol=1e-15)
    for name, p in [("clipped_linear", linear_probability), ("logistic_main_effects", probability)]:
        bins = np.minimum((p * 10).astype(int), 9)
        rows = calibration.loc[calibration.model == name]
        assert len(rows) == 10 and int(rows["count"].sum()) == len(y)
        ece = 0.0
        for index in range(10):
            selected = bins == index
            row = rows.iloc[index]
            assert int(row["count"]) == int(selected.sum())
            if selected.any():
                np.testing.assert_allclose([row.mean_probability, row.purchase_rate], [p[selected].mean(), y[selected].mean()])
                ece += selected.sum() * abs(p[selected].mean() - y[selected].mean()) / len(y)
        metric = {
            "brier_mse": float(brier_score_loss(y, p)),
            "log_loss": float(log_loss(y, np.clip(p, 1e-15, 1 - 1e-15), labels=[0, 1])),
            "ece_10_equal_width_bins": float(ece),
            "accuracy_at_0_5": float(np.mean((p >= .5) == y)),
            "correct_at_0_5": int(np.sum((p >= .5) == y)),
        }
        for key, value in metric.items():
            np.testing.assert_allclose(value, result["metrics"][name][key], rtol=1e-12, atol=1e-15)
        metrics[name] = metric
    output = {
        "validated_utc": datetime.now(timezone.utc).isoformat(), "status": "passed",
        "method": "Fresh process; no fitting or tuning",
        "working_directory_outside_project": Path.cwd().resolve() != ROOT,
        "checks": ["all direct dependency pins", "data/model/notebook hashes", "exact heldout IDs and labels",
                   "train-only scaler count/means/variances", "four-feature schema", "positive-class extraction",
                   "finite bounded probabilities", "independent reload equality", "single/batch consistency",
                   "saved predictions", "Brier/logloss/accuracy recomputation", "all calibration bins and ECE",
                   "baseline preserved", "portable paths"],
        "train_rows": len(train), "heldout_rows": len(test), "metrics": metrics,
        "reload_max_abs_difference": float(np.max(np.abs(probability - repeat))),
        "model_sha256": digest(model_path), "dataset_sha256": digest(data_path),
        "training_warning": result["warnings"],
        "interface": "predict_proba(features)[:, index of class 1]; existing pricing agents unchanged",
    }
    (ROOT / "model_training/logistic-final-validation.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
