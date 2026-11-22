# Verification record

Local verification date: 22 November 2026. Python 3.12.14.

## Completed

| Check | Observed result |
| --- | --- |
| Full public source acquisition | Original retail workbook and churn CSV downloaded, archive/member hashes recorded |
| Full build | Completed for 541,909 retail input rows, 3,150 churn rows and 6,000 synthetic shipments |
| Offline demo build | Completed using generated synthetic inputs, with network access prohibited in the integration test |
| Financial audit | Input/exclusion/retention counts reconcile. Credits stay in net revenue. Missing-ID sales stay in totals |
| Churn partitions | No identical allowed-feature group crosses train, validation and test partitions |
| Batch inference | Five-row example scored with the locally generated model |
| Optimisation | All 256 defined choices evaluated, optimum checked against every feasible candidate |
| Static checks | `ruff check .` and `ruff format --check .` passed |
| Automated tests | 21 tests passed, including all four dashboard views and interaction edge cases |
| Notebook execution | All three notebooks executed with actual Python output and embedded charts |
| Static showcase | Generated from the full computed results |

## Notebook execution method

The default runner executes ordinary Python code cells in process, evaluates their
final expressions and captures actual text/HTML/PNG outputs. It fails on a Python
exception. This avoids kernel socket restrictions in this workspace. It does not
invent results or copy in prewritten cell output. Standard notebook files remain
compatible with Jupyter. `--engine jupyter` enables the separate-kernel path, which
could not run in this restricted environment. IPython magics and shell cells are
not supported by the in-process runner. These notebooks contain ordinary Python.

## Not verified here

- Hosted Actions and Pages must be checked against their actual GitHub run or deployment results. Account connection alone does not establish either outcome.
- Pixel-level browser inspection. Browser process sockets are restricted. Dashboard
  execution and widget changes were verified through Streamlit's AppTest framework.
- Docker image runtime. A Docker engine is unavailable in this workspace.
- Native Power BI Desktop rendering or M/DAX execution. The supplied files are a
  documented handoff. Python/SQL metric calculations were executed.

The repository has no fabricated CI badge, deployment URL or claim of real
customer interventions, realised savings or production model performance.

Public snapshot review: actual customer-level exports and raw reference inputs are excluded. Dashboard views use aggregate segment and capacity metrics.
