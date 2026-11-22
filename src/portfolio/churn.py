"""Group-separated retention model selection and out-of-sample scoring."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from portfolio.common import ROOT, SEED, fetch_dataset, require_columns, save_json, sha256
from portfolio.synthetic import churn_demo

# Status is a potential proxy for already-inactive customers. Customer Value has
# undocumented construction. Age and Age Group are omitted to avoid demographic targeting.
FEATURES = [
    "call_failure",
    "complains",
    "subscription_length",
    "charge_amount",
    "seconds_of_use",
    "frequency_of_use",
    "frequency_of_sms",
    "distinct_called_numbers",
    "tariff_plan",
]
EXCLUDED = ["status", "customer_value", "age", "age_group"]


def prepare_churn(raw: pd.DataFrame) -> pd.DataFrame:
    frame = raw.copy()
    frame.columns = ["_".join(str(c).lower().split()) for c in frame.columns]
    require_columns(frame, FEATURES + ["churn"])
    frame = frame[FEATURES + ["churn"]].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(frame.to_numpy()).all():
        raise ValueError("Churn data contains missing or infinite values")
    if not frame.churn.isin([0, 1]).all():
        raise ValueError("Churn labels must be binary")
    if (frame[FEATURES] < 0).any().any():
        raise ValueError("Churn predictors must be non-negative")
    if not frame.tariff_plan.isin([1, 2]).all() or not frame.complains.isin([0, 1]).all():
        raise ValueError("Unexpected tariff or complaint categories")
    return frame


def grouped_split(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.Series]:
    # Without customer IDs, identical predictor vectors must never span partitions.
    groups = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    development, test = next(outer.split(frame[FEATURES], frame.churn, groups))
    inner = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=SEED + 1)
    train_rel, validation_rel = next(
        inner.split(
            frame.iloc[development][FEATURES],
            frame.iloc[development].churn,
            groups.iloc[development],
        )
    )
    return development[train_rel], development[validation_rel], test, groups


def classification_metrics(y, probability, threshold: float) -> dict:
    predicted = probability >= threshold
    return {
        "average_precision": float(average_precision_score(y, probability)),
        "roc_auc": float(roc_auc_score(y, probability)),
        "brier_score": float(brier_score_loss(y, probability)),
        "precision": float(precision_score(y, predicted, zero_division=0)),
        "recall": float(recall_score(y, predicted, zero_division=0)),
        "confusion_matrix": confusion_matrix(y, predicted, labels=[0, 1]).tolist(),
        "threshold": float(threshold),
    }


def select_threshold(y, probability, false_negative_cost=5.0, false_positive_cost=1.0):
    """Choose a threshold on validation labels only. Costs are hypothetical weights."""
    rows = []
    for threshold in np.linspace(0.02, 0.98, 97):
        tn, fp, fn, tp = confusion_matrix(y, probability >= threshold, labels=[0, 1]).ravel()
        rows.append(
            {
                "threshold": threshold,
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "true_positives": int(tp),
                "weighted_error": float(fn * false_negative_cost + fp * false_positive_cost),
            }
        )
    grid = pd.DataFrame(rows)
    best = grid.sort_values(["weighted_error", "threshold"], ascending=[True, False]).iloc[0]
    return float(best.threshold), grid


def build_churn(source: str, output: Path) -> dict:
    import json

    output.mkdir(parents=True, exist_ok=True)
    if source == "full":
        path = fetch_dataset("churn")
        spec = json.loads((ROOT / "data/sources.json").read_text())["churn"]
        if sha256(path) != spec["file_sha256"]:
            raise ValueError("Churn source checksum mismatch")
        raw = pd.read_csv(path)
    else:
        raw = churn_demo()
    frame = prepare_churn(raw)
    train, val, test, groups = grouped_split(frame)
    x, y = frame[FEATURES], frame.churn
    candidates = {
        "dummy_prior": DummyClassifier(strategy="prior"),
        "logistic_regression": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=2000, random_state=SEED)
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=8, min_samples_leaf=5, n_jobs=1, random_state=SEED
        ),
    }
    comparison = []
    for name, estimator in candidates.items():
        estimator.fit(x.iloc[train], y.iloc[train])
        probability = estimator.predict_proba(x.iloc[val])[:, 1]
        comparison.append({"model": name, **classification_metrics(y.iloc[val], probability, 0.5)})
    winner = max(comparison, key=lambda r: r["average_precision"])["model"]
    model = candidates[winner]
    validation_probability = model.predict_proba(x.iloc[val])[:, 1]
    threshold, grid = select_threshold(y.iloc[val], validation_probability)
    # Keep the exact train-fitted model used for threshold selection. Refitting on
    # validation would change scores and invalidate this threshold assessment.
    test_probability = model.predict_proba(x.iloc[test])[:, 1]
    metrics = classification_metrics(y.iloc[test], test_probability, threshold)
    budget = max(1, int(np.ceil(0.2 * len(test))))
    top = np.argsort(-test_probability, kind="stable")[:budget]
    precision_at_budget = float(y.iloc[test].iloc[top].mean())
    importance = permutation_importance(
        model,
        x.iloc[test],
        y.iloc[test],
        scoring="average_precision",
        n_repeats=5,
        random_state=SEED,
        n_jobs=1,
    )
    pd.DataFrame(
        {
            "feature": FEATURES,
            "ap_drop_mean": importance.importances_mean,
            "ap_drop_std": importance.importances_std,
        }
    ).sort_values("ap_drop_mean", ascending=False).to_csv(
        output / "churn_importance.csv", index=False
    )
    scored = frame.iloc[test].copy()
    scored.insert(0, "source_row", test)
    scored["risk_probability"] = test_probability
    scored["flag_at_validation_threshold"] = test_probability >= threshold
    scored.to_csv(output / "churn_test_predictions.csv", index=False)
    ranked = scored.sort_values("risk_probability", ascending=False, kind="stable")
    capacity_rows = []
    for share in range(5, 51, 5):
        queue = ranked.head(max(1, int(np.ceil(len(ranked) * share / 100))))
        precision = float(queue.churn.mean())
        capacity_rows.append(
            {
                "review_share_pct": share,
                "review_slots": len(queue),
                "observed_precision": precision,
                "observed_recall": float(queue.churn.sum() / ranked.churn.sum()),
                "lift": precision / float(ranked.churn.mean()),
            }
        )
    pd.DataFrame(capacity_rows).to_csv(output / "churn_capacity_summary.csv", index=False)
    bins = np.linspace(0, 1, 21)
    distribution = []
    for label, part in scored.groupby("churn"):
        counts, edges = np.histogram(part.risk_probability, bins=bins)
        for idx, count in enumerate(counts):
            distribution.append(
                {
                    "bin_midpoint": float((edges[idx] + edges[idx + 1]) / 2),
                    "outcome": "Churned" if label else "Did not churn",
                    "cases": int(count),
                }
            )
    pd.DataFrame(distribution).to_csv(output / "churn_score_distribution.csv", index=False)
    assignments = pd.DataFrame(
        {"source_row": np.arange(len(frame)), "feature_group": groups, "partition": "unassigned"}
    )
    for label, indices in [("train", train), ("validation", val), ("test", test)]:
        assignments.loc[indices, "partition"] = label
    assignments.to_csv(output / "churn_split_assignments.csv", index=False)
    grid.to_csv(output / "churn_threshold_validation.csv", index=False)
    pd.DataFrame(
        [{k: v for k, v in row.items() if k != "confusion_matrix"} for row in comparison]
    ).to_csv(output / "churn_model_comparison.csv", index=False)
    joblib.dump(
        {"model": model, "features": FEATURES, "threshold": threshold},
        output / "churn_model.joblib",
    )
    summary = {
        "dataset": "UCI Iranian Churn" if source == "full" else "Seeded synthetic churn demo",
        "source_mode": source,
        "rows": len(frame),
        "feature_groups": int(groups.nunique()),
        "seed": SEED,
        "train_rows": len(train),
        "validation_rows": len(val),
        "test_rows": len(test),
        "churn_rate": float(y.mean()),
        "test_churn_rate": float(y.iloc[test].mean()),
        "selected_model": winner,
        "selection_metric": "validation average precision",
        "excluded_features": EXCLUDED,
        "features": FEATURES,
        "test_metrics": metrics,
        "precision_at_top_20_percent": precision_at_budget,
        "lift_at_top_20_percent": precision_at_budget / float(y.iloc[test].mean()),
        "cost_assumption": "False negative = 5 and false positive = 1 arbitrary cost units; not ROI",
        "deployment_status": "Research demonstration; requires prospective validation",
    }
    save_json(output / "churn_summary.json", summary)
    return summary


def score_customers(model_path: Path, input_path: Path, output_path: Path) -> None:
    # joblib/pickle must only be loaded from your own trusted build.
    bundle = joblib.load(model_path)
    frame = pd.read_csv(input_path)
    require_columns(frame, bundle["features"])
    x = frame[bundle["features"]].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(x.to_numpy()).all() or (x < 0).any().any():
        raise ValueError("Scoring inputs must be finite and non-negative")
    if not x.tariff_plan.isin([1, 2]).all() or not x.complains.isin([0, 1]).all():
        raise ValueError("Unexpected tariff or complaint categories")
    result = frame.copy()
    result["risk_probability"] = bundle["model"].predict_proba(x)[:, 1]
    result["flag"] = result.risk_probability >= bundle["threshold"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
