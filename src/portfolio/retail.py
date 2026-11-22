"""Financially reconciled retail mart with explicit data-quality policies."""

from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from portfolio.common import SEED, fetch_dataset, require_columns, save_json, sha256
from portfolio.synthetic import retail_demo

COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def clean_retail(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    require_columns(raw, COLUMNS)
    frame = raw[COLUMNS].copy()
    frame.columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    ]
    frame["invoice_date"] = pd.to_datetime(frame["invoice_date"], errors="coerce")
    for col in ["quantity", "unit_price"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    for col in ["invoice_no", "stock_code", "country"]:
        frame[col] = frame[col].astype("string").str.strip()
    frame["customer_id"] = pd.to_numeric(frame["customer_id"], errors="coerce").astype("Int64")
    duplicate_mask = frame.duplicated()
    invalid_mask = (
        frame["invoice_date"].isna()
        | frame["quantity"].isna()
        | frame["unit_price"].isna()
        | ~np.isfinite(frame["quantity"])
        | ~np.isfinite(frame["unit_price"])
        | (frame["unit_price"] <= 0)
        | (frame["quantity"] == 0)
        | frame[["invoice_no", "stock_code", "country"]].isna().any(axis=1)
        | frame[["invoice_no", "stock_code", "country"]].eq("").any(axis=1)
    )
    # Mutually exclusive counts allow input = duplicate + invalid + retained.
    invalid_after_dedup = invalid_mask & ~duplicate_mask
    retained = frame.loc[~duplicate_mask & ~invalid_mask].copy()
    retained["line_value"] = retained["quantity"] * retained["unit_price"]
    retained["is_cancellation"] = retained["invoice_no"].str.upper().str.startswith("C")
    # A C-prefixed positive line contradicts the dataset's credit-note convention.
    contradictory = retained["is_cancellation"] & retained["quantity"].gt(0)
    if contradictory.any():
        raise ValueError("Positive quantity on a cancellation invoice requires manual review")
    gross = float(retained.loc[retained.line_value.gt(0), "line_value"].sum())
    credits = float(-retained.loc[retained.line_value.lt(0), "line_value"].sum())
    audit = {
        "input_rows": len(raw),
        "exact_duplicates_removed": int(duplicate_mask.sum()),
        "invalid_rows_removed_after_dedup": int(invalid_after_dedup.sum()),
        "retained_rows": len(retained),
        "missing_customer_rows_retained": int(retained.customer_id.isna().sum()),
        "gross_sales_gbp": gross,
        "credits_gbp": credits,
        "net_revenue_gbp": gross - credits,
        "duplicate_policy": "Remove exact duplicate rows; alternative policy requires source invoice-line IDs",
    }
    if retained.empty:
        raise ValueError("No valid retail lines remain after cleaning")
    return retained, audit


def build_retail(source: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    if source == "full":
        path = fetch_dataset("retail")
        raw = pd.read_excel(path, dtype={"InvoiceNo": str, "StockCode": str})
    else:
        raw = retail_demo()
    frame, audit = clean_retail(raw)
    frame.to_parquet(output / "retail_lines.parquet", index=False)
    with duckdb.connect(str(output / "warehouse.duckdb")) as con:
        con.register("clean_input", frame)
        con.execute("CREATE OR REPLACE TABLE fact_retail AS SELECT * FROM clean_input")
        con.execute((Path(__file__).parent / "queries/retail.sql").read_text())
        for name in ["daily", "monthly", "products", "rfm", "cohorts"]:
            mart = con.sql(f"SELECT * FROM mart_retail_{name}").df()
            mart.to_csv(output / f"retail_{name}.csv", index=False)
            if name == "rfm":
                mart.groupby("segment", as_index=False).agg(
                    customers=("customer_id", "count"), gross_sales_gbp=("monetary_gbp", "sum")
                ).to_csv(output / "retail_segments.csv", index=False)
    positive = frame[frame.line_value.gt(0)]
    countries = frame.groupby("country").line_value.sum().sort_values(ascending=False)
    unidentified = positive.loc[positive.customer_id.isna(), "line_value"].sum()
    summary = {
        **audit,
        "source_mode": source,
        "source_file_sha256": sha256(path) if source == "full" else None,
        "synthetic_seed": SEED if source == "demo" else None,
        "data_type": "Historical public dataset" if source == "full" else "Synthetic demo",
        "period_start": str(frame.invoice_date.min().date()),
        "period_end": str(frame.invoice_date.max().date()),
        "positive_orders": int(positive.invoice_no.nunique()),
        "identified_customers": int(positive.customer_id.nunique()),
        "unidentified_gross_sales_share": float(unidentified / audit["gross_sales_gbp"]),
        "top_country": str(countries.index[0]),
        "top_country_net_revenue_share": float(countries.iloc[0] / audit["net_revenue_gbp"]),
        "credit_to_gross_ratio": audit["credits_gbp"] / audit["gross_sales_gbp"],
    }
    save_json(output / "retail_summary.json", summary)
    return summary
