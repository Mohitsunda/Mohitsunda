# 03 · Scottish SME green logistics business case

## Case-study brief

An illustrative SME logistics operator wants to reduce transport emissions while
protecting customer service and controlling spend. The case connects the portfolio
owner's interest in ESG and logistics with requirements, data analysis, options
appraisal and a measurable change proposal.

All shipments, distances, cost inputs, delays, emissions factors and consolidation
effects are synthetic. No company data or empirical impact is represented.

## Process

Current process: dispatch individual shipments, record delivery and cost data,
review late deliveries after completion.

Proposed process: aggregate by lane, inspect feasible consolidation choices,
approve a limited pilot, track service and emissions with an agreed rollback rule.

## Requirements traceability

| ID | User story | Acceptance criterion | Evidence |
| --- | --- | --- | --- |
| LOG-01 | As an operations owner, I need shipment-weighted service | Overall SLA equals on-time shipments / shipments, not mean lane percentages | Aggregated weights in optimiser and test |
| LOG-02 | As a finance owner, I need a spend cap | Scenario cost <= baseline × (1 + budget) | Feasibility test |
| LOG-03 | As a sustainability analyst, I need transparent assumptions | Units and invented factors appear beside outputs | Config, dashboard and generated memo |
| LOG-04 | As a planner, I need the best feasible option | Evaluate all 256 binary lane decisions and select minimum emissions | Enumeration and optimum test |
| LOG-05 | As a reviewer, I need infeasibility explained | A service target above achievable service returns a clear message | Infeasible-case test and dashboard |
| LOG-06 | As a pilot owner, I need an implementable plan | Export selected lanes, cost, emissions and projected service | CSV download |

## Stakeholder responsibilities, proposed

| Activity | Accountable | Responsible | Consulted |
| --- | --- | --- | --- |
| Approve budget | Finance owner | Business analyst | Operations owner |
| Confirm feasibility | Operations owner | Carrier planner | Customer service |
| Validate emissions inputs | Sustainability owner | Data analyst | Carrier planner |
| Approve pilot/rollback | Operations owner | Pilot lead | Finance and customer service |

These are proposed project roles, not people contacted during portfolio development.

## Options appraisal

Baseline: make no change. Consolidation candidates: either keep each lane unchanged
or consolidate it under the configured cost, distance and service assumptions.
Enumerate the 2^8 decisions, filter by spend and service constraints, minimise
emissions, then break ties by lower cost. This is a discrete lane-choice model,
not vehicle routing, network optimisation or carrier scheduling.

## Change and benefits measurement

Pilot one selected lane for four weeks after validating real shipment and carrier
data. Record kilometres, allocated loads, invoices, promised/delivered timestamps
and fuel or energy use. Define rollback criteria and exception owners before
launch. Track cost per shipment, service rate, emissions per shipment and absolute
emissions. Separate volume changes from process effects. Benefits remain projected
until measured against a pre-agreed comparison.

## Decision log

| Decision | Reason | Consequence |
| --- | --- | --- |
| Dedicated movement per source row | Makes distance allocation explicit | Shared-load and empty-return emissions are excluded |
| Illustrative factor, 0.25 kg CO₂e/km | Avoids presenting an unverified factor as official | Cannot support a carbon audit |
| Exact enumeration | Eight choices are small enough for full search | Optimum is limited to defined choices |
| Service penalty of 1.5 percentage points | Makes service/cost trade-offs inspectable | An assumption, not a measured intervention effect |

## Deliverables

- [Executed notebook](../../notebooks/03_green_logistics.ipynb)
- [Generator and optimiser](../../src/portfolio/logistics.py)
- [Editable assumptions](../../config/logistics.json)
- [Computed business case](../../artifacts/full/logistics_business_case.md)
- [Full scenario enumeration](../../artifacts/full/logistics_scenarios.csv)
