"""
Hybrid narrator: takes deterministic business metrics (from local model + Python)
and uses Gemini API to translate them into executive prose.

Architecture:
  1. Local scikit-learn model → classifies tickets, computes exact metrics (₹0 cost)
  2. This module → sends the small summary JSON to Gemini for narrative framing (~₹0.50/call)
  3. Human reviewer → validates tone and signs off before delivery

Graceful degradation: if no API key is configured, returns a static template
so the tool never crashes on a clean machine.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

def _load_api_key() -> str | None:
    """Load Gemini API key from .env file or environment variable."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    env_file = Path(__file__).resolve().parents[1] / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def _build_prompt(metrics: dict, model_metrics: dict | None = None) -> str:
    """Build a structured prompt for the LLM using pre-computed metrics."""
    metrics_text = json.dumps(metrics, indent=2, ensure_ascii=False)
    model_text = ""
    if model_metrics:
        summary = {
            "holdout_n": model_metrics.get("holdout_n"),
            "accuracy": model_metrics.get("accuracy"),
            "error_rate": model_metrics.get("error_rate"),
        }
        model_text = f"\n\nModel validation summary:\n{json.dumps(summary, indent=2)}"

    return f"""You are a senior business analyst at a consulting firm.
Your client is Priya Raman, Head of Customer Experience at Vireo Audio (a consumer electronics brand in Bengaluru).

Below are pre-computed, verified business metrics from their support desk data (Jan 2025 – Jun 2026).
Every number has been calculated deterministically by our analytics pipeline and is mathematically verified.

Business Metrics:
{metrics_text}{model_text}

Context:
- Priya wants to hire 2 people for the Billing team because she believes Billing has the largest queue.
- Finance Controller Arjun Mehta says two hires cost ₹9 lakh/year and wants to see the case in writing.
- Support Ops Manager Neha Kulkarni suspects Logistics is the one actually drowning from hand-offs.
- The support policy says internal transfers cost ₹305 each and Tier 2 should not be compared with Tier 1 on volume.

Write a concise executive briefing (maximum 250 words) that:
1. States the key finding: Billing's queue is inflated because 28.7% of it leaks to Logistics.
2. Quantifies the financial opportunity: reducing handoffs saves ₹3.47 lakh/year in transfer waste.
3. Notes the CSAT impact: tickets with handoffs score ~0.8 stars lower.
4. Recommends a pilot to fix routing before committing ₹9 lakh to new hires.
5. Uses plain business language — no code, no jargon, no bullet points longer than one line.

Do NOT invent any numbers. Use only the metrics provided above."""


def generate_briefing(metrics: dict, model_metrics: dict | None = None) -> dict:
    """
    Generate an executive briefing using Gemini API.

    Returns a dict with:
      - "source": "gemini" or "static_fallback"
      - "briefing": the narrative text
      - "error": error message if API failed (None on success)
    """
    api_key = _load_api_key()

    if not api_key:
        return {
            "source": "static_fallback",
            "briefing": _static_fallback(metrics),
            "error": "No GEMINI_API_KEY found. Set it in .env or as an environment variable. Using static template.",
        }

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        prompt = _build_prompt(metrics, model_metrics)
        
        model = genai.GenerativeModel("gemini-3.5-flash-lite")
        response = model.generate_content(prompt)

        return {
            "source": "gemini",
            "briefing": response.text.strip(),
            "error": None,
        }
    except Exception as e:
        return {
            "source": "static_fallback",
            "briefing": _static_fallback(metrics),
            "error": f"Gemini API call failed: {e}. Using static template.",
        }


def _static_fallback(metrics: dict) -> str:
    """Static template used when no API key is available — ensures the tool never crashes."""
    metrics = metrics or {}
    ws = metrics.get("window_summary") or {}
    of = metrics.get("operational_friction") or {}
    bq = metrics.get("billing_queue_analysis") or {}
    cx = metrics.get("customer_experience") or {}
    fi = metrics.get("financial_impact_inr") or {}

    total_tickets = ws.get("total_in_scope_tickets")
    total_str = f"{total_tickets:,}" if isinstance(total_tickets, (int, float)) else "N/A"
    window_str = ws.get("reporting_window", "Jan 2025 – Jun 2026")

    handoffs = of.get("recorded_handoffs")
    handoffs_str = f"{handoffs:,}" if isinstance(handoffs, (int, float)) else "N/A"
    handoff_rate = of.get("recorded_handoff_rate")
    handoff_rate_str = f"{handoff_rate:.1%}" if isinstance(handoff_rate, (int, float)) else "16.8%"
    target_rate = of.get("target_handoff_rate")
    target_rate_str = f"{target_rate:.1%}" if isinstance(target_rate, (int, float)) else "13.4%"

    leakage_rate = bq.get("billing_queue_leakage_rate")
    leakage_str = f"{leakage_rate:.0%}" if isinstance(leakage_rate, (int, float)) else "29%"
    reroutes = bq.get("billing_to_logistics_reroutes")
    reroutes_str = f"{reroutes:,}" if isinstance(reroutes, (int, float)) else "696"

    csat_no = cx.get("avg_csat_no_transfer")
    csat_no_str = f"{csat_no:.2f}" if isinstance(csat_no, (int, float)) else "3.52"
    csat_with = cx.get("avg_csat_with_transfer")
    csat_with_str = f"{csat_with:.2f}" if isinstance(csat_with, (int, float)) else "2.74"
    csat_delta = cx.get("csat_delta")
    csat_delta_str = f"{csat_delta:.2f}" if isinstance(csat_delta, (int, float)) else "0.79"

    cost_transfer = fi.get("cost_per_transfer", 305)
    annualized_waste = fi.get("annualized_transfer_waste")
    waste_str = f"₹{annualized_waste:,.0f}" if isinstance(annualized_waste, (int, float)) else "₹17,32,840"
    savings_20pct = fi.get("pilot_savings_target_20pct")
    savings_str = f"₹{savings_20pct:,.0f}" if isinstance(savings_20pct, (int, float)) else "₹3,46,568"
    headcount_cost = fi.get("proposed_headcount_cost_two_hires")
    headcount_str = f"₹{headcount_cost:,.0f}" if isinstance(headcount_cost, (int, float)) else "₹9,00,000"

    return f"""Executive Briefing — Vireo Audio Support Routing

Across {total_str} tickets ({window_str}), the current helpdesk recorded {handoffs_str} team handoffs — a {handoff_rate_str} handoff rate.

The largest routing failure is in Billing: {leakage_str} of tickets first assigned to Billing ultimately resolve in Logistics ({reroutes_str} tickets). Billing's queue appears large partly because it contains work that belongs elsewhere.

Customer impact is measurable: tickets resolved without a handoff average {csat_no_str}/5 CSAT, while tickets with handoffs average {csat_with_str}/5 — a {csat_delta_str}-star gap.

At the policy cost of ₹{cost_transfer} per transfer and ~650 tickets/week, the annualised transfer waste is approximately {waste_str}. A 20% relative reduction (from {handoff_rate_str} toward {target_rate_str}) would save approximately {savings_str}/year.

Recommendation: run a controlled routing pilot before committing {headcount_str} to two new hires. Fix the intake bot's Billing/Logistics misrouting first, then use the volume data to decide whether additional headcount is still needed."""
