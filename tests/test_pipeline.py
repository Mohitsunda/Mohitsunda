import json

import pandas as pd
import pytest

from portfolio.cli import main


def test_offline_build_and_batch_scoring(tmp_path, monkeypatch):
    from portfolio.common import ROOT

    def no_network(*args, **kwargs):
        raise AssertionError("Demo must not access the network")

    monkeypatch.setattr("urllib.request.urlopen", no_network)
    output = tmp_path / "demo"
    main(["build", "--source", "demo", "--output", str(output)])
    summary = json.loads((output / "retail_summary.json").read_text())
    assert summary["input_rows"] > 1000
    assert (output / "portfolio_overview.png").stat().st_size > 1000
    assert (output / "retail_case_study.md").exists()
    main(
        [
            "score",
            "--model",
            str(output / "churn_model.joblib"),
            "--input",
            str(ROOT / "examples/scoring_input.csv"),
            "--output",
            str(tmp_path / "scored.csv"),
        ]
    )
    scores = pd.read_csv(tmp_path / "scored.csv")
    assert len(scores) == 5
    assert scores.risk_probability.between(0, 1).all()
    segments = pd.read_csv(output / "retail_segments.csv")
    assert set(segments.columns) == {"segment", "customers", "gross_sales_gbp"}
    capacity = pd.read_csv(output / "churn_capacity_summary.csv")
    assert len(capacity) == 10
    assert "source_row" not in capacity.columns


def test_public_snapshot_excludes_individual_customer_exports():
    import subprocess

    from portfolio.common import ROOT

    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    forbidden = ("/retail_rfm.csv", "/churn_test_predictions.csv", "/churn_split_assignments.csv")
    assert not any(p.startswith("data/reference/") or p.endswith(forbidden) for p in tracked if p)


def test_dashboard_initial_render_and_demo_selection():
    from streamlit.testing.v1 import AppTest

    from portfolio.common import ROOT

    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    assert not app.exception
    assert "From messy data" in app.title[0].value
    app.sidebar.selectbox[0].select("demo").run()
    assert not app.exception
    assert app.metric[0].label == "Retail transaction rows"


@pytest.mark.parametrize(
    "page,title",
    [
        ("retail", "UK retail performance"),
        ("churn", "Customer retention intelligence"),
        ("logistics", "Green logistics decision lab"),
    ],
)
def test_every_dashboard_page_renders(page, title):
    from streamlit.testing.v1 import AppTest

    from portfolio.common import ROOT

    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    app.switch_page(f"app_pages/{page}.py").run()
    assert not app.exception
    assert app.title[0].value == title
    if page == "retail":
        app.multiselect[0].set_value([]).run()
        assert not app.exception
        assert "No records" in app.info[0].value
    elif page == "logistics":
        app.slider[1].set_value(95).run()
        assert not app.exception
        assert "No scenario" in app.warning[0].value
    else:
        app.slider[0].set_value(30).run()
        assert not app.exception
