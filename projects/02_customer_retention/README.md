# 02 · Customer retention decision support

## Problem

A retention team has a limited review budget. Build a reproducible risk ranking,
compare it with a prior-only baseline and choose an operating threshold without
using the final test set for selection.

## Pipeline

1. Acquire and validate UCI Iranian Churn.
2. Define a permitted feature set. Exclude Status, derived Customer Value, Age and Age Group.
3. Hash predictor vectors into groups so identical vectors cannot leak across splits.
4. Create grouped train/validation/test partitions, roughly 60/20/20.
5. Train a dummy prior, logistic regression and random forest on training only.
6. Select the model on validation average precision. Select threshold with an explicit
   hypothetical 5:1 false-negative/false-positive cost weight on validation only.
7. Freeze the training model. Evaluate the untouched test set and export diagnostics.
8. Save a locally rebuilt model for schema-checked CSV batch inference.

The threshold is not tuned to the test set. The model is not refitted on validation,
because that would alter the score distribution used for threshold selection.

## Deliverables

- [Executed notebook](../../notebooks/02_customer_retention.ipynb)
- [Training and batch inference](../../src/portfolio/churn.py)
- [Computed model card](../../artifacts/full/churn_model_card.md)
- [Model comparison](../../artifacts/full/churn_model_comparison.csv)
- Auditable split assignments generated locally by the training pipeline
- [Scoring input example](../../examples/scoring_input.csv)

## Acceptance criteria

| ID | Requirement | Evidence |
| --- | --- | --- |
| CH-01 | No identical allowed-feature group spans partitions | Group disjointness test |
| CH-02 | Target and excluded proxies cannot enter predictors | Explicit allowlist test |
| CH-03 | A no-skill model is compared | Prior baseline in validation export |
| CH-04 | Threshold minimises declared validation cost | Weighted-error test |
| CH-05 | Results reflect class imbalance | AP, prevalence, precision, recall and lift |
| CH-06 | CSV inference rejects malformed categories | Contract tests and batch smoke test |

## Interpretation

Average precision evaluates ranking across recall levels, while ROC AUC is a
secondary diagnostic. Confusion matrices and capacity-constrained precision make
the trade-off visible. Top-20% lift compares observed queue precision with observed
test prevalence. It is not a conversion improvement or financial saving.

UCI says input features are aggregated over nine months and labels are measured at
month twelve. The file has no dates or reliable customer identifiers, so true
temporal validation is unavailable. Grouping identical features reduces a specific
leakage risk but cannot reconstruct account identity or guarantee independence.

## Deployment gap

Research demonstration only. A production system would need prospective data,
feature availability checks, probability calibration, subgroup evaluation, drift
monitoring and a controlled treatment experiment. The dashboard's exploratory test
capacity slider is a diagnostic, not validation of a new deployment policy.
No API serving or real-time integration is claimed.
