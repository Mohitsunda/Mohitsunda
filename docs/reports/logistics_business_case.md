# Green logistics: service, cost and emissions trade-offs

## Scenario status

All 6,000 shipments are generated from seed 42 for eight illustrative
Scottish lanes. Distances, costs, delays and emissions inputs are invented assumptions.
This is a business-analysis and optimisation demonstration, not a company's results or
a compliant carbon inventory. The 0.25 kg CO₂e/km factor is illustrative and is not a
government conversion factor. Each row represents a dedicated vehicle movement allocated
fully to one shipment. Shared-load allocation and empty returns are outside this scenario.

## Computed scenario

| Measure | Baseline | Selected scenario |
| --- | ---: | ---: |
| Total transport cost | £734,531.26 | £763,242.34 |
| Illustrative tonnes CO₂e | 251.95 | 222.78 |
| Shipment-weighted on-time rate | 85.70% | 85.14% |

The selected scenario reduces modelled emissions by 11.58%
for an additional £28,711.08. This is a projected result conditional
on the assumptions. No savings or intervention effect has been observed.

## Optimisation and requirements

Enumerate all 256 combinations of lane consolidation.
Minimise emissions subject to at most a 4% increase in total transport cost and at least
84% shipment-weighted on-time service. 128 scenarios satisfy
both constraints. Ties resolve by lower cost and then lexicographic selection. Candidate
consolidation assumes a 22% distance reduction, 8% lane-cost increase and 1.5 percentage-point
on-time penalty. The optimum applies only to these discrete choices and assumptions.

Selected lanes: Edinburgh–Aberdeen, Edinburgh–Inverness, Glasgow–Aberdeen.

## Proposed change and measurement

Pilot one selected lane for four weeks. Before launch, validate carrier capacity, service
windows, actual odometer kilometres, load allocation, fuel and cost data. Set a service
rollback threshold with the operations owner. Compare against a pre-agreed baseline and
record changed shipment volumes. No recommendation should be implemented from synthetic
evidence alone. The dashboard exposes budget, distance reduction and service assumptions
so a stakeholder can inspect feasible alternatives and infeasible combinations.

Full requirements, acceptance tests, RACI and decision log: `projects/03_green_logistics/README.md`.
