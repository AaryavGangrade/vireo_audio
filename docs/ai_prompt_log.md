# AI Collaboration & Prompt Engineering Log

This log documents how generative AI (ChatGPT / Claude) was used as an interactive pair-programming and thinking partner during the five-hour development of the Vireo Audio Support Intelligence system. 

The human candidate drove all architecture, data validation, and business decisions, using the LLM for exploratory code scaffolding, hypothesis testing, and iterative refinement.

---

## Turn 1: Initial Exploration & Queue Analysis

### Candidate Prompt:
> *"I'm working on a support desk dataset for Vireo Audio (consumer electronics brand in Bengaluru) covering Jan 2025 – Jun 2026. Priya Raman (Head of CX) wants to hire 2 new agents for Billing because she believes it's the largest queue. Let's write an initial data loading script in Python to inspect the ticket distributions across `category` and `assigned_team`."*

### AI Response & Initial Code:
* Generated pandas code loading `tickets.csv` and computing `value_counts()` on `assigned_team`.
* **AI's initial conclusion:** *"Billing is indeed one of the highest volume queues (2,425 tickets, ~20.8%), following Chat Frontline (26.0%). Hiring two agents for Billing seems justified by raw volume."*

### Candidate Correction / Push-Back:
> *"Hold on. Let's look deeper. In `tickets.csv`, we have both `assigned_team` (first assignment) and we can join `agents.csv` to see who actually resolved the ticket (`resolved_team`). Also read `support-policy.pdf` §6 on team ownership. Run a crosstab between first-assigned team and final resolving team. Are tickets actually staying in Billing?"*

### AI Refinement & Discovery:
* Computed the routing matrix:
  ```python
  pd.crosstab(df['assigned_team'], df['resolved_team'])
  ```
* **Discovery:** Out of 2,425 tickets first assigned to Billing, **696 tickets (28.7%) actually resolved in Logistics**!
* **Candidate Decision:** The problem isn't that Billing is understaffed; the intake bot is misrouting shipping delays into Billing. We must push back on the naive "hire 2 people for Billing" recommendation.

---

## Turn 2: Architecture & Cost Dilemma (The Hybrid Model Decision)

### Candidate Prompt:
> *"Now we need a machine learning classifier to recommend the right category and team for incoming customer messages. What model should we use?"*

### AI Response:
* Recommended using OpenAI `gpt-4o-mini` or fine-tuning an LLM to classify tickets via API calls.

### Candidate Correction / Push-Back:
> *"No, that violates two core requirements:*
> 1. *The project must run locally on a clean machine without paid API keys.*
> 2. *Vireo handles ~650 tickets/week (~2,800/month). Calling an external LLM for every message introduces recurring SaaS bills, network latency (1-2s/ticket), and downtime risks.*
> 
> *Instead, let's build a **Hybrid Model**:*
> - *Layer 1 (The Engine): A local, zero-cost `scikit-learn` classifier (TF-IDF + Calibrated Linear SVM). Fast (2ms), offline, ₹0.*
> - *Layer 2 (The Narrator): An optional Gemini API layer (`gemini-3.5-flash-lite`) that ONLY takes our pre-computed, verified business metrics JSON and writes an executive briefing for Priya. If no API key is provided, gracefully fall back to a static template so the app never crashes."*

### AI Implementation:
* Implemented `src/pipeline.py` with `FeatureUnion` (word + char n-grams) and `CalibratedClassifierCV(LinearSVC)`.
* Created `src/narrator.py` with the Gemini narrator and `_static_fallback` graceful degradation.

---

## Turn 3: Catching Hidden Data Quality Traps

### Candidate Prompt:
> *"When I compute ticket resolution duration (`resolved_at - created_at`), thousands of tickets from early 2025 show negative resolution times! Why is this happening?"*

### AI Response & Policy Lookup:
* Investigated timestamps and checked `support-policy.pdf` §8:
  * Freshdesk (`legacy_fd`) stored resolution timestamps in **UTC**.
  * The current helpdesk displays timestamps in **IST (UTC+05:30)**.
  * Naively subtracting them causes 2,379 tickets to appear to resolve *before* they were created.
* Wrote the fix:
  ```python
  legacy = t["source_system"].eq("legacy_fd")
  t.loc[legacy, "resolved_dt"] = t.loc[legacy, "resolved_dt"] + pd.DateOffset(hours=5, minutes=30)
  ```

### Candidate Follow-up on Transfers:
> *"Also check the `transfers` column. There are 3,913 NaN values in legacy rows. If we do `fillna(0)`, the handoff rate drops to 11.1%. What does the email say about this?"*
* **Resolution:** The email thread confirmed Freshdesk didn't track transfers. Candidate mandated that transfer cost analysis must use **current helpdesk rows only (7,728 tickets)**, revealing the true **16.8% handoff rate** (1,299 handoffs).

---

## Turn 4: Model Validation & The "82% Accuracy" Investigation

### Candidate Prompt:
> *"I ran train/test split on historical `category`. The holdout accuracy is 81.88%. Can we tune hyperparameters to get this to 95%?"*

### AI Response & Analysis:
* Ran grid search on SVM `C` and n-gram ranges; accuracy plateaued around 82.5%.
* Inspected misclassified samples.
* **Finding:** The model was often predicting `Charging & Battery`, but the CSV tag was `App & Firmware`. Upon reading the customer messages (*"earbuds won't charge in case"*), the **model was right and the CSV tag was wrong**!

### Candidate Decision:
> *"The historical labels have significant human error. We cannot treat the CSV tags as ground truth. Let's do two things:*
> 1. *Conduct an independent, stratified **Manual Audit of 110 tickets** to evaluate both the model and the source tags against human ground truth.*
> 2. *Implement a **70% confidence threshold**. If the model is uncertain, don't guess — route to Human Review to avoid ₹305 transfer penalties."*

### Results Produced:
* **Manual Audit:** Source tags were only **82.7%** correct. The model was **94.5%** correct (104/110).
* **Repeated-Run Sensitivity:** Ran 5 random holdout seeds (7, 19, 42, 73, 101) to verify stability (mean 82.2%, spread 1.73 points).

---

## Turn 5: Financial Modeling & Executive Framing

### Candidate Prompt:
> *"Let's ground the business case in actual policy figures. Arjun Mehta (Finance) says 2 hires cost ₹9 Lakhs/year. The policy says internal transfers cost ₹305 each. Let's calculate the financial opportunity of reducing handoffs by 20% and add CSAT impact."*

### AI Implementation & Math Verification:
* Current handoffs: 16.8% of tickets.
* At 650 tickets/week (33,800/year):
  $$\text{Annual Transfer Waste} = 16.8\% \times 33,800 \times \text{₹}305 \approx \text{₹}17.33\text{ Lakhs/year}$$
* A 20% relative reduction (down to 13.4%) saves:
  $$\text{₹}17.33\text{ Lakhs} \times 20\% = \mathbf{\text{₹}3.47\text{ Lakhs/year in direct waste}}$$
* CSAT analysis:
  * Non-transferred tickets: **3.52 / 5.0**
  * Transferred tickets: **2.74 / 5.0** (Steep **0.79 star penalty**)
* Combined opportunity: Avoid premature ₹9 Lakhs hiring + ₹3.47 Lakhs transfer savings = **₹12.47 Lakhs total first-year financial opportunity**.

---

## Summary of Discarded Approaches

Throughout the pair-programming session, several initial AI suggestions were explicitly evaluated and rejected:
1. **Discarded:** Paid LLM runtime API dependency for ticket classification (rejected due to cost, latency, and clean-machine failure).
2. **Discarded:** Staffing-hours simulation based on resolution duration (rejected because resolution time includes idle customer wait time, not active agent handle time).
3. **Discarded:** Blind auto-routing on all tickets (rejected in favor of a 70% confidence guardrail with a Human Review fallback).
4. **Discarded:** Treating historical tags as ground truth (rejected after manual audit exposed 17.3% error rate in source tags).
