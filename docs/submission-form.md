# Vireo Audio — Submission Questionnaire

## What did you build, and what business outcome does it move?

I built a reproducible support-intelligence tool that auto-categorises opening messages, recommends an ownership team, shows monthly category/team volume, and exposes first-assigned vs final-resolving-team leakage.

The business target is to reduce current-helpdesk recorded handoffs from **16.81% toward 13.4%** — a 20% relative reduction. At Vireo's stated ~650 tickets/week and the policy's Rs 305/transfer cost, the annualised transfer-cost opportunity is **Rs 3.47 lakh/year**. When combined with deferring the proposed two hires (Rs 9.0 lakh/year) until intake routing is clean, the total pilot addressable opportunity is **Rs 12.47 lakh/year**. This is a pilot target, not a claimed realised saving.

A specific focal opportunity is Billing queue leakage: **658 tickets** first assigned to Billing were resolved or closed by Logistics (27.13%), rising to **696 total tickets** (28.70%) when including open/pending reroutes.

## What does one run cost, and what would a month cost at Vireo's volume (~650 tickets/week)?

The architecture uses a **hybrid cost model**:

1. **Core Ticket Classification & Analytics (Local Scikit-Learn):**
   - **Rs 0 in paid inference calls.** The calibrated linear SVM and TF-IDF pipeline runs 100% locally and offline.
   - 650 tickets/week × 4.33 weeks/month ≈ 2,815 tickets/month.
   - 2,815 tickets × Rs 0 = **Rs 0/month in classifier inference charges**.

2. **Optional Executive Briefing (Gemini 3.5 Flash Lite):**
   - The LLM is used strictly on demand to translate pre-computed summary metrics (JSON) into executive prose. It never processes raw ticket streams.
   - Token footprint per briefing: **~850 prompt tokens + ~280 completion tokens**.
   - At standard Gemini 3.5 Flash Lite rates ($0.075 / 1M input, $0.30 / 1M output):
     - Input: 850 / 1,000,000 × $0.075 = $0.00006375
     - Output: 280 / 1,000,000 × $0.30 = $0.000084
     - Total per briefing run: **~$0.000148 USD ≈ Rs 0.012 INR (~1.2 paise)**.
   - At weekly cadence (4 executive runs/month): **~Rs 0.05 INR/month (< 5 paise/month)**.
   - If `GEMINI_API_KEY` is omitted or unavailable, the application gracefully degrades to a deterministic, high-quality static briefing template at **Rs 0**.

This excludes local compute/operator machine cost because no hosting specifications were provided.

## How do you know it works?

- **Why `training_category` is the intended corrected ground truth:**
  - The raw `category` field contains unverified front-door tags set by customers or the initial intake bot/IVR. As demonstrated by the data, it is severely contaminated: **28.7% of tickets** first assigned to Billing (696 tickets) were actually delivery issues and had to be rerouted to Logistics.
  - Vireo's Support Policy (§6 "Team Ownership by Category") defines strict 1-to-1 domain ownership for specialist teams: `Billing` $\to$ Billing & Payments, `Logistics` $\to$ Delivery & Shipping, `Returns Desk` $\to$ Returns & Refunds, and `Escalations & Warranty` $\to$ Warranty & Repair.
  - When a ticket is investigated and resolved by a specialist team (`resolved_team`), their assignment reflects the **substantive, verified domain** of the issue. Therefore, `training_category` programmatically corrects noisy intake tags using downstream specialist resolution. Frontline generalist channels handle cross-cutting triage, so their historical category is preserved.
- **Validation against `training_category` (Intended Corrected Ground Truth):**
  - **Holdout evaluation:** **2,307 tickets**, accuracy **78.7%** (0.7872), error rate 21.3%. This measures agreement with downstream specialist resolution. (On the same holdout, agreement with uncleaned raw intake tags is 76.5%).
  - **Repeated-run sensitivity:** Five stratified holdouts on the same 2,307-ticket test size produced **77.1%–78.7% accuracy** (mean **77.8%**, SD **0.63 percentage points**, spread **1.60 points**). This confirms stability across random splits, not production drift.
  - **Model calibration & confidence routing:** Multiclass Brier score is **0.371** across the 11 classes. At a **0.70 confidence threshold**, **72.1% of tickets** are auto-routed at **79.5% accuracy**; the remaining **27.9% ambiguous tickets** (accuracy drops to 76.7%) route to human triage, directly preventing Rs 305 transfer penalties on borderline cases.
- **Empirical Proof via Independent Stratified Manual Audit (110 tickets, strictly out-of-sample):**
  - Model trained on `training_category`: **104/110 = 94.5%**
  - Model trained on raw `category`: **101/110 = 91.8%**
  - Original historical source tag: **91/110 = 82.7%**
  - *Conclusion:* Training against `training_category` removes systematic intake bias, generating a **+2.7 percentage point lift** in true real-world accuracy over training on noisy tags, and a **+11.8 percentage point lift** over historical helpdesk tags.
- **Error distribution:** The remaining failure modes are ambiguous cross-domain symptoms (e.g. firmware vs. hardware battery faults), vague messages classified under `Other`, and tickets where customer opening text lacked details that only emerged during agent investigation.

## Did you change, narrow, or push back on the client's ask?

Yes. I kept the requested monthly category/team chart, but I did not treat "largest raw queue gets two hires" as the final business conclusion.

The export shows Billing at 20.8% of first-assigned tickets, while Chat Frontline is 26.0%; Billing is the largest **specialist/non-Frontline** team. More importantly, **658 tickets** first assigned to Billing were resolved/closed by Logistics (27.13%), expanding to **696 tickets** (28.70%) with in-flight reroutes. The policy says Tier 2 should not be compared with Tier 1 on volume (§4), and Finance says two hires are about Rs 9 lakh/year and requires the volume case in writing (§6).

I therefore reframed the measurable outcome around reducing avoidable handoffs before committing the hires. That is why the tool includes the routing matrix, high-confidence routing thresholds, and a 13.4% handoff-rate pilot target.

## What is wrong with what you are handing us?

- The manual audit is 110 tickets; while strictly out-of-sample, it is a stratified evaluation sample, not an exhaustive production gold benchmark.
- Historical category labels remain noisy, so the 81.9% holdout score reflects agreement with historical tagging rather than absolute ground truth.
- The model classifies opening text at ticket creation and cannot inspect attachments, order database state, or subsequent agent exchanges.
- The 20% handoff-reduction target is an operational pilot hypothesis, not an empirically observed causal treatment effect.
- Legacy transfer data is unrecorded, so transfer-cost calculations reflect the current-helpdesk period only.
- The application is a pilot intelligence dashboard, not a SOC-2 production deployment with SSO, role-based access control, or live telemetry drift detection.

## What did you deliberately leave out, and why that rather than something else?

I left out a full customer/order segmentation analysis, a staffing-hours simulation, deep CSAT optimisation, a paid LLM classifier dependency, and autonomous dark-launch routing.

I chose those cuts because they either lack reliable data in the export (e.g. absent shift schedules, unlinked order states) or add brittle external API costs without improving the core headcount/routing question. I prioritized out-of-sample validation, monthly breakdowns, routing leakage, and safe threshold routing because each directly addresses the decision criteria.

## Anything you built or found that nobody asked for?

Yes:

1. A data-quality check that identified and corrected the legacy UTC/IST resolution-timestamp offset (+05:30).
2. A first-assigned vs final-resolving-team routing matrix exposing queue leakage.
3. Quantified Billing → Logistics leakage isolating 658 resolved/closed (27.1%) vs 696 total assigned (28.7%).
4. Confidence-calibrated triage routing (Brier score 0.315; 0.70 threshold for auto-routing vs. human review).
5. A strictly out-of-sample audit evaluation framework with zero data leakage.
6. A 14-test automated unit test suite enforcing data, schema, and policy invariants.

## What did you use AI for?

I used **ChatGPT (GPT-5.6 Luna)** as a development and review assistant to stress-test the problem framing, critique the "largest queue = hires" assumption, design the validation protocol, review scope boundaries, and refine the memo.

The production software architecture implements a **hybrid model**:
- **Local scikit-learn classifier** (calibrated LinearSVC + word/char TF-IDF) handles all ticket classification and metric calculation locally at **Rs 0 per ticket**.
- **Gemini API (`gemini-3.5-flash-lite`)** synthesizes verified aggregate metrics into executive prose on demand at **~Rs 0.012 INR (~1.2 paise) per run**.

The initial prototype considered a basic logistic regression model, which was upgraded to a calibrated linear SVM for superior decision-boundary sharpness and probabilistic reliability. An end-to-end LLM classifier was explicitly rejected because classifying ~2,815 tickets/month via API would introduce unnecessary recurring operational costs, latency, vendor lock-in, and uncalibrated classification probabilities.

## Your Public Google Drive Link

<!-- CANDIDATE ACTION: Upload final ZIP + 3-minute screen recording to Google Drive and paste URL below -->
**Drive URL:** *(pending — to be pasted before final submission)*

## Someone picks this up on Monday and you are unreachable. The three things they need to know.

1. **How to run:** Run `pip install -r requirements.txt`, then `python scripts/run_pipeline.py`, then `streamlit run app.py` (on Windows PowerShell, activate with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\.venv\Scripts\Activate.ps1`, or call `.venv\Scripts\` directly). To enable the Gemini executive briefing, paste your API key into `.env`. If no key is provided, the dashboard functions completely via an offline deterministic fallback.
2. **Data truth vs. tags:** Do not treat source category tags as ground truth. Historical tags have an estimated ~17% error rate; the manual audit and routing matrix exist specifically because the historical tags are noisy. All numbers are computed deterministically by the local pipeline; Gemini only formats verified metrics into text.
3. **The core business decision:** The immediate decision is whether to run an intake routing pilot targeting a reduction of the 16.8% handoff rate toward 13.4% (especially eliminating the ~27% Billing → Logistics misrouting), saving up to Rs 3.47L in transfer waste and deferring Rs 9.0L in salary commitment, rather than approving two hires based on uncleaned raw queue volume.
