"""Interactive portfolio. Launch with `streamlit run streamlit_app.py`."""

import sys
from pathlib import Path

# Also supports Streamlit Cloud, where requirements install dependencies but do
# not install this local src-layout package as an editable distribution.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st  # noqa: E402

from portfolio.common import ROOT  # noqa: E402
from portfolio.dashboard import home  # noqa: E402

st.set_page_config(page_title="Mohit Sunda | Analytics portfolio", page_icon="📊", layout="wide")
st.markdown(
    """<style>
  .block-container {padding-top:2.2rem; max-width:1440px}
  [data-testid="stMetric"] {background:white;border:1px solid #dce7ed;border-radius:12px;padding:18px}
  [data-testid="stMetricLabel"] {color:#597184}
  h1,h2,h3 {letter-spacing:-.025em}
  [data-testid="stSidebar"] {border-right:1px solid #dce7ed}
</style>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### MOHIT SUNDA")
    st.caption("DATA ANALYTICS · BUSINESS ANALYSIS")
    source = st.selectbox(
        "Retail data run",
        ["full", "demo"],
        format_func=lambda v: "Full UCI dataset" if v == "full" else "Synthetic offline demo",
        key="retail_source",
    )
    st.caption(
        "Full mode shows public-source aggregate results. Demo mode generates synthetic inputs. Logistics is synthetic in both modes."
    )
    st.divider()

base = ROOT / "artifacts" / source
if not (base / "run_manifest.json").exists():
    st.info(f"Build the data first: portfolio build --source {source}")
    st.stop()


st.navigation(
    [
        st.Page(home, title="Portfolio overview", icon="🏠", default=True),
        st.Page("app_pages/retail.py", title="UK retail performance", icon="🛒"),
        st.Page("app_pages/churn.py", title="Customer retention", icon="📈"),
        st.Page("app_pages/logistics.py", title="Green logistics", icon="🚚"),
    ]
).run()
