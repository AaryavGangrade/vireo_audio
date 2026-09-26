# Three-minute screen recording script

No slides. Record the terminal + browser dashboard.

## 0:00–0:25 — Problem and setup

Say:
> "This is Vireo Set E. I treated the email as a client brief, not a specification. The requested output is monthly category/team volume, but I also looked for the business problem underneath the headcount request."

Show `README.md` briefly, then `scripts/run_pipeline.py`.

## 0:25–1:10 — Data decisions

Show the dashboard's data-quality section.

Say:
> "I found three important data issues. There are 139 pre-window tickets, so I excluded them. Legacy resolution timestamps are UTC while the ticket timestamps are IST, so I correct that before duration analysis. And legacy transfer blanks are not zeros, so transfer-cost analysis uses the current helpdesk only."

## 1:10–1:45 — What changed from the naive approach

Show the monthly team chart and routing matrix.

Say:
> "The email points toward Billing, but the export does not support treating that as settled: Billing is 20.8% of first assignments, while Chat Frontline is 26.0%. Billing is the largest specialist team, and 696 Billing-first tickets ultimately resolve in Logistics. The policy also says Tier 2 should not be compared with Tier 1 on ticket volume. So I changed the business question from 'which team is biggest?' to 'can we reduce avoidable handoffs before we buy capacity?'"

## 1:45–2:25 — AI tool and validation

Paste a few example customer messages into the classifier.

Say:
> "The model uses the opening message only, because that is available at ticket creation. It combines word and character TF-IDF with a calibrated linear SVM and gives a confidence score. Low-confidence cases are kept for review."

Open the validation section.

Say:
> "The historical-label holdout is 2,307 tickets at 81.9% agreement. Across five stratified holdouts it ranges from 81.4% to 83.2%, so I surface split sensitivity rather than one seed. Because the tags are noisy, I did a separate stratified 110-ticket manual audit: 94.5% for the model versus 82.7% for the source tags. Low-confidence predictions go to human review, and the classifier recommends the actual Frontline team from channel rather than inventing a generic queue."

## 2:25–2:55 — Business number

Show the handoff metric.

Say:
> "The current helpdesk has 1,299 recorded handoffs across 7,728 tickets, 16.8%. At Rs 305 each, that is Rs 3.96 lakh in observed cost. Annualised to 650 tickets a week, a 20% reduction is roughly Rs 3.47 lakh a year. That's the pilot target—not a claim that the model has already saved it."

## 2:55–3:00 — Scope honesty

Say:
> "I deliberately left out a staffing-hours simulation, deep customer segmentation, paid LLM inference, and autonomous routing because they either lacked defensible data or added risk without improving the immediate decision."
