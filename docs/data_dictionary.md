# Data and metric dictionary

## Source provenance

| Asset | Publisher / generation | Licence | Scope |
| --- | --- | --- | --- |
| Online Retail | Daqing Chen, UCI, DOI 10.24432/C5BW33 | CC BY 4.0 | UK-based non-store retailer, December 2010 to 9 December 2011 |
| Iranian Churn | UCI, DOI 10.24432/C5JW3Z | CC BY 4.0 | 3,150 telecom customer rows, nine-month inputs / month-twelve labels |
| Logistics shipments | NumPy seeded generator, this repository | MIT | 6,000 illustrative dedicated vehicle movements in 2025 |

Source integrity hashes are in `data/sources.json`. Synthetic demo generation uses seed 42 in `src/portfolio/synthetic.py`. Raw sources and individual-customer exports remain local. Inspect raw files for actual missing
values. Publisher summary metadata is not a substitute for profiling downloaded data.

## Retail fact

| Field | Meaning | Treatment |
| --- | --- | --- |
| `invoice_no` | Source invoice or credit-note identifier | C prefix indicates cancellation |
| `stock_code` / `description` | Item or charge identifier / name | Charge lines stay in the financial view |
| `quantity` | Signed source quantity | Zero/invalid excluded, negatives retained |
| `unit_price` | GBP per unit | Positive finite values only, source precision retained |
| `invoice_date` | Source timestamp | Invalid dates excluded |
| `customer_id` | Anonymous source identifier | Nullable, never imputed |
| `country` | Source country | Non-empty required |
| `line_value` | Quantity × unit price | Signed financial value |

| Metric | Definition | Boundary |
| --- | --- | --- |
| Gross sales | Sum of positive line values | Includes unidentified customers and valid charges |
| Credits | Negative of sum of negative line values | Value ratio, not item return rate |
| Net recorded revenue | Gross sales minus credits | Not profit or VAT-adjusted accounting revenue |
| Positive orders | Distinct invoices with positive line value | Credits are not orders |
| Gross order value | Gross sales / positive orders | Named gross to avoid net/gross confusion |
| Unidentified sales share | Positive value without customer ID / gross sales | Financial coverage diagnostic |
| Recency | Snapshot date minus latest positive purchase date | Snapshot = max observed date + one day |
| Frequency | Distinct positive invoices per identified customer | Observed window only |
| Monetary | Positive purchase value per identified customer | Not net value or lifetime value |
| Purchase activity retention | Active identified customers / first-observed cohort size | No activity is not confirmed contractual churn |
| Complete month | Month precedes final observed month | Conservative final-month exclusion |

## Churn predictors

| Fields | Units / categories |
| --- | --- |
| `call_failure` | Count of call failures |
| `complains` | 0 no complaint, 1 complaint |
| `subscription_length` | Months |
| `charge_amount` | Ordinal 0 to 9 |
| `seconds_of_use` | Seconds |
| `frequency_of_use` | Call count |
| `frequency_of_sms` | SMS count |
| `distinct_called_numbers` | Distinct called number count |
| `tariff_plan` | 1 pay-as-you-go, 2 contractual |
| `churn` | Outcome, 0 no churn, 1 churn. Never a predictor |

Source Status, Customer Value, Age and Age Group are excluded. Feature-vector groups
are hashes of the permitted predictors, without labels. Test source rows are row
offsets in the historical source, not actual customer identities.

## Logistics

| Metric | Definition |
| --- | --- |
| On-time rate | Shipment-weighted share delivered within promised days |
| Illustrative baseline emissions | Dedicated vehicle km × 0.25 kg CO₂e/km |
| Scenario emissions | Baseline lane emissions × (1 − assumed distance reduction), selected lanes only |
| Scenario cost | Baseline lane cost × (1 + assumed cost increase), selected lanes only |
| Scenario service | Baseline lane service less assumed percentage-point penalty, selected lanes only |

The factor and all intervention effects are invented for this scenario. Empty
returns, vehicle type, electricity mix, shared loads and lifecycle boundaries are
not modelled. They must be defined for any real carbon accounting work.
