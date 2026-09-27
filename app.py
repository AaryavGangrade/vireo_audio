from pathlib import Path
import json
import pandas as pd
import streamlit as st
import joblib
from src.pipeline import load_data, prepare_tickets, recommend_team
from src.narrator import generate_briefing
from src.config import (CATEGORY_TO_TEAM, TARGET_HANDOFF_RATE, WEEKLY_TICKET_VOLUME,
                        AUTO_ROUTE_CONFIDENCE, HEADCOUNT_COST_TWO_HIRES_INR)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MODEL = ROOT / "models/vireo_category_model.joblib"

st.set_page_config(page_title="Vireo Audio Support Intelligence", layout="wide")
st.title("Vireo Audio — Support Intelligence")
st.caption("Set E | Jan 2025–Jun 2026 | Hybrid AI: Local classifier + Gemini executive narrator")

@st.cache_data
def load_prepared():
    tickets, agents = load_data(DATA)
    return prepare_tickets(tickets, agents)

@st.cache_resource
def load_model():
    return joblib.load(MODEL)

try:
    df = load_prepared()
    model = load_model()
except Exception as e:
    st.error("Run `python scripts/run_pipeline.py` first.")
    st.exception(e)
    st.stop()

metrics = json.loads((ROOT / "outputs/business_metrics.json").read_text())
mm = json.loads((ROOT / "outputs/model_metrics.json").read_text())

# --- Top-level KPI cards ---
ws = metrics["window_summary"]
of = metrics["operational_friction"]
bq = metrics["billing_queue_analysis"]
fi = metrics["financial_impact_inr"]
cx = metrics["customer_experience"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Tickets", f"{ws['total_in_scope_tickets']:,}")
c2.metric("Handoff Rate", f"{of['recorded_handoff_rate']:.1%}")
c3.metric("Billing → Logistics", f"{bq['billing_to_logistics_reroutes']:,} ({bq['billing_queue_leakage_rate']:.0%})")
c4.metric("Manual Audit", "94.5% / 110")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Transfer Waste / Year", f"₹{fi['annualized_transfer_waste']:,.0f}")
c6.metric("Pilot Savings Target", f"₹{fi['pilot_savings_target_20pct']:,.0f}")
c7.metric("CSAT (No Transfer)", f"{cx['avg_csat_no_transfer']}/5")
c8.metric("CSAT (With Transfer)", f"{cx['avg_csat_with_transfer']}/5 (↓{cx['csat_delta']})")

# --- 1. Monthly volume charts ---
st.subheader("1. Monthly Volume")
view = st.radio("Break down by", ["Category", "First-assigned team"], horizontal=True)
chart = pd.crosstab(df.month, df.category if view == "Category" else df.assigned_team)
st.bar_chart(chart)

# --- 2. Routing leakage matrix ---
st.subheader("2. Routing Leakage (First-Assigned vs. Resolving Team)")
st.dataframe(pd.crosstab(df.assigned_team, df.resolved_team), use_container_width=True)
st.info(
    f"**Business target:** reduce handoffs from {of['recorded_handoff_rate']:.1%} toward "
    f"{of['target_handoff_rate']:.1%}. A 20% relative reduction saves ~₹{fi['pilot_savings_target_20pct']:,.0f}/year "
    f"in transfer waste, and avoids a premature ₹{HEADCOUNT_COST_TWO_HIRES_INR:,.0f} hiring commitment."
)

# --- 3. AI Classifier (live demo) ---
st.subheader("3. Try the Classifier")
channel = st.selectbox("Channel", ["chat", "email", "voice", "social"], index=0)
message = st.text_area("Paste a customer's opening message", height=140)
if st.button("Classify") and message.strip():
    p = model.predict_proba([message])[0]
    idx = p.argmax()
    category = model.classes_[idx]
    confidence = float(p[idx])
    team = recommend_team(category, channel)
    if confidence < AUTO_ROUTE_CONFIDENCE:
        st.warning(f"**{category}** → Human review ({confidence:.0%} confidence; below {AUTO_ROUTE_CONFIDENCE:.0%} threshold)")
    else:
        st.success(f"**{category}** → {team} ({confidence:.0%} confidence)")
    st.dataframe(
        pd.DataFrame(
            sorted(zip(model.classes_, p), key=lambda x: x[1], reverse=True)[:5],
            columns=["Category", "Probability"]
        ),
        hide_index=True
    )

# --- 4. AI Executive Briefing (Gemini hybrid) ---
st.subheader("4. AI Executive Briefing (Powered by Gemini)")
st.caption("Local model computes exact numbers → Gemini translates them into executive prose.")
if st.button("Generate Executive Briefing"):
    with st.spinner("Generating briefing from verified metrics..."):
        result = generate_briefing(metrics, mm)
    if result["error"]:
        st.warning(f"⚠️ {result['error']}")
    st.markdown(f"**Source:** `{result['source']}`")
    st.markdown("---")
    st.markdown(result["briefing"])

# --- 5. Data quality & scope ---
st.subheader("5. Data Quality & Scope Decisions")
st.markdown(
    "- **139 tickets** before the README's Jan 2025 start are excluded.\n"
    "- Legacy resolution timestamps are UTC and are converted to IST (+05:30) before duration analysis.\n"
    "- Transfers are blank on legacy rows, so transfer-cost analysis uses the current helpdesk only.\n"
    "- Tier 2 is shown for completeness but is not used in a Tier-1 headcount ranking (per policy §6).\n"
    "- CSAT blanks are excluded from averages, not treated as zero (per policy §8)."
)

with st.expander("Validation, repeatability and known gaps"):
    st.write(f"**Historical-tag holdout:** {mm['holdout_n']:,} tickets; accuracy {mm['accuracy']:.1%}.")
    rm_path = ROOT / "outputs/repeated_run_metrics.json"
    if rm_path.exists():
        rm = json.loads(rm_path.read_text())
        st.write(
            f"**Five holdout splits:** {rm['min_accuracy']:.1%}–{rm['max_accuracy']:.1%}; "
            f"mean {rm['mean_accuracy']:.1%}; SD {rm['std_accuracy']:.2%}; "
            f"spread {rm['range_accuracy']:.2%}."
        )
    st.write("**Independent manual audit:** 104/110 = 94.5% model accuracy vs 91/110 = 82.7% source-tag accuracy.")
    st.markdown(
        "**Known evidence gaps:** only 110 manually reviewed tickets; historical labels are noisy; "
        "legacy transfer counts are unavailable; the handoff savings target is a pilot hypothesis, "
        "not a causal estimate; production drift/authentication/monitoring are not implemented."
    )
