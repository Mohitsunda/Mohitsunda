# Synthetic retail demonstration

The seed-42 generator produced 12,088 artificial transaction lines.
This offline run exercises data contracts, signed revenue, SQL marts, segment totals
and cohort calculations. No record represents an actual customer.

Computed synthetic gross sales: £633,224.49.
Computed synthetic credits: £45,914.67.
Computed synthetic net revenue: £587,309.82.

The quality audit retains 12,028 rows. Input rows reconcile to
retained rows plus duplicate and invalid exclusions. Individual details are generated
locally. The public snapshot contains only aggregate results.

Use `portfolio build --source full` for the separate historical UCI case study.
The full-data decision memo is in `artifacts/full/retail_case_study.md`.
