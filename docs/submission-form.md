# Vireo Audio — Submission Questionnaire

## What did you build, and what business outcome does it move?
I built a reproducible support-intelligence tool that auto-categorises opening customer messages, recommends ownership teams, and exposes queue leakage between first-assigned and resolving teams.

It targets reducing Vireo's recorded handoff rate from **16.81% toward 13.4%** (a 20% relative reduction), saving **₹3.47 lakh/year** in avoidable transfer waste (1,299 handoffs @ ₹305/transfer at ~650 tickets/week). Crucially, it exposes that **658 tickets (27.13%)** first assigned to Billing were resolved by Logistics (**696 tickets / 28.70%** including open reroutes). Deferring two premature Billing hires (**₹9.0 lakh/year**) until routing is fixed yields a total addressable pilot opportunity of **₹12.47 lakh/year**. This is a pilot target, not an unsupported claim of realised causal savings.

## What does one run cost, and what would a month cost at Vireo's volume (~650 tickets/week)?
**₹0 in paid inference calls** for classification. The calibrated LinearSVC runs 100% locally and offline.
- **Classifier:** 650 tickets/week × 4.33 weeks ≈ 2,815 tickets/month × ₹0 = **₹0/month**.
- **Optional Gemini 3.5 Flash Lite executive briefing:** ~850 input + ~280 output tokens on pre-computed summary metrics = **₹0.012 INR (~1.2 paise) per run**, or **~₹0.05/month** at weekly reviews. Degrades to a deterministic static template at ₹0 if no key is provided.
- *(Excludes local compute/operator machine cost; no hosting specs were provided).*

## How do you know it works?
- **Ground Truth Alignment:** Evaluated against `training_category` (downstream resolving team per Support Policy §6), which corrects the 28.7% intake bot misrouting in Billing.
- **Holdout Evaluation:** 2,307 tickets (20% split) on `training_category`: **78.7% accuracy** (error: 21.3%; raw tag agreement: 76.5%).
- **Sensitivity:** 5 stratified holdout splits: **77.1%–78.7% accuracy** (mean **77.8%**, SD **0.63%**, spread **1.60%**).
- **Calibration & Routing:** Multiclass Brier score **0.371**. A 70% confidence threshold auto-routes **72.1% of tickets at 79.5% accuracy**; the remaining 27.9% ambiguous tickets route to human triage to prevent ₹305 transfer penalties.
- **Out-of-Sample Manual Audit (110 tickets):** Model trained on `training_category`: **104/110 = 94.5%**; Model trained on raw `category`: **101/110 = 91.8%**; Historical source tags: **91/110 = 82.7%**.
- **Common Errors:** Ambiguous cross-domain symptoms (firmware vs. battery hardware), vague `Other` messages, and opening text lacking details that only emerge during investigation.

## Did you change, narrow, or push back on the client's ask?
Yes. I delivered the requested monthly charts, but pushed back on "largest raw queue = two hires for Billing".
- **Why:** 27.1% of Billing's resolved queue (658 tickets; 696 total) was actually resolved by Logistics. Billing's queue is artificially swollen by front-door intake misroutes.
- **Policy:** Tier 2 cannot be compared with Tier 1 on volume (§4), and Finance requires written justification before committing ₹9L/year (§6).
- **Pivot:** Reframed the goal around fixing intake routing to cut handoffs toward 13.4% before adding headcount.

## What is wrong with what you are handing us?
- Manual audit is 110 tickets; a stratified exploratory evaluation sample, not an exhaustive production gold benchmark.
- Historical tags have ~17% noise; the 78.7% holdout accuracy measures agreement with policy-corrected specialist resolution, not an infallible benchmark.
- Model operates text-only on opening messages at ticket creation; cannot inspect attachments, order database state, or subsequent agent exchanges.
- The 20% handoff reduction (₹3.47L) is a pilot target hypothesis, not an observed causal treatment effect.
- Legacy Freshdesk rows lack transfer tracking; transfer costs reflect current helpdesk only.
- It is a pilot dashboard, lacking enterprise SSO, RBAC, and live telemetry drift monitoring.

## What did you deliberately leave out, and why that rather than something else?
I left out staffing-hours simulations, direct CSAT optimization, paid LLM classification, and 100% autonomous dark-launch routing.
- **Why:** The export lacks active handle times and shift schedules; CSAT has high voluntary response bias (~30% response rate); LLM APIs introduce recurring costs and uncalibrated probabilities. I prioritized queue leakage, out-of-sample validation, and confidence thresholds because they directly resolve the headcount vs. routing question.

## Anything you built or found that nobody asked for?
1. Identified and corrected the legacy UTC/IST resolution timestamp offset (+05:30) per policy §8.
2. First-assigned vs. resolving team routing matrix exposing the 27.1% Billing $\to$ Logistics leak.
3. Quantified Billing $\to$ Logistics leakage isolating 658 resolved/closed (27.1%) vs 696 total assigned (28.7%).
4. Confidence-calibrated triage routing (Brier score 0.371; 70% threshold).
5. Strict out-of-sample isolation of the 110 audit tickets during training to prove zero data leakage.
6. 14-test automated unit test suite enforcing data, schema, and policy invariants.

## What did you use AI for?
- **Tools:** ChatGPT (GPT-5.6 Luna) for architectural sounding board, code review, and memo drafting; Gemini 3.5 Flash Lite for on-demand executive text synthesis.
- **Where it helped:** Challenging the "hire for Billing" assumption, structuring the business case, and formulating calibration checks.
- **Wasted time / Threw away:** Early attempts at end-to-end LLM ticket classification; discarded due to hallucinations, high token costs, and uncalibrated probabilities in favor of a local calibrated LinearSVC.
- **Screen recording:** https://drive.google.com/file/d/1n4gMEOy-FGd49BkAFa-1ED1tYHe_GhNN/view?usp=drive_link

## Your Public Google Drive Link
https://drive.google.com/file/d/1n4gMEOy-FGd49BkAFa-1ED1tYHe_GhNN/view?usp=drive_link

## Someone picks this up on Monday and you are unreachable. The three things they need to know.
1. **How to run:** Run `pip install -r requirements.txt`, `python scripts/run_pipeline.py`, and `streamlit run app.py` (on Windows PowerShell, activate via `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\.venv\Scripts\Activate.ps1`, or call `.venv\Scripts\` directly). Put your Gemini API key in `.env` (or run without it for static fallback).
2. **Data truth vs. tags:** Do not trust raw source tags; historical tags have ~17% error. All numbers are computed deterministically by the local model; Gemini only formats verified metrics into text.
3. **The core business decision:** Run an intake routing pilot to cut the 16.8% handoff rate toward 13.4% and eliminate the ~27% Billing $\to$ Logistics misrouting before committing ₹9L to two hires based on uncleaned raw volume.

## Honest hours spent.
10

## Github Repo Link
https://github.com/AaryavGangrade/vireo_audio
