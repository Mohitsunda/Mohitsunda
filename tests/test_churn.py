import numpy as np
import pandas as pd
import pytest

from portfolio.churn import FEATURES, grouped_split, prepare_churn, select_threshold
from portfolio.synthetic import churn_demo


def test_feature_groups_never_cross_partitions():
    frame = prepare_churn(pd.concat([churn_demo(), churn_demo().head(100)], ignore_index=True))
    train, val, test, groups = grouped_split(frame)
    sets = [set(groups.iloc[idx]) for idx in [train, val, test]]
    assert sets[0].isdisjoint(sets[1])
    assert sets[0].isdisjoint(sets[2])
    assert sets[1].isdisjoint(sets[2])
    assert len(set(np.concatenate([train, val, test]))) == len(frame)
    assert all(frame.iloc[idx].churn.nunique() == 2 for idx in [train, val, test])


def test_target_and_proxy_features_are_not_predictors():
    assert "churn" not in FEATURES
    assert set(FEATURES).isdisjoint({"status", "customer_value", "age", "age_group"})


def test_threshold_uses_weighted_errors_with_explicit_costs():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.2, 0.4, 0.8])
    threshold, grid = select_threshold(y, p)
    assert 0.2 < threshold <= 0.4
    assert grid.weighted_error.min() == 0


def test_contract_rejects_unknown_categories():
    raw = churn_demo().head(10)
    raw["Tariff Plan"] = 8
    with pytest.raises(ValueError, match="categories"):
        prepare_churn(raw)
