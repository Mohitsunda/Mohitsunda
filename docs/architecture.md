# Architecture and design

## Data flow

| Stage | Retail | Retention | Logistics |
| --- | --- | --- | --- |
| Source | Checksummed UCI XLSX or generated synthetic demo | Checksummed UCI CSV or generated synthetic demo | Seeded synthetic generator |
| Contract | Required columns, finite values, invoice sign, valid dates | Numeric allowlist, binary target, valid categories | Unique shipment IDs, positive finite quantities |
| Transformation | Explicit exclusions, signed line value | Normalised names, feature groups, partition assignment | Lane aggregation and illustrative emissions |
| Analysis | DuckDB SQL marts, RFM, cohorts | Train, validate, freeze, test, batch score | Enumerate choices, filter constraints, minimise emissions |
| Output | CSV, JSON, Parquet, DuckDB, memo | CSV, JSON, local model, model card | CSV, JSON, plan and business case |
| Presentation | Streamlit + Power BI handoff | Streamlit risk diagnostics | Streamlit scenario explorer |

## Engineering choices

- A single packaged codebase avoids copied logic in notebooks and dashboard pages.
- The dashboard reads built results. Opening a page does not download datasets or retrain models.
- Seeded artificial retail and churn generators make CI and demonstrations work offline.
- Full public-source hashes detect unexpected upstream changes before processing.
- Raw and executable model files stay out of Git. A build recreates both locally.
- CSV/JSON outputs allow inspection without Python. Monetary presentation rounds
  to two decimals while calculations retain the source price precision.
- The demo and full folders are separate. Full mode uses UCI retail and churn sources. Demo mode generates artificial retail and churn inputs. Logistics is synthetic in both.
- GitHub Actions can test the project without cloud credentials or secret tokens.

## Dataset refresh

These are historical research snapshots, not live feeds. A changed checksum is a
review event. Verify the upstream source, licence, schema and row counts before
updating `data/sources.json`. Download reviewed sources with `portfolio download --dataset all`, rerun both builds and review result diffs.
Do not bypass checksum failures or silently substitute a different dataset.
