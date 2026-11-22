"""Dashboard views shared by the app router and file-based pages."""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio.common import ROOT
from portfolio.logistics import optimise_lanes


def base_path():
    return ROOT / "artifacts" / st.session_state.get("retail_source", "full")


@st.cache_data
def read_csv(path: str):
    return pd.read_csv(path)


def table(name):
    return read_csv(str(base_path() / name))


def summary(name):
    return json.loads((base_path() / name).read_text())


def chart(fig):
    fig.update_layout(
        font_family="Arial",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=35, b=10),
        colorway=["#087f8c", "#16324f", "#db9c3c", "#6aa7a2"],
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def home():
    st.caption("PORTFOLIO / 01")
    st.title("From messy data to a decision.")
    st.write(
        "Three reproducible projects spanning commercial analytics, predictive modelling and operational change."
    )
    r, c, logistics = (
        summary("retail_summary.json"),
        summary("churn_summary.json"),
        summary("logistics_summary.json"),
    )
    cols = st.columns(3)
    with cols[0]:
        st.metric("Retail transaction rows", f"{r['input_rows']:,}")
        st.subheader("UK retail performance")
        st.write(
            "Reconcile revenue, inspect credits, segment customers and explore purchase activity cohorts."
        )
        st.caption("Python · DuckDB SQL · Power BI export")
    with cols[1]:
        st.metric("Churn test average precision", f"{c['test_metrics']['average_precision']:.3f}")
        st.subheader("Customer retention")
        st.write(
            "Compare baselines, separate duplicate feature groups and prioritise a finite review queue."
        )
        st.caption("scikit-learn · validation design · batch inference")
    with cols[2]:
        st.metric("Logistics scenarios evaluated", f"{logistics['scenarios_evaluated']:,}")
        st.subheader("Green logistics planning")
        st.write(
            "Explore the cost, service and emissions trade-offs of a synthetic Scottish logistics case."
        )
        st.caption("Scenario optimisation · requirements · change plan")
    st.divider()
    st.image(str(base_path() / "portfolio_overview.png"), width="stretch")
    st.subheader("Built to be inspected")
    st.write(
        "Every project includes source provenance, metric definitions, executable code, computed outputs and limitations. Use the navigation to explore each decision."
    )
    st.caption(
        "Independent portfolio work. Historical public data and synthetic scenarios. No employer or client outcomes are claimed."
    )


def retail():
    source = st.session_state.get("retail_source", "full")
    st.caption("COMMERCIAL ANALYTICS / 02")
    st.title("UK retail performance")
    r = summary("retail_summary.json")
    st.caption(f"{r['data_type']} · {r['period_start']} to {r['period_end']} · {source} run · GBP")
    daily = table("retail_daily.csv").copy()
    daily["order_date"] = pd.to_datetime(daily.order_date)
    col1, col2 = st.columns([2, 1])
    with col1:
        countries = st.multiselect(
            "Countries", sorted(daily.country.unique()), default=["United Kingdom"]
        )
    with col2:
        date_range = st.date_input(
            "Date range",
            value=(daily.order_date.min().date(), daily.order_date.max().date()),
            min_value=daily.order_date.min().date(),
            max_value=daily.order_date.max().date(),
        )
    if len(date_range) != 2:
        st.info("Choose an end date to apply the date filter.")
        return
    chosen = daily[
        daily.country.isin(countries)
        & daily.order_date.between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))
    ]
    if chosen.empty:
        st.info("No records match this selection. Select a country or a wider date range.")
        return
    gross, credits, net, orders = [
        chosen[col].sum() for col in ["gross_sales_gbp", "credits_gbp", "net_revenue_gbp", "orders"]
    ]
    cols = st.columns(4)
    cols[0].metric("Net recorded revenue", f"£{net:,.0f}")
    cols[1].metric("Positive invoices", f"{orders:,.0f}")
    cols[2].metric("Gross order value", f"£{gross / orders:,.2f}" if orders else "N/A")
    cols[3].metric("Credits / gross sales", f"{credits / gross:.1%}" if gross else "N/A")
    trend = chosen.groupby("order_date", as_index=False)[
        ["gross_sales_gbp", "credits_gbp", "net_revenue_gbp"]
    ].sum()
    chart(
        px.line(
            trend,
            x="order_date",
            y="net_revenue_gbp",
            title="Daily net revenue",
            labels={"order_date": "Date", "net_revenue_gbp": "GBP"},
        )
    )
    st.caption(
        "Partial days and December 2011 are included in this filtered daily view. Compare like-for-like periods."
    )
    t1, t2, t3 = st.tabs(["Customer activity", "Data quality", "Decision memo"])
    with t1:
        st.caption(
            "The following customer views cover the whole run, independently of the country/date filters above."
        )
        segments = table("retail_segments.csv")
        chart(px.bar(segments, x="segment", y="customers", title="Rule-based customer segments"))
        cohorts = table("retail_cohorts.csv")
        matrix = cohorts.pivot(index="cohort_month", columns="month_index", values="retention")
        chart(
            px.imshow(
                matrix,
                text_auto=".0%",
                color_continuous_scale="Teal",
                zmin=0,
                zmax=1,
                title="Purchase activity retention",
                labels={"color": "Active share"},
            )
        )
        st.caption(
            "Cohorts use first observed purchase. Blank cells are unobserved, not zero. Final-month activity is censored."
        )
        st.download_button(
            "Download customer segments",
            segments.to_csv(index=False),
            "customer_segments.csv",
            "text/csv",
        )
    with t2:
        st.dataframe(
            pd.DataFrame(
                {
                    "Check": [
                        "Input rows",
                        "Duplicates removed",
                        "Invalid rows removed",
                        "Retained rows",
                        "Retained without customer ID",
                    ],
                    "Count": [
                        r[k]
                        for k in [
                            "input_rows",
                            "exact_duplicates_removed",
                            "invalid_rows_removed_after_dedup",
                            "retained_rows",
                            "missing_customer_rows_retained",
                        ]
                    ],
                }
            ),
            hide_index=True,
        )
        st.write(
            f"Unidentified customers account for {r['unidentified_gross_sales_share']:.1%} of gross sales. Their transactions stay in financial totals."
        )
    with t3:
        st.markdown((base_path() / "retail_case_study.md").read_text())


def churn():
    st.caption("PREDICTIVE ANALYTICS / 03")
    st.title("Customer retention intelligence")
    c = summary("churn_summary.json")
    st.caption(c["dataset"] + " · no production customer decisions")
    cols = st.columns(4)
    cols[0].metric("Test average precision", f"{c['test_metrics']['average_precision']:.3f}")
    cols[1].metric("Test ROC AUC", f"{c['test_metrics']['roc_auc']:.3f}")
    cols[2].metric("Top 20% lift", f"{c['lift_at_top_20_percent']:.2f}×")
    cols[3].metric("Frozen validation threshold", f"{c['test_metrics']['threshold']:.2f}")
    t1, t2, t3 = st.tabs(["Review capacity", "Model evidence", "Model card"])
    with t1:
        capacities = table("churn_capacity_summary.csv")
        budget = st.slider("Share of held-out cases to review (%)", 5, 50, 20, 5)
        selected = capacities.loc[capacities.review_share_pct.eq(budget)].iloc[0]
        k1, k2, k3 = st.columns(3)
        k1.metric("Review slots", int(selected.review_slots))
        k2.metric("Observed precision in queue", f"{selected.observed_precision:.1%}")
        k3.metric("Observed churners captured", f"{selected.observed_recall:.1%}")
        st.caption(
            "Exploratory aggregate holdout diagnostics. Changing capacity does not validate a new deployment policy. Individual source rows and review queues are generated locally by the pipeline."
        )
        distribution = table("churn_score_distribution.csv")
        chart(
            px.bar(
                distribution,
                x="bin_midpoint",
                y="cases",
                color="outcome",
                barmode="overlay",
                title="Aggregate held-out risk score distribution",
            )
        )
        st.dataframe(capacities, hide_index=True, width="stretch")
        st.download_button(
            "Download aggregate capacity metrics",
            capacities.to_csv(index=False),
            "capacity_metrics.csv",
            "text/csv",
        )
    with t2:
        st.write(f"Selected using validation average precision: {c['selected_model']}.")
        st.dataframe(table("churn_model_comparison.csv"), hide_index=True, width="stretch")
        importance = table("churn_importance.csv").sort_values("ap_drop_mean")
        chart(
            px.bar(
                importance,
                y="feature",
                x="ap_drop_mean",
                orientation="h",
                title="Held-out permutation importance",
            )
        )
        st.caption("Association, not causation. Correlated features share predictive information.")
        st.dataframe(
            pd.DataFrame(
                c["test_metrics"]["confusion_matrix"],
                index=["Actual 0", "Actual 1"],
                columns=["Predicted 0", "Predicted 1"],
            ),
            width="stretch",
        )
    with t3:
        st.markdown((base_path() / "churn_model_card.md").read_text())


def logistics():
    st.caption("BUSINESS ANALYSIS / 04")
    st.title("Green logistics decision lab")
    st.info(
        "Synthetic data and illustrative emissions assumptions. Scenario outputs are not observed savings."
    )
    saved = summary("logistics_summary.json")
    assumptions = dict(saved["assumptions"])
    a, b, c = st.columns(3)
    assumptions["max_cost_increase_pct"] = a.slider("Maximum cost increase (%)", 0, 10, 4) / 100
    assumptions["minimum_weighted_on_time_rate"] = (
        b.slider("Minimum on-time service (%)", 75, 95, 84) / 100
    )
    assumptions["consolidation_distance_reduction_pct"] = (
        c.slider("Assumed distance reduction (%)", 5, 40, 22) / 100
    )
    lanes = table("logistics_lane_plan.csv")[
        ["lane", "shipments", "distance_km", "cost_gbp", "co2e_kg", "on_time_rate"]
    ]
    try:
        plan, result, frontier = optimise_lanes(lanes, assumptions)
    except ValueError as exc:
        st.warning(str(exc))
        st.caption(
            "The baseline service rate is below this requested service constraint. Adjust the assumptions to inspect feasible choices."
        )
        return
    cols = st.columns(4)
    cols[0].metric("Modelled CO₂e reduction", f"{result['co2e_reduction_pct']:.1%}")
    cols[1].metric("Additional cost", f"£{result['cost_increase_gbp']:,.0f}")
    cols[2].metric("Scenario on-time rate", f"{result['scenario_on_time_rate']:.1%}")
    cols[3].metric("Feasible combinations", result["feasible_scenarios"])
    chart(
        px.scatter(
            frontier,
            x="cost_gbp",
            y="co2e_kg",
            color=frontier.feasible.map({True: "Feasible", False: "Outside constraints"}),
            hover_data=["weighted_on_time_rate", "selection"],
            title="All 256 discrete choices",
            labels={"cost_gbp": "Scenario cost (GBP)", "co2e_kg": "Illustrative CO₂e (kg)"},
        )
    )
    st.dataframe(
        plan[
            [
                "lane",
                "shipments",
                "consolidate",
                "scenario_cost_gbp",
                "scenario_co2e_kg",
                "scenario_on_time_rate",
            ]
        ],
        hide_index=True,
        width="stretch",
    )
    st.download_button(
        "Download this scenario plan", plan.to_csv(index=False), "scenario_plan.csv", "text/csv"
    )
    with st.expander("Business case and assumptions"):
        st.caption(
            "The following memo describes the saved default scenario. The live scenario above reflects your current sliders."
        )
        st.markdown((base_path() / "logistics_business_case.md").read_text())
