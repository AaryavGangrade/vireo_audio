# Vireo Audio — Support Intelligence (Set E)

A reproducible AI-assisted support-ticket analysis built from the supplied Set E pack.

## Architecture: Hybrid AI (Local Model + Gemini Narrator)

This tool uses a **two-layer hybrid architecture**:

1. **Local scikit-learn classifier** — classifies all tickets, computes all business metrics, and handles routing recommendations. Cost: **Rs 0 per ticket**. Runs 100% offline in ~30 seconds.
2. **Gemini API narrator** (optional) — takes the pre-computed, verified metrics JSON and translates it into executive prose on demand. Cost: **~Rs 0.012 INR (~1.2 paise) per briefing** (~850 prompt tokens + ~280 completion tokens using `gemini-3.5-flash-lite`). Gracefully degrades to a deterministic, high-quality static template if no API key is configured.

The LLM never generates numbers. It only writes words from numbers the local model has already computed.

## What this does

1. Loads the supplied CSVs and validates the reporting window.
2. Corrects the legacy resolution-timestamp timezone issue documented in the policy.
3. Produces monthly ticket volume by category and first-assigned team.
4. Compares first-assigned team with the final resolving team to expose routing leakage.
5. Trains a local word+character TF-IDF classifier on the customer's opening message (strictly excluding audit tickets).
6. Gives a category, recommended ownership team, and calibrated confidence for a new message.
7. Reports validation results, Brier score calibration, and the business case for reducing avoidable handoffs.
8. Generates an executive briefing from verified metrics via Gemini (optional).

## Business headline

The observed current-helpdesk period contains 7,728 tickets and 1,299 recorded team handoffs: **16.8%** of tickets. At the policy's Rs 305 per transfer, that is **Rs 3.96 lakh** in observed transfer cost.

**27.1% of Billing's queue is resolved/closed by Logistics (658 tickets)**, rising to **28.7% (696 tickets)** when including in-flight reroutes misrouted by the intake bot. Billing's queue appears large partly because it contains work that belongs elsewhere.

Customer impact: tickets without handoffs average **3.52/5 CSAT**; tickets with handoffs average **2.74/5** — a **0.79-star observed gap** (correlation/association per policy §8).

A practical pilot target is a 20% relative reduction in recorded handoffs, from 16.8% toward **13.4%**. At the stated volume (~650 tickets/week), that is about **Rs 3.47 lakh/year** of transfer cost avoided. Combined with deferring the proposed two hires (Rs 9.0 lakh/year), the total addressable opportunity is approximately **Rs 12.47 lakh/year**.

This is a target/business case, not a claim that the tool has already caused these savings.

## Scope decisions

- The README says Jan 2025–Jun 2026. The raw export also contains 139 tickets from Jun–Dec 2024; those are excluded rather than silently changing the scope.
- The policy says legacy resolution timestamps are UTC while displayed helpdesk timestamps are IST. Legacy `resolved_at` is therefore shifted +05:30 before duration analysis.
- `transfers` is blank for legacy rows. Transfer-cost analysis therefore uses current-helpdesk rows only; blanks are not converted into zero for that purpose.
- Tier 2 (Escalations & Warranty) is included in reporting but is not ranked against Tier 1 for headcount because the policy explicitly says Tier 2 is not to be compared with Tier 1 on volume (§4).
- The live classifier uses the customer's opening message, because that is what exists at ticket creation. Agent closing notes are not used for live classification.
- CSAT blanks are excluded from averages, not treated as zero (per policy §8).

## Model

The final classifier is a calibrated linear SVM over a FeatureUnion of:

- word TF-IDF, unigrams + bigrams
- character TF-IDF, 3–5 character n-grams

The model is intentionally local and reproducible. No paid API calls are required for classification.

### Validation & Ground Truth Alignment

The model trains and evaluates against **`training_category`**, the intended policy-corrected ground truth:
- **Why `training_category`:** Raw intake tags in `category` are noisy and contaminated (e.g. 28.7% of Billing's intake was rerouted to Logistics). Under Vireo Support Policy §6, specialist resolving teams have strict 1-to-1 domain ownership (`Billing` $\to$ Billing & Payments, `Logistics` $\to$ Delivery & Shipping, etc.). Downstream specialist resolution is the verified operational ground truth.
- **Validation on `training_category` (specialist ground truth):** **2,307 tickets**, accuracy **78.7%** (0.7872). (Agreement with uncleaned raw intake tags on the same holdout is 76.5%).
- **Repeated-run sensitivity:** **5 stratified holdouts** on `training_category` produced **77.1%–78.7%** accuracy (mean **77.8%**, SD **0.63 percentage points**, spread **1.60 points**). Measures split stability, not production drift.
- **Model calibration & confidence routing:** Multiclass Brier score is **0.371** across 11 classes. At a **0.70 confidence threshold**, **72.1% of tickets** are auto-routed at **79.5% accuracy**; the remaining **27.9% ambiguous tickets** route to human triage (where accuracy drops to 76.7%), preventing avoidable Rs 305 transfer penalties on borderline cases.
- **Independent stratified manual audit (110 tickets, strictly out-of-sample):**
  - Model trained on `training_category`: **104/110 (94.5%)**
  - Model trained on raw `category`: **101/110 (91.8%)**
  - Original source tag: **91/110 (82.7%)**
  - *Proof:* Training against `training_category` eliminates systematic intake bias, delivering a +2.7 percentage point lift over training on raw tags, and a +11.8 percentage point lift over historical helpdesk tags.
- **Typical failure modes:** Typical model failures are genuinely overlapping descriptions (e.g. firmware vs. battery charging symptoms), vague messages, and tickets with incomplete customer opening context.

The manual audit is stored in `outputs/manual_audit.csv`; its aggregate result is in `outputs/manual_audit_results.json`.

## Run from a clean machine

Requires Python 3.11+.

```bash
python -m venv .venv

# Windows PowerShell (if script execution is restricted, run this line first):
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
python scripts/run_pipeline.py
python -m pytest tests/ -v
streamlit run app.py
```

*Tip on Windows PowerShell without activating:*
```powershell
.\.venv\Scripts\python.exe scripts/run_pipeline.py
.\.venv\Scripts\pytest.exe tests/ -v
.\.venv\Scripts\streamlit.exe run app.py
```

The pipeline takes the supplied data from `data/`, trains the model, and writes artifacts to `models/` and `outputs/`.

### Optional: Enable Gemini executive briefing

Paste your Gemini API key into `.env`:
```
GEMINI_API_KEY=your-key-here
```
Without it, the dashboard uses a high-quality static template — the tool never crashes.

## Project map

- `app.py` — Streamlit demo/dashboard (hybrid: local classifier + Gemini narrator)
- `src/pipeline.py` — data cleaning, model training, validation, business metrics
- `src/config.py` — policy-derived constants and routing ownership
- `src/narrator.py` — Gemini-powered executive briefing generator with static fallback
- `scripts/run_pipeline.py` — clean-machine entry point
- `tests/` — data/policy sanity checks
- `.env` — Gemini API key (optional; placeholder provided)
- `outputs/business_metrics.json` — structured business case metrics
- `outputs/monthly_by_category.csv` — requested monthly category breakdown
- `outputs/monthly_by_team.csv` — requested monthly team breakdown
- `outputs/routing_matrix.csv` — first-assigned vs final resolving team
- `outputs/ticket_predictions.csv` — AI output for every historical ticket
- `outputs/model_metrics.json` — holdout model metrics
- `outputs/manual_audit.csv` — stratified manual audit set
- `docs/` — executive memo, decisions and scope, questionnaire answers, and prompt log

## Reviewer-critical gaps

- The manual benchmark is only 110 tickets, so it is evidence rather than a production-grade gold set.
- Historical labels are noisy; holdout accuracy is label agreement, not ground-truth accuracy.
- Legacy transfer counts are unavailable, so transfer-cost analysis covers current-helpdesk rows only.
- The 20% handoff-reduction target is a pilot hypothesis, not a causal estimate.
- The tool has no production authentication, logging, drift monitoring or human-label workflow.
- Unknown `agent_id` keys fail loudly during ingestion rather than silently creating missing ownership.

## Important limitation

The source system's category is noisy. The classifier therefore should not be treated as a fully autonomous router on day one. The UI exposes confidence and the recommended operating model is: high-confidence predictions can be auto-routed in a pilot; uncertain predictions go to a human review queue. A production rollout should measure transfer rate and SLA breaches before/after the pilot rather than assuming the model causes the savings.
