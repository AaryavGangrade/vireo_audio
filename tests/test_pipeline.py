import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline import load_data, prepare_tickets, validate_input_keys, recommend_team, business_metrics
from src.config import SLA_MINUTES
ROOT = Path(__file__).resolve().parents[1]

def test_window_and_schema():
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    assert df["created_dt"].min() >= pd.Timestamp("2025-01-01")
    assert df["created_dt"].max() < pd.Timestamp("2026-07-01")
    assert df["ticket_id"].is_unique
    assert df["resolved_team"].notna().all()

def test_legacy_resolution_fix():
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    legacy = df[df["source_system"] == "legacy_fd"]
    valid = legacy["resolved_dt"].notna()
    assert (legacy.loc[valid, "resolved_dt"] >= legacy.loc[valid, "created_dt"]).all()

def test_sla_targets():
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    assert df["sla_target_minutes"].notna().all()
    assert set(df["sla_target_minutes"].unique()) <= set(SLA_MINUTES.values())

def test_policy_ownership_categories():
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    assert (df.loc[df.resolved_team == "Billing", "training_category"] == "Billing & Payments").all()
    assert (df.loc[df.resolved_team == "Logistics", "training_category"] == "Delivery & Shipping").all()


def test_missing_agent_key_fails_loudly():
    tickets, agents = load_data(ROOT / "data")
    bad = tickets.copy()
    bad.loc[0, "agent_id"] = "DOES_NOT_EXIST"
    try:
        validate_input_keys(bad, agents)
        assert False, "expected missing agent key to fail"
    except ValueError as e:
        assert "Unknown agent_id" in str(e)


def test_channel_aware_frontline_recommendation():
    assert recommend_team("Connectivity", "chat") == "Chat Frontline"
    assert recommend_team("Connectivity", "email") == "Email Frontline"
    assert recommend_team("Connectivity", "voice") == "Voice Frontline"
    assert recommend_team("Billing & Payments", "chat") == "Billing"


def test_billing_leakage_metric():
    """Verify that business_metrics captures the Billing → Logistics leakage."""
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    bm = business_metrics(df)
    bqa = bm["billing_queue_analysis"]
    assert bqa["billing_to_logistics_reroutes"] == 696
    assert bqa["billing_first_assigned_tickets"] == 2425
    assert bqa["billing_queue_leakage_rate"] == 0.287


def test_csat_impact_metric():
    """Verify CSAT analysis: handoff tickets should have lower CSAT than non-handoff."""
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    bm = business_metrics(df)
    cx = bm["customer_experience"]
    assert cx["avg_csat_no_transfer"] > cx["avg_csat_with_transfer"], \
        "Handoff tickets should have lower CSAT"
    assert cx["csat_delta"] > 0, "CSAT delta should be positive (no-transfer minus with-transfer)"


def test_business_metrics_structure():
    """Verify business_metrics returns all required top-level sections."""
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    bm = business_metrics(df)
    required_sections = [
        "window_summary", "operational_friction", "billing_queue_analysis",
        "customer_experience", "financial_impact_inr", "service_levels"
    ]
    for section in required_sections:
        assert section in bm, f"Missing section: {section}"


def test_handoff_rate_uses_current_helpdesk_only():
    """Verify that handoff rate denominator is current-helpdesk tickets (not total window)."""
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    bm = business_metrics(df)
    # Handoff rate should be ~16.8%, NOT ~11.1% (which would indicate using total 11,641 as denominator)
    rate = bm["operational_friction"]["recorded_handoff_rate"]
    assert rate > 0.15, f"Handoff rate {rate} looks too low — may be using total tickets instead of current-helpdesk only"
    assert rate < 0.20, f"Handoff rate {rate} is unexpectedly high"


def test_missing_agent_column_fails_loudly():
    """Verify that agents table schema validation catches missing columns immediately."""
    tickets, agents = load_data(ROOT / "data")
    bad_agents = agents.drop(columns=["team"])
    try:
        validate_input_keys(tickets, bad_agents)
        assert False, "expected missing agent team column to fail"
    except ValueError as e:
        assert "agents.csv is missing required columns" in str(e)


def test_narrator_missing_keys_safe_fallback():
    """Verify that narrator static fallback gracefully handles empty or partial metrics dictionaries."""
    from src.narrator import _static_fallback
    # Empty dict
    res_empty = _static_fallback({})
    assert "Executive Briefing" in res_empty
    # None
    res_none = _static_fallback(None)
    assert "Executive Briefing" in res_none
    # Partial dict
    res_partial = _static_fallback({"operational_friction": {"recorded_handoffs": 500}})
    assert "500" in res_partial


def test_billing_leakage_detailed_breakdown():
    """Verify precise split of 658 resolved/closed vs 696 total assigned Billing->Logistics reroutes."""
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    bm = business_metrics(df)
    bqa = bm["billing_queue_analysis"]
    assert bqa["billing_to_logistics_resolved_closed"] == 658
    assert bqa["billing_to_logistics_open_pending"] == 38
    assert bqa["billing_to_logistics_total_assigned"] == 696
    assert bqa["billing_queue_leakage_rate_resolved_closed"] == 0.271
    assert bqa["billing_queue_leakage_rate_total_assigned"] == 0.287


def test_audit_strictly_out_of_sample():
    """Verify that train_production_model strictly excludes the 110 audit tickets and confirms zero leakage."""
    from src.pipeline import train_production_model
    tickets, agents = load_data(ROOT / "data")
    df = prepare_tickets(tickets, agents)
    model, audit_results = train_production_model(df)
    assert audit_results["is_strictly_out_of_sample"] is True
    assert audit_results["n"] == 110
    assert audit_results["training_tickets_excluded"] == 110
    assert audit_results["production_model_correct"] == 104
    assert audit_results["production_model_accuracy"] == 0.9455

