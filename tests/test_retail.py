import duckdb
import numpy as np
import pandas as pd
import pytest

from portfolio.retail import clean_retail


def invoice(invoice="100", quantity=2, price=10, customer=1):
    return {
        "InvoiceNo": invoice,
        "StockCode": "SKU1",
        "Description": "Item",
        "Quantity": quantity,
        "InvoiceDate": "2011-01-01",
        "UnitPrice": price,
        "CustomerID": customer,
        "Country": "United Kingdom",
    }


def test_revenue_keeps_credits_and_unidentified_sales():
    raw = pd.DataFrame([invoice(), invoice("101", customer=None), invoice("C100", -1)])
    clean, audit = clean_retail(raw)
    assert audit["gross_sales_gbp"] == 40
    assert audit["credits_gbp"] == 10
    assert audit["net_revenue_gbp"] == 30
    assert len(clean) == 3
    assert audit["missing_customer_rows_retained"] == 1


def test_exclusions_are_mutually_exclusive():
    raw = pd.DataFrame([invoice(), invoice(), invoice("102", price=0), invoice("102", price=0)])
    _, audit = clean_retail(raw)
    assert audit["input_rows"] == (
        audit["exact_duplicates_removed"]
        + audit["invalid_rows_removed_after_dedup"]
        + audit["retained_rows"]
    )
    assert audit["exact_duplicates_removed"] == 2
    assert audit["invalid_rows_removed_after_dedup"] == 1


def test_cancellation_sign_requires_review():
    with pytest.raises(ValueError, match="cancellation"):
        clean_retail(pd.DataFrame([invoice("C100", quantity=1)]))


def test_missing_columns_fail_clearly():
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_retail(pd.DataFrame({"Quantity": [1]}))


def test_nonfinite_financial_values_cannot_enter_totals():
    raw = pd.DataFrame([invoice(), invoice("102", quantity=np.inf), invoice("103", price=np.inf)])
    clean, audit = clean_retail(raw)
    assert len(clean) == 1
    assert audit["invalid_rows_removed_after_dedup"] == 2
    assert audit["net_revenue_gbp"] == 20


def test_financial_marts_reconcile_and_cohorts_have_no_future_zeros():
    from pathlib import Path

    raw = pd.DataFrame([invoice(), invoice("101", quantity=3), invoice("C100", -1)])
    raw.loc[1, "InvoiceDate"] = "2011-02-01"
    clean, audit = clean_retail(raw)
    with duckdb.connect() as con:
        con.register("fact_retail", clean)
        sql = Path(__file__).parents[1] / "src/portfolio/queries/retail.sql"
        con.execute(sql.read_text())
        assert (
            con.sql("SELECT SUM(net_revenue_gbp) FROM mart_retail_daily").fetchone()[0]
            == audit["net_revenue_gbp"]
        )
        cohorts = con.sql("SELECT * FROM mart_retail_cohorts").df()
        assert cohorts.month_index.max() == 1
        assert np.allclose(cohorts.retention, 1)
        rfm = con.sql("SELECT * FROM mart_retail_rfm").df()
        assert rfm.iloc[0].frequency == 2
        assert rfm.iloc[0].monetary_gbp == 50
