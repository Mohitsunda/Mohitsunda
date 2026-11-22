# Synthetic churn model demonstration

The seed-42 generator produced 1,500 artificial labelled cases. No input
row describes an actual customer. The offline run exercises group-separated splits,
baseline comparison, validation-only model/threshold selection and batch scoring.

Selected model: logistic_regression.
Synthetic held-out average precision: 0.6059.
Synthetic held-out ROC AUC: 0.7420.
Validation-selected threshold: 0.53.

These scores describe the generator only. They are not evidence of predictive
performance for actual customers. Full mode separately downloads UCI Iranian Churn
locally, with an aggregate model card in `artifacts/full/churn_model_card.md`.
