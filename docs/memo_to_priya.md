# To: Priya Raman, Head of Customer Experience
## Subject: Vireo support routing and headcount — Set E

### The decision in one minute

I would not use raw ticket volume alone as the headcount rule. The data supports a more actionable finding: **27.1% of Billing's queue is resolved by Logistics (658 tickets)**, rising to **28.7% (696 tickets)** when including open and pending routing. The intake bot is systematically misrouting shipping issues into the payments queue.

The current helpdesk recorded **1,299 team handoffs across 7,728 tickets**, or **16.8%**. At the policy cost of Rs 305 per transfer, that is **Rs 3.96 lakh** of observed transfer cost over the current-system period.

### What it costs Vireo — in money and in customer experience

At roughly 650 tickets/week, a 20% relative reduction in handoffs would save about **Rs 3.47 lakh/year** in transfer cost alone. Combined with deferring the two hires (Rs 9 lakh/year per Arjun's estimate), the total addressable opportunity is approximately **Rs 12.5 lakh/year**.

It also correlates with customer experience: tickets resolved without a handoff average **3.52/5 CSAT**, while tickets with handoffs average **2.74/5** — an observed **0.79-star gap**. Addressing routing eliminates transfer friction where customer satisfaction is currently lowest.

### What the data says

Across Jan 2025–Jun 2026 there are 11,641 in-scope tickets. Chat Frontline is the largest first-assigned team at 26.0%; Billing is the largest specialist/non-Frontline team at 20.8%, followed by Logistics at 16.4%. The email thread's earlier 22% Billing figure does not match this export.

The policy also says Tier 2 is measured in days and should not be compared with Tier 1 on tickets closed, so I have not used raw Tier 2 volume to decide headcount.

### What I built

A hybrid AI-assisted tool that:

- produces the requested monthly category and team breakdowns;
- compares first-assigned and final resolving teams;
- classifies a new opening message into Vireo's support categories;
- returns a recommended ownership team and calibrated confidence;
- keeps uncertain cases (below 70% confidence) for human review;
- generates an executive briefing from verified metrics using Gemini (optional).

The classifier uses word and character TF-IDF features with a calibrated linear SVM. The Gemini layer translates numbers into prose but never generates the numbers themselves.

### How reliable is it?

Trained against policy-corrected specialist resolution (`training_category`), the model achieved 78.7% accuracy on a 2,307-ticket holdout (and 76.5% agreement with uncleaned raw intake tags). Across five stratified holdouts, accuracy ranged from 77.1% to 78.7% (mean 77.8%, SD 0.63 points), demonstrating split stability across seeds. Because historical tags are themselves noisy, I separately reviewed an independent, stratified 110-ticket audit that was completely excluded from the model's training data: the model was correct on 104/110 (94.5%), versus 91/110 (82.7%) for the source tag.

The remaining errors are mainly ambiguous product/hardware/app descriptions, vague `Other` cases, and messages where the same symptom can reasonably belong to more than one queue.

### Recommended next step

Run a controlled routing pilot. Keep the existing routing as the control, use the classifier only on high-confidence cases, send low-confidence cases to review, and track:

1. handoffs per 100 tickets;
2. Billing → Logistics reroutes;
3. first-response SLA breaches;
4. transfer cost per 100 tickets;
5. CSAT scores (handoff vs. first-contact).

Use the 13.4% handoff-rate target as the pilot success threshold. This keeps the business case measurable rather than assuming the model itself creates savings.

### Data caveat

The raw export contains pre-window 2024 rows, which I excluded. Legacy resolution timestamps are UTC while the displayed ticket timestamps are IST; the pipeline corrects that before resolution-time analysis. Legacy transfer values are blank, so transfer-cost analysis is restricted to current-helpdesk rows. CSAT blanks are excluded from averages per policy §8.
