"""Synthetic Scottish SME logistics case with an exhaustive scenario optimiser."""

from __future__ import annotations

from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from portfolio.common import ROOT, SEED, require_columns, save_json

LANES = {
    "Edinburgh–Glasgow": 95,
    "Edinburgh–Dundee": 105,
    "Edinburgh–Perth": 80,
    "Edinburgh–Stirling": 65,
    "Edinburgh–Aberdeen": 205,
    "Edinburgh–Inverness": 250,
    "Glasgow–Aberdeen": 235,
    "Glasgow–Inverness": 270,
}


def generate_deliveries(rows: int = 6000, seed: int = SEED) -> pd.DataFrame:
    if rows < 1:
        raise ValueError("At least one delivery is required")
    rng = np.random.default_rng(seed)
    lane = rng.choice(list(LANES), size=rows)
    distance = np.array([LANES[item] for item in lane]) * rng.uniform(0.95, 1.12, rows)
    promised = rng.integers(1, 4, rows)
    extra = rng.binomial(1, 0.09 + (distance > 200) * 0.10)
    delivered = promised + extra
    return pd.DataFrame(
        {
            "shipment_id": [f"SYN-{i:05d}" for i in range(rows)],
            "lane": lane,
            "dispatch_date": pd.Timestamp("2025-01-01")
            + pd.to_timedelta(rng.integers(0, 365, rows), unit="D"),
            "distance_km": distance.round(2),
            "weight_kg": rng.uniform(20, 450, rows).round(2),
            "promised_days": promised,
            "actual_days": delivered,
            "cost_gbp": (20 + distance * 0.55 + rng.uniform(0, 20, rows)).round(2),
        }
    )


def summarise_lanes(deliveries: pd.DataFrame, diesel_factor: float) -> pd.DataFrame:
    require_columns(
        deliveries,
        [
            "shipment_id",
            "lane",
            "distance_km",
            "weight_kg",
            "promised_days",
            "actual_days",
            "cost_gbp",
        ],
    )
    if deliveries.shipment_id.duplicated().any():
        raise ValueError("Duplicate shipment IDs")
    numeric = deliveries[["distance_km", "weight_kg", "promised_days", "actual_days", "cost_gbp"]]
    if (
        not np.isfinite(numeric.to_numpy()).all()
        or (numeric <= 0).any().any()
        or not np.isfinite(diesel_factor)
        or diesel_factor <= 0
    ):
        raise ValueError("Logistics quantities and emissions factor must be finite and positive")
    frame = deliveries.copy()
    frame["on_time"] = frame.actual_days <= frame.promised_days
    frame["baseline_co2e_kg"] = frame.distance_km * diesel_factor
    return (
        frame.groupby("lane", as_index=False)
        .agg(
            shipments=("shipment_id", "count"),
            distance_km=("distance_km", "sum"),
            cost_gbp=("cost_gbp", "sum"),
            co2e_kg=("baseline_co2e_kg", "sum"),
            on_time_rate=("on_time", "mean"),
        )
        .sort_values("lane")
        .reset_index(drop=True)
    )


def optimise_lanes(
    lanes: pd.DataFrame, assumptions: dict
) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Enumerate all 2^8 lane decisions. No heuristic labelled as an optimum."""
    require_columns(
        lanes, ["lane", "shipments", "distance_km", "cost_gbp", "co2e_kg", "on_time_rate"]
    )
    if lanes.empty or len(lanes) > 16:
        raise ValueError("Scenario enumeration supports 1 to 16 lanes")
    budget_pct = float(assumptions["max_cost_increase_pct"])
    minimum_sla = float(assumptions["minimum_weighted_on_time_rate"])
    distance_cut = float(assumptions["consolidation_distance_reduction_pct"])
    cost_change = float(assumptions["consolidation_cost_increase_pct"])
    sla_penalty = float(assumptions["consolidation_on_time_penalty_pp"]) / 100
    if (
        not 0 <= distance_cut < 1
        or not 0 <= minimum_sla <= 1
        or budget_pct < 0
        or cost_change < 0
        or not 0 <= sla_penalty <= 1
    ):
        raise ValueError("Invalid scenario assumptions")
    baseline_cost = float(lanes.cost_gbp.sum())
    baseline_co2 = float(lanes.co2e_kg.sum())
    weights = lanes.shipments.to_numpy()
    rows = []
    for bits in product([0, 1], repeat=len(lanes)):
        selection = np.asarray(bits)
        cost = float((lanes.cost_gbp * (1 + selection * cost_change)).sum())
        emissions = float((lanes.co2e_kg * (1 - selection * distance_cut)).sum())
        sla = float(
            np.average(np.clip(lanes.on_time_rate - selection * sla_penalty, 0, 1), weights=weights)
        )
        feasible = cost <= baseline_cost * (1 + budget_pct) + 1e-8 and sla >= minimum_sla - 1e-8
        rows.append(
            {
                "selection": "".join(map(str, bits)),
                "cost_gbp": cost,
                "co2e_kg": emissions,
                "weighted_on_time_rate": sla,
                "feasible": feasible,
            }
        )
    frontier = pd.DataFrame(rows)
    feasible = frontier[frontier.feasible]
    if feasible.empty:
        raise ValueError("No scenario satisfies budget and service constraints. Relax assumptions.")
    best = feasible.sort_values(["co2e_kg", "cost_gbp", "selection"]).iloc[0]
    selected = np.array([int(x) for x in best.selection])
    plan = lanes.copy()
    plan["consolidate"] = selected.astype(bool)
    plan["scenario_cost_gbp"] = plan.cost_gbp * (1 + selected * cost_change)
    plan["scenario_co2e_kg"] = plan.co2e_kg * (1 - selected * distance_cut)
    plan["scenario_on_time_rate"] = np.clip(plan.on_time_rate - selected * sla_penalty, 0, 1)
    summary = {
        "data_type": "Synthetic scenario, not an observed company dataset",
        "shipments": int(lanes.shipments.sum()),
        "lanes": len(lanes),
        "baseline_cost_gbp": baseline_cost,
        "baseline_co2e_kg": baseline_co2,
        "baseline_on_time_rate": float(np.average(lanes.on_time_rate, weights=weights)),
        "scenario_cost_gbp": float(best.cost_gbp),
        "scenario_co2e_kg": float(best.co2e_kg),
        "scenario_on_time_rate": float(best.weighted_on_time_rate),
        "cost_increase_gbp": float(best.cost_gbp - baseline_cost),
        "co2e_reduction_pct": float(1 - best.co2e_kg / baseline_co2),
        "scenarios_evaluated": len(frontier),
        "feasible_scenarios": len(feasible),
        "selected_lanes": plan.loc[plan.consolidate, "lane"].tolist(),
        "assumptions": assumptions,
    }
    return plan, summary, frontier


def build_logistics(output: Path) -> dict:
    import json

    assumptions = json.loads((ROOT / "config/logistics.json").read_text())
    deliveries = generate_deliveries()
    lanes = summarise_lanes(deliveries, assumptions["illustrative_diesel_kg_co2e_per_km"])
    plan, summary, frontier = optimise_lanes(lanes, assumptions)
    deliveries.to_csv(output / "logistics_deliveries.csv", index=False)
    plan.to_csv(output / "logistics_lane_plan.csv", index=False)
    frontier.to_csv(output / "logistics_scenarios.csv", index=False)
    save_json(output / "logistics_summary.json", summary)
    return summary
