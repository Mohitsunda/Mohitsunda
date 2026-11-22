# Public snapshot and local detail

The public repository contains code, synthetic demo generators, aggregate results,
case studies and executed synthetic-data notebook walkthroughs.

The full pipeline downloads licensed historical UCI sources to `data/raw/` on the
user's computer. These downloads, individual-customer RFM exports, row-level churn
predictions, split assignments and local model files are excluded from Git. The
dashboard uses segment totals, cohort counts, score-bin counts and aggregate
capacity metrics. It does not publish customer identifiers or a per-person queue.

Demo mode generates artificial retail and churn inputs from seed 42. Logistics
is synthetic in both modes. The five scoring examples are invented input vectors.
No demo row is copied from an actual customer.

Detailed local files support auditing and batch-inference demonstrations. Review
their permissions and intended audience before sharing them elsewhere. The
repository's publication test rejects tracked individual-customer export paths.
