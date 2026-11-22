# Project walkthroughs and questions

Use these prompts to explain work you have personally reviewed and understood.
Do not describe the portfolio as an employer project or claim synthetic benefits
were achieved. The initial implementation was created with AI assistance.

## Retail, a two-minute walkthrough

State the commercial question. Explain why removing every row without CustomerID
would understate financial totals. Show gross minus credits equals net, then the
separate identified-customer RFM/cohort views. Explain the exact-duplicate assumption
and partial final month. Finish with a controlled reactivation pilot recommendation.

Questions to practise:

1. How would totals change if genuine identical invoice lines were deduplicated?
2. Why is first-observed purchase not necessarily acquisition?
3. What does a blank future cohort cell mean?
4. What additional data would you need to calculate contribution margin?

## Retention, a two-minute walkthrough

State the capacity-constrained review decision. Explain the dummy baseline,
average precision and grouped partitioning. Show how validation selects the model
and cost threshold before test evaluation. Explain why Status and Customer Value
were excluded, then show precision/lift at a fixed review capacity. Finish with
prospective validation and a randomised intervention pilot.

Questions to practise:

1. Why is accuracy a weak headline with class imbalance?
2. Why keep identical feature vectors in the same partition?
3. Why not refit on validation after selecting the threshold?
4. Why does predicted churn risk not equal retention treatment benefit?

## Logistics, a two-minute walkthrough

Declare that it is a synthetic business case. Describe cost and service acceptance
criteria, the binary lane choices and the full 256-choice search. Show how a stricter
service constraint can make every choice infeasible. Finish with the data required
for a measured operational pilot and an agreed rollback rule.

Questions to practise:

1. Why weight on-time service by shipments rather than averaging lane percentages?
2. What exactly is optimal and what is outside the search space?
3. What would make the emissions estimate suitable for real reporting?
4. How would you separate volume effects from intervention benefits?
