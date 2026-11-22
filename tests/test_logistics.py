import numpy as np
import pandas as pd
import pytest

from portfolio.logistics import generate_deliveries, optimise_lanes, summarise_lanes


def assumptions(**overrides):
    return {
        "max_cost_increase_pct": 0.04,
        "minimum_weighted_on_time_rate": 0.8,
        "consolidation_distance_reduction_pct": 0.22,
        "consolidation_cost_increase_pct": 0.08,
        "consolidation_on_time_penalty_pp": 1.5,
        **overrides,
    }


def test_synthetic_generator_is_reproducible():
    pd.testing.assert_frame_equal(generate_deliveries(20), generate_deliveries(20))


def test_optimum_respects_budget_sla_and_all_candidates():
    lanes = summarise_lanes(generate_deliveries(600), 0.25)
    plan, result, grid = optimise_lanes(lanes, assumptions())
    assert len(grid) == 2 ** len(lanes)
    assert result["scenario_cost_gbp"] <= result["baseline_cost_gbp"] * 1.04 + 1e-6
    assert result["scenario_on_time_rate"] >= 0.8
    assert result["scenario_co2e_kg"] == grid[grid.feasible].co2e_kg.min()
    assert np.isclose(result["scenario_co2e_kg"], plan.scenario_co2e_kg.sum())


def test_zero_budget_keeps_baseline():
    lanes = summarise_lanes(generate_deliveries(600), 0.25)
    plan, result, _ = optimise_lanes(lanes, assumptions(max_cost_increase_pct=0))
    assert not plan.consolidate.any()
    assert result["co2e_reduction_pct"] == 0


def test_infeasible_service_target_is_explicit():
    lanes = summarise_lanes(generate_deliveries(600), 0.25)
    with pytest.raises(ValueError, match="No scenario"):
        optimise_lanes(lanes, assumptions(minimum_weighted_on_time_rate=0.99))


def test_duplicate_shipments_fail():
    deliveries = generate_deliveries(10)
    with pytest.raises(ValueError, match="Duplicate shipment"):
        summarise_lanes(pd.concat([deliveries, deliveries]), 0.25)
