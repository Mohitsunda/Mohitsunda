# 01 · UK retail performance and customer activity

## Problem and intended user

A commercial analyst needs to reconcile recorded revenue, understand credit
movements and identify customers suitable for a reactivation experiment. The
stakeholders are a finance owner, trading manager and CRM analyst. These are
proposed roles for the case study, not actual project participants.

## End-to-end workflow

1. Download the original UCI workbook and verify its checksum.
2. Validate the schema, parse dates and remove exact duplicates and invalid lines.
3. Retain negative-value credits and unidentified customers in financial totals.
4. Load a fact table into DuckDB. Build daily, monthly, product, RFM and cohort marts.
5. Export CSV results, plot complete-month revenue and write a decision memo.
6. Review the Streamlit dashboard and hand the marts or fact file to Power BI.

Run: `portfolio build --source full`.

## Deliverables

- [Executed notebook](../../notebooks/01_uk_retail.ipynb)
- [Cleaning and orchestration](../../src/portfolio/retail.py)
- [Executable SQL](../../src/portfolio/queries/retail.sql)
- [Computed full-data memo](../../artifacts/full/retail_case_study.md)
- [Metric definitions](../../docs/data_dictionary.md)
- [Power BI model handoff](../../powerbi/README.md)

## Acceptance criteria

| ID | Requirement | Verification |
| --- | --- | --- |
| RET-01 | All input rows are retained or explained by an exclusion | Mutually exclusive audit counts |
| RET-02 | Gross minus credits equals net | SQL and Python reconciliation test |
| RET-03 | Missing customer ID does not discard a sale | Fixture with unidentified purchase |
| RET-04 | Credits do not create purchasing frequency | Credit-note/RFM test |
| RET-05 | Future cohort periods remain missing | SQL cohort test and null heatmap cells |
| RET-06 | Partial final month is marked | `complete_month` SQL flag |
| RET-07 | A reviewer can rebuild without credentials | Offline demo and checksummed public source |

## Analysis decisions

- Remove exact duplicates because no line ID is available. This may remove genuine
  repeated identical lines. The policy is explicit and changes finance totals.
- Exclude zero/negative price, zero quantity, malformed numerics/dates and missing
  invoice, stock code or country. Financial quantities must be finite.
- Keep non-product rows such as valid charges. An alternate merchandise-only view
  requires an agreed stock-code mapping, not an undocumented regular expression.
- Preserve source decimal precision in calculations. Display values to two decimals.
- Segment using transparent recency/frequency rules rather than arbitrary quintiles
  presented as customer value estimates. No unobserved lifetime value is inferred.

## Limitations and next data requests

The first observed purchase is not necessarily a customer's acquisition date.
December 2011 is partial. This retailer has many wholesalers. No margin, stock,
marketing exposure, tax treatment or contact permission is available. Request
invoice-line IDs, return reasons and permissioned CRM linkage before a real pilot.
Measure reactivation through a randomised holdout rather than attributing all
repeat purchases to the campaign.
