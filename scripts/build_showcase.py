"""Regenerate a static, dependency-free recruiter showcase from computed results."""

import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
results = ROOT / "artifacts/full"
retail, churn, logistics = [
    json.loads((results / f"{name}_summary.json").read_text())
    for name in ["retail", "churn", "logistics"]
]
docs = ROOT / "docs"
(docs / "assets").mkdir(exist_ok=True)
(docs / "reports").mkdir(exist_ok=True)
shutil.copy2(results / "portfolio_overview.png", docs / "assets/portfolio_overview.png")
for name in ["retail_case_study.md", "churn_model_card.md", "logistics_business_case.md"]:
    shutil.copy2(results / name, docs / "reports" / name)
html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Mohit Sunda's data analytics portfolio: Python, SQL, predictive modelling and business analysis.">
<title>Mohit Sunda | Analytics portfolio</title><style>
:root{--navy:#16324f;--teal:#087f8c;--muted:#526b7c;--paper:#f7fafb;--line:#dce7ed}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--navy);font:16px/1.65 system-ui,-apple-system,sans-serif}
a{color:var(--teal)}header,main,footer{max-width:1200px;margin:auto;padding:24px 32px}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line)}
.brand{font-weight:750;letter-spacing:.05em;font-size:14px}nav a{margin-left:24px;text-decoration:none;font-size:14px}.hero{padding:72px 0 42px;max-width:910px}.eyebrow{color:var(--teal);letter-spacing:.14em;font-size:12px;font-weight:750;text-transform:uppercase}
h1{font-size:clamp(36px,6vw,66px);line-height:1.08;letter-spacing:-.05em;margin:18px 0 25px}h2{font-size:30px;letter-spacing:-.03em}h3{font-size:24px;line-height:1.25;letter-spacing:-.025em}.lead{font-size:20px;color:var(--muted);max-width:760px}
.pills{display:flex;gap:9px;flex-wrap:wrap;margin:26px 0}.pill{padding:5px 11px;background:#e8f2f4;border-radius:25px;font-size:12px;font-weight:650}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.card{padding:30px;background:white;border:1px solid var(--line);border-radius:16px;display:flex;flex-direction:column}
.num{color:var(--teal);font-size:12px;font-weight:750;letter-spacing:.1em}.metric{font-size:38px;font-weight:750;letter-spacing:-.04em;margin-top:auto}.metric-label,.small{font-size:13px;color:var(--muted)}.card a{margin-top:24px;font-weight:700;text-decoration:none}.card p{color:var(--muted)}
section{padding:32px 0}.strip{background:var(--navy);color:white;border-radius:16px;padding:32px 36px;margin:40px 0}.strip p{color:#d7e6ee}.strip a{color:#b6f0ec}.chart{width:100%;height:auto;background:white;border:1px solid var(--line);border-radius:14px}.method{display:grid;grid-template-columns:1fr 1fr;gap:48px}.method li{margin:10px 0}.detail{background:white;border:1px solid var(--line);border-radius:14px;padding:28px 32px;margin:20px 0}.detail h3{margin:5px 0 15px}.detail p{max-width:900px}footer{border-top:1px solid var(--line);font-size:13px;color:var(--muted);margin-top:30px}
@media(max-width:800px){.grid,.method{grid-template-columns:1fr}header,main,footer{padding:20px}header{align-items:flex-start}nav a{margin-left:13px;font-size:12px}.hero{padding-top:45px}.card{padding:24px}.metric{margin-top:20px}.strip{padding:25px}.detail{padding:24px}}
</style></head><body>
<header><span class="brand">MOHIT SUNDA</span><nav aria-label="Main navigation"><a href="#projects">Projects</a><a href="#approach">Approach</a><a href="#evidence">Evidence</a></nav></header>
<main><div class="hero"><div class="eyebrow">Data analytics / business analysis</div><h1>Clear evidence.<br>Practical decisions.</h1>
<p class="lead">I connect Python, SQL and business analysis to answer commercial questions, test predictive models and examine operational trade-offs.</p>
<p>MSc Business Analytics and Consultancy, Heriot-Watt University. Completed with merit.</p>
<div class="pills"><span class="pill">Python</span><span class="pill">SQL / DuckDB</span><span class="pill">Power BI handoff</span><span class="pill">scikit-learn</span><span class="pill">Requirements &amp; change</span></div></div>
<section id="projects"><div class="eyebrow">Selected case studies</div><h2>Three questions. Three complete workflows.</h2><div class="grid">
<article class="card"><div class="num">01 / COMMERCIAL ANALYTICS</div><h3>UK retail performance</h3><p>Reconcile recorded revenue, inspect credit movements and distinguish customer activity from financial totals.</p><div class="metric">{{RETAIL_ROWS}}</div><div class="metric-label">historical public transaction rows</div><a href="#retail">Explore the case →</a></article>
<article class="card"><div class="num">02 / PREDICTIVE MODELLING</div><h3>Customer retention</h3><p>Compare baselines and build a capacity-aware review queue using a group-separated holdout.</p><div class="metric">{{AP}}</div><div class="metric-label">test average precision, public telecom data</div><a href="#retention">Inspect the model →</a></article>
<article class="card"><div class="num">03 / BUSINESS ANALYSIS</div><h3>Green logistics</h3><p>Evaluate lane consolidation choices against explicit budget and service constraints in a synthetic case.</p><div class="metric">256</div><div class="metric-label">discrete scenarios fully evaluated</div><a href="#logistics">Review the decision →</a></article></div></section>
<section id="approach"><div class="method"><div><div class="eyebrow">How I structure an analysis</div><h2>Make the result inspectable.</h2><p>Each case starts with a decision and ends with evidence, assumptions and an actionable next step.</p></div><div><ol><li>Define the question and metric boundaries.</li><li>Validate data and document exclusions.</li><li>Run reproducible analysis with a baseline.</li><li>Separate observed evidence from projected effects.</li><li>Recommend a measured next action.</li></ol></div></div></section>
<section id="evidence"><div class="eyebrow">Computed outputs</div><h2>Results with context.</h2><img class="chart" src="assets/portfolio_overview.png" width="2550" height="750" alt="Charts of complete-month retail net revenue, churn permutation importance and synthetic logistics emissions scenarios">
<article class="detail" id="retail"><div class="num">01 / UK RETAIL</div><h3>Revenue and customer activity need different scopes.</h3><p>The full source records <strong>£{{NET}}</strong> in net revenue after the documented duplicate and invalid-line policy. Unidentified customers account for <strong>{{UNKNOWN}}</strong> of gross positive sales, so their purchases remain in financial totals while customer cohorts use identified buyers only.</p><p class="small">Historical UK retailer, 2010–2011. Net recorded revenue is not profit. The final month is incomplete.</p><a href="reports/retail_case_study.md" download>Download the decision memo</a></article>
<article class="detail" id="retention"><div class="num">02 / CUSTOMER RETENTION</div><h3>Keep selection separate from final evaluation.</h3><p>A {{MODEL}} model selected on validation average precision scores <strong>{{AP}}</strong> on the held-out test set. Identical allowed-feature vectors stay in one partition. The highest-scoring 20% of test cases achieve <strong>{{LIFT}}×</strong> lift against test prevalence.</p><p class="small">Public Iranian telecom research data. Prediction is not treatment benefit. No production deployment or realised savings are claimed.</p><a href="reports/churn_model_card.md" download>Download the model card</a></article>
<article class="detail" id="logistics"><div class="num">03 / GREEN LOGISTICS</div><h3>Optimise within an explicit service and budget envelope.</h3><p>Across 6,000 generated shipments, the chosen scenario reduces illustrative emissions by <strong>{{REDUCTION}}</strong> for <strong>£{{COST}}</strong> additional modelled cost, while keeping the configured constraints.</p><p class="small">Entirely synthetic data. Distances, emissions factors and intervention effects are assumptions. The optimum covers eight binary lane choices only.</p><a href="reports/logistics_business_case.md" download>Download the business case</a></article></section>
<div class="strip"><div class="eyebrow" style="color:#9ddedc">Reproducible by design</div><h2>Code, tests and a working dashboard.</h2><p>The repository includes a packaged Python CLI, executable SQL, three notebooks, an interactive Streamlit app, an offline demo, data provenance, automated checks and deployment configuration.</p><p class="small" style="color:#d7e6ee">This static showcase presents evidence. Run the repository's Streamlit app to use filters, risk review controls and the scenario explorer.</p></div>
</main><footer>Mohit Sunda · Independent portfolio work, built with AI assistance. Public datasets: UCI Online Retail and Iranian Churn, CC BY 4.0. Logistics data: synthetic. Source attribution is retained in each memo.</footer></body></html>"""
replacements = {
    "RETAIL_ROWS": f"{retail['input_rows']:,}",
    "AP": f"{churn['test_metrics']['average_precision']:.3f}",
    "NET": f"{retail['net_revenue_gbp']:,.2f}",
    "UNKNOWN": f"{retail['unidentified_gross_sales_share']:.1%}",
    "MODEL": churn["selected_model"].replace("_", " "),
    "LIFT": f"{churn['lift_at_top_20_percent']:.2f}",
    "REDUCTION": f"{logistics['co2e_reduction_pct']:.1%}",
    "COST": f"{logistics['cost_increase_gbp']:,.2f}",
}
for key, value in replacements.items():
    html = html.replace("{{" + key + "}}", escape(value))
(docs / "index.html").write_text(html)
(docs / ".nojekyll").touch()
print(f"Built {docs / 'index.html'}")
