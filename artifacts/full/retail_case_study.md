# UK retail: performance and customer activity

## Decision brief

Full mode uses UCI Online Retail. Demo mode uses generated artificial transactions. The full
run contains 541,909 input rows from 2010-12-01 to 2011-12-09.
Demo-run figures describe generated artificial transactions, not a real retailer.

## Computed evidence

| Measure | Value |
| --- | ---: |
| Gross positive sales | £10,642,110.80 |
| Negative-value credits | £893,979.73 |
| Net recorded revenue | £9,748,131.07 |
| Positive invoices | 19,960 |
| Identified purchasing customers | 4,338 |
| Credits / gross sales | 8.40% |
| Unidentified share of gross sales | 16.49% |
| United Kingdom share of net revenue | 84.01% |

## Recommended next decisions

1. Investigate credit-note causes with transaction owners before changing returns policy.
   The credit/gross ratio measures value movements, not a product return probability.
2. Pilot a reactivation message for the 285 customers meeting the explicit
   'Loyal lapsed' rule: at least three positive invoices and more than 90 days since purchase.
   Establish contact permission and randomise a control group before estimating uplift.
3. Address missing customer identifiers before using purchase activity retention as a store-wide KPI.
4. Compare complete months only. December 2011 stops on 9 December and cannot be compared
   directly with a complete November.

## Reconciliation and scope

5,268 exact duplicate rows removed.
2,512 further invalid rows removed.
534,129 rows retained, including
132,565 without a customer ID.
Input rows equal duplicate exclusions plus invalid exclusions plus retained rows.
Gross sales minus credits equals net revenue. Missing-ID sales remain in financial totals
but cannot enter RFM or customer activity cohorts. Positive-price non-product lines remain
included, so this is a recorded-revenue analysis rather than merchandise-only sales.

No margin, marketing cost, contact permission, stock availability or customer acquisition
date is provided. Cohorts mean first observed purchase in this window, not confirmed new
customers. Pre-window activity and right-censoring limit interpretation. Deduplicating exact
rows is an explicit assumption because source invoice-line IDs are unavailable.

## Reproduce

Run `portfolio build --source full` from the repository root.
Inspect `retail_summary.json`, `retail_daily.csv`, `retail_rfm.csv`,
`retail_cohorts.csv` and the executable SQL in `src/portfolio/queries/retail.sql`.

Source: Chen, D. (2015), [Online Retail, UCI](https://doi.org/10.24432/C5BW33), CC BY 4.0.
