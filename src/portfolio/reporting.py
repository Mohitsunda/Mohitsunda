"""Generate decision memos and publication-ready charts from computed outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

TEAL = "#087f8c"
NAVY = "#16324f"
AMBER = "#d2882d"


def render_reports(output: Path, retail: dict, churn: dict, logistics: dict) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.labelcolor": NAVY,
            "text.color": NAVY,
        }
    )
    monthly = pd.read_csv(output / "retail_monthly.csv")
    importance = pd.read_csv(output / "churn_importance.csv")
    lanes = pd.read_csv(output / "logistics_lane_plan.csv")
    fig, axes = plt.subplots(1, 3, figsize=(17, 5), layout="constrained")
    complete = monthly[monthly.complete_month]
    axes[0].bar(complete.month.str[:7], complete.net_revenue_gbp / 1000, color=TEAL)
    axes[0].tick_params(axis="x", rotation=75, labelsize=8)
    axes[0].set(title=f"Retail | {retail['source_mode']} data", ylabel="Net revenue (£000)")
    top = importance.head(6).sort_values("ap_drop_mean")
    axes[1].barh(top.feature.str.replace("_", " "), top.ap_drop_mean, color=NAVY)
    axes[1].set(title="Churn | held-out diagnostics", xlabel="Average precision drop when permuted")
    axes[2].bar(
        ["Baseline", "Scenario"],
        [logistics["baseline_co2e_kg"] / 1000, logistics["scenario_co2e_kg"] / 1000],
        color=[NAVY, TEAL],
    )
    axes[2].set(title="Logistics | synthetic scenario", ylabel="Illustrative tonnes CO₂e")
    fig.suptitle("Mohit Sunda | Analytics portfolio", fontsize=19, fontweight="bold")
    fig.savefig(output / "portfolio_overview.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
    ax.barh(lanes.lane, lanes.co2e_kg / 1000, color=NAVY, label="Baseline")
    ax.barh(lanes.lane, lanes.scenario_co2e_kg / 1000, color=TEAL, label="Scenario")
    ax.set(title="Synthetic lane consolidation plan", xlabel="Illustrative tonnes CO₂e")
    ax.legend()
    fig.savefig(output / "logistics_lane_chart.png", dpi=150)
    plt.close(fig)

    rfm = pd.read_csv(output / "retail_rfm.csv")
    lapsed = rfm[rfm.segment.eq("Loyal lapsed")]
    retail_report = f"""# UK retail: performance and customer activity

## Decision brief

Full mode uses UCI Online Retail. Demo mode uses generated artificial transactions. The {retail["source_mode"]}
run contains {retail["input_rows"]:,} input rows from {retail["period_start"]} to {retail["period_end"]}.
Demo-run figures describe generated artificial transactions, not a real retailer.

## Computed evidence

| Measure | Value |
| --- | ---: |
| Gross positive sales | £{retail["gross_sales_gbp"]:,.2f} |
| Negative-value credits | £{retail["credits_gbp"]:,.2f} |
| Net recorded revenue | £{retail["net_revenue_gbp"]:,.2f} |
| Positive invoices | {retail["positive_orders"]:,} |
| Identified purchasing customers | {retail["identified_customers"]:,} |
| Credits / gross sales | {retail["credit_to_gross_ratio"]:.2%} |
| Unidentified share of gross sales | {retail["unidentified_gross_sales_share"]:.2%} |
| {retail["top_country"]} share of net revenue | {retail["top_country_net_revenue_share"]:.2%} |

## Recommended next decisions

1. Investigate credit-note causes with transaction owners before changing returns policy.
   The credit/gross ratio measures value movements, not a product return probability.
2. Pilot a reactivation message for the {len(lapsed):,} customers meeting the explicit
   'Loyal lapsed' rule: at least three positive invoices and more than 90 days since purchase.
   Establish contact permission and randomise a control group before estimating uplift.
3. Address missing customer identifiers before using purchase activity retention as a store-wide KPI.
4. Compare complete months only. December 2011 stops on 9 December and cannot be compared
   directly with a complete November.

## Reconciliation and scope

{retail["exact_duplicates_removed"]:,} exact duplicate rows removed.
{retail["invalid_rows_removed_after_dedup"]:,} further invalid rows removed.
{retail["retained_rows"]:,} rows retained, including
{retail["missing_customer_rows_retained"]:,} without a customer ID.
Input rows equal duplicate exclusions plus invalid exclusions plus retained rows.
Gross sales minus credits equals net revenue. Missing-ID sales remain in financial totals
but cannot enter RFM or customer activity cohorts. Positive-price non-product lines remain
included, so this is a recorded-revenue analysis rather than merchandise-only sales.

No margin, marketing cost, contact permission, stock availability or customer acquisition
date is provided. Cohorts mean first observed purchase in this window, not confirmed new
customers. Pre-window activity and right-censoring limit interpretation. Deduplicating exact
rows is an explicit assumption because source invoice-line IDs are unavailable.

## Reproduce

Run `portfolio build --source {retail["source_mode"]}` from the repository root.
Inspect `retail_summary.json`, `retail_daily.csv`, `retail_rfm.csv`,
`retail_cohorts.csv` and the executable SQL in `src/portfolio/queries/retail.sql`.

Source: Chen, D. (2015), [Online Retail, UCI](https://doi.org/10.24432/C5BW33), CC BY 4.0.
"""
    metrics = churn["test_metrics"]
    churn_report = f"""# Customer retention: prioritisation with an honest holdout

## Business decision

Which customers should a capacity-limited retention team review first? Full mode uses public Iranian telecom research data. Demo mode uses generated synthetic inputs. Neither is a UK banking, retail or production customer model.
For the full UCI source, inputs aggregate the first nine months, followed by a three-month planning gap to churn labels.

## Computed model results

| Measure | Value |
| --- | ---: |
| Source rows / unique feature groups | {churn["rows"]:,} / {churn["feature_groups"]:,} |
| Train / validation / test rows | {churn["train_rows"]} / {churn["validation_rows"]} / {churn["test_rows"]} |
| Selected model | {churn["selected_model"]} |
| Test churn prevalence | {churn["test_churn_rate"]:.2%} |
| Test average precision | {metrics["average_precision"]:.4f} |
| Test ROC AUC | {metrics["roc_auc"]:.4f} |
| Test Brier score, lower is better | {metrics["brier_score"]:.4f} |
| Validation-selected threshold | {metrics["threshold"]:.2f} |
| Test precision / recall at that threshold | {metrics["precision"]:.2%} / {metrics["recall"]:.2%} |
| Test precision in highest-scoring 20% | {churn["precision_at_top_20_percent"]:.2%} |
| Top-20% lift against test prevalence | {churn["lift_at_top_20_percent"]:.2f}× |

## Evaluation design

Identical allowed-feature vectors stay in one partition with StratifiedGroupKFold.
This prevents duplicate-vector leakage without assuming that anonymised rows are all
independent customers. The split is roughly 60/20/20, not guaranteed exact because groups
are indivisible. A dummy prior, scaled logistic regression and random forest compete on
validation average precision. A fixed 5:1 false-negative/false-positive cost weight selects
the threshold on validation only. These are arbitrary decision weights, not financial ROI.
The fitted training model is frozen before evaluating the test set. It is not refitted on
validation. Split assignments are generated locally for audit. Only aggregate model diagnostics are published.

Status and Customer Value are excluded because operational timing or derivation could hide
leakage. Age and Age Group are excluded from this targeting example. Excluding demographics
alone does not prove fairness. Permutation importance is a post-hoc held-out diagnostic,
not evidence of causation and not used to tune the model. Correlated usage variables can
share importance. Brier score is reported, but model probabilities are not calibrated in a
separate prospective cohort. Bootstrap uncertainty and temporal validation remain future work.

## Recommendation

Review the highest-risk queue within an agreed contact budget. Do not claim that contacting
a predicted churner prevents churn. Run a randomised retention pilot to estimate incremental
effect and costs. Obtain newer, local data, validate feature timing, assess subgroup error
rates and monitor drift before any operational deployment. No actual customers are contacted.

## Batch inference

After building, run `portfolio score --model artifacts/full/churn_model.joblib
--input examples/scoring_input.csv --output artifacts/scored_customers.csv` as one line.
Only load model files produced by your own trusted build. No model pickle is committed.

Source: [Iranian Churn (2020), UCI](https://doi.org/10.24432/C5JW3Z), CC BY 4.0.
"""
    logistics_report = f"""# Green logistics: service, cost and emissions trade-offs

## Scenario status

All {logistics["shipments"]:,} shipments are generated from seed 42 for eight illustrative
Scottish lanes. Distances, costs, delays and emissions inputs are invented assumptions.
This is a business-analysis and optimisation demonstration, not a company's results or
a compliant carbon inventory. The 0.25 kg CO₂e/km factor is illustrative and is not a
government conversion factor. Each row represents a dedicated vehicle movement allocated
fully to one shipment. Shared-load allocation and empty returns are outside this scenario.

## Computed scenario

| Measure | Baseline | Selected scenario |
| --- | ---: | ---: |
| Total transport cost | £{logistics["baseline_cost_gbp"]:,.2f} | £{logistics["scenario_cost_gbp"]:,.2f} |
| Illustrative tonnes CO₂e | {logistics["baseline_co2e_kg"] / 1000:,.2f} | {logistics["scenario_co2e_kg"] / 1000:,.2f} |
| Shipment-weighted on-time rate | {logistics["baseline_on_time_rate"]:.2%} | {logistics["scenario_on_time_rate"]:.2%} |

The selected scenario reduces modelled emissions by {logistics["co2e_reduction_pct"]:.2%}
for an additional £{logistics["cost_increase_gbp"]:,.2f}. This is a projected result conditional
on the assumptions. No savings or intervention effect has been observed.

## Optimisation and requirements

Enumerate all {logistics["scenarios_evaluated"]} combinations of lane consolidation.
Minimise emissions subject to at most a 4% increase in total transport cost and at least
84% shipment-weighted on-time service. {logistics["feasible_scenarios"]} scenarios satisfy
both constraints. Ties resolve by lower cost and then lexicographic selection. Candidate
consolidation assumes a 22% distance reduction, 8% lane-cost increase and 1.5 percentage-point
on-time penalty. The optimum applies only to these discrete choices and assumptions.

Selected lanes: {", ".join(logistics["selected_lanes"])}.

## Proposed change and measurement

Pilot one selected lane for four weeks. Before launch, validate carrier capacity, service
windows, actual odometer kilometres, load allocation, fuel and cost data. Set a service
rollback threshold with the operations owner. Compare against a pre-agreed baseline and
record changed shipment volumes. No recommendation should be implemented from synthetic
evidence alone. The dashboard exposes budget, distance reduction and service assumptions
so a stakeholder can inspect feasible alternatives and infeasible combinations.

Full requirements, acceptance tests, RACI and decision log: `projects/03_green_logistics/README.md`.
"""
    if retail["source_mode"] == "demo":
        retail_report = f"""# Synthetic retail demonstration

The seed-42 generator produced {retail["input_rows"]:,} artificial transaction lines.
This offline run exercises data contracts, signed revenue, SQL marts, segment totals
and cohort calculations. No record represents an actual customer.

Computed synthetic gross sales: £{retail["gross_sales_gbp"]:,.2f}.
Computed synthetic credits: £{retail["credits_gbp"]:,.2f}.
Computed synthetic net revenue: £{retail["net_revenue_gbp"]:,.2f}.

The quality audit retains {retail["retained_rows"]:,} rows. Input rows reconcile to
retained rows plus duplicate and invalid exclusions. Individual details are generated
locally. The public snapshot contains only aggregate results.

Use `portfolio build --source full` for the separate historical UCI case study.
The full-data decision memo is in `artifacts/full/retail_case_study.md`.
"""
    if churn["source_mode"] == "demo":
        churn_report = f"""# Synthetic churn model demonstration

The seed-42 generator produced {churn["rows"]:,} artificial labelled cases. No input
row describes an actual customer. The offline run exercises group-separated splits,
baseline comparison, validation-only model/threshold selection and batch scoring.

Selected model: {churn["selected_model"]}.
Synthetic held-out average precision: {metrics["average_precision"]:.4f}.
Synthetic held-out ROC AUC: {metrics["roc_auc"]:.4f}.
Validation-selected threshold: {metrics["threshold"]:.2f}.

These scores describe the generator only. They are not evidence of predictive
performance for actual customers. Full mode separately downloads UCI Iranian Churn
locally, with an aggregate model card in `artifacts/full/churn_model_card.md`.
"""
    for name, content in [
        ("retail_case_study.md", retail_report),
        ("churn_model_card.md", churn_report),
        ("logistics_business_case.md", logistics_report),
    ]:
        (output / name).write_text(content)
