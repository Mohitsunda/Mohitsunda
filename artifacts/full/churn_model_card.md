# Customer retention: prioritisation with an honest holdout

## Business decision

Which customers should a capacity-limited retention team review first? Full mode uses public Iranian telecom research data. Demo mode uses generated synthetic inputs. Neither is a UK banking, retail or production customer model.
For the full UCI source, inputs aggregate the first nine months, followed by a three-month planning gap to churn labels.

## Computed model results

| Measure | Value |
| --- | ---: |
| Source rows / unique feature groups | 3,150 / 2,785 |
| Train / validation / test rows | 1884 / 631 / 635 |
| Selected model | random_forest |
| Test churn prevalence | 15.91% |
| Test average precision | 0.9085 |
| Test ROC AUC | 0.9777 |
| Test Brier score, lower is better | 0.0447 |
| Validation-selected threshold | 0.22 |
| Test precision / recall at that threshold | 66.67% / 95.05% |
| Test precision in highest-scoring 20% | 71.65% |
| Top-20% lift against test prevalence | 4.50× |

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
