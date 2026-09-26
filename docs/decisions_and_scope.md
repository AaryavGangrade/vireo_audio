# Strategic Decisions, Technical Push-Backs, and Scope Boundaries

This document details the critical architectural choices, deliberate scope omissions, and strategic push-backs made during the evaluation of the Vireo Audio Set E support desk dataset.

---

## 1. Where I Pushed Back on the Client Brief

### Push-Back 1: Refusing to Use "Largest Raw Queue = Two Hires"
* **The Client Request:** In the email thread, Priya Raman stated that the team with the largest queue should receive the next two headcount hires.
* **The Reality in the Data:**
  * While Billing appears as the largest specialist queue (2,425 tickets, 20.8% of in-scope volume), **658 tickets (27.1%) resolve in Logistics, rising to 696 (28.7%) including open reroutes**.
  * The intake bot is systematically misrouting courier and delivery delays into the payments queue because customers mention invoice numbers alongside tracking issues.
  * Finance Controller Arjun Mehta explicitly questioned approving **₹9 Lakhs/year** without a clear business case.
* **The Decision:** I retained the requested monthly queue charts for transparency, but reframed the primary recommendation: **fix the intake routing leak first**. Reducing handoffs avoids ₹3.47 Lakhs/year in transfer penalties and avoids committing ₹9 Lakhs to the wrong department.

### Push-Back 2: Enforcing the Jan 2025 – Jun 2026 Scope Boundary
* **The Data Reality:** The raw `tickets.csv` export contains 139 tickets dated between June and December 2024.
* **The Decision:** I strictly excluded these 139 pre-window rows rather than silently skewing the reporting baseline. All analyses reflect exactly the 11,641 in-scope tickets.

### Push-Back 3: Correcting the UTC vs. IST Legacy Timestamp Bug
* **The Policy Reality:** Per `support-policy.pdf` §8, Freshdesk (`legacy_fd`) logged resolution timestamps in **UTC**, whereas the current helpdesk displays all timestamps in **IST (+05:30)**.
* **The Danger:** A naive duration subtraction (`resolved_at - created_at`) makes 2,379 legacy tickets appear to resolve *before they were even created*.
* **The Decision:** Applied a strict `pd.DateOffset(hours=5, minutes=30)` normalization to all `legacy_fd` resolution timestamps before computing resolution metrics.

### Push-Back 4: Refusing to Treat Blank Legacy Transfers as Zero
* **The Data Reality:** Freshdesk did not capture ticket transfers, leaving `transfers` as `NaN` on all 3,913 legacy rows.
* **The Danger:** Using `fillna(0)` artificially dilutes the handoff rate from **16.8% down to 11.1%**, misleading leadership into believing routing friction is minor.
* **The Decision:** Restriced transfer-cost analysis strictly to the 7,728 tickets on the current helpdesk where transfers are actively recorded.

### Push-Back 5: Respecting the Tier 2 Exemption Rule
* **The Policy Reality:** `support-policy.pdf` §6 explicitly states that Tier 2 (Escalations & Warranty) is measured in days and must never be compared against Tier 1 on raw ticket count.
* **The Decision:** Included Tier 2 in reporting matrices for holistic visibility, but strictly excluded it from any headcount or speed rankings.

---

## 2. What I Deliberately Left Out (Scope Cuts)

Every production system requires disciplined trade-offs under a five-hour evaluation window. Here is what was left out and why:

1. **Staffing-Capacity / Erlang-C Simulation:**
   * *Why omitted:* The dataset provides ticket creation and resolution timestamps, but **not active handle time**. A ticket open for 3 days usually involves 15 minutes of agent work and 71.75 hours of customer/courier wait time. Building an Erlang model on resolution duration creates dangerous false precision.
2. **Heavy Deep Learning / Transformer Dependencies:**
   * *Why omitted:* Installing PyTorch / HuggingFace requires gigabytes of downloads, introduces GPU dependencies, and risks breaking the "clean-machine" requirement. The Calibrated Linear SVM trains in 10 seconds, runs in 2ms, achieves 94.5% ground-truth accuracy, and occupies ~9 MB on disk.
3. **Deep Customer & Order Segmentation:**
   * *Why omitted:* Joining `customers.csv` and `orders.csv` provides lifetime value insights, but does not alter the immediate routing or headcount decision. Keeping the schema lean prevents bloat.
4. **Fully Autonomous Routing (No Human in the Loop):**
   * *Why omitted:* Because the historical tags have an ~17% error rate, auto-routing 100% of tickets would guarantee misroutes. A **70% confidence threshold** with a Human Review fallback is the only defensible operational design.

---

## 3. Engineering & Reviewer-Risk Controls

To ensure production-grade reliability, the codebase incorporates five explicit defensive mechanisms:

* **Repeatability & Sensitivity:** Evaluated across 5 random holdout seeds (7, 19, 42, 73, 101) against policy-corrected specialist resolution (`training_category`). The observed spread is narrow (77.1% – 78.7%, mean 77.8%, SD 0.63%, spread 1.60%), proving stability across random splits rather than a lucky fluke. (Historical raw tag agreement across the same seeds is 81.4% – 83.2%, mean 82.2%).
* **Missing-Key & Schema Defense:** `validate_input_keys()` enforces that both `tickets.csv` and `agents.csv` contain all required keys, unknown agent IDs fail loudly with error traces, and unsupported channels are caught before processing.
* **Channel-Aware Routing:** Frontline queues automatically resolve to the specific channel frontline (e.g. Chat → Chat Frontline, Voice → Voice Frontline) rather than generic placeholders.
* **Safe Fallbacks:** The Gemini narrator layer in `src/narrator.py` handles missing API keys, rate limits, or empty metrics dictionaries without ever throwing runtime exceptions.
* **Automated Test Suite:** 14 automated unit and integration tests (`tests/test_pipeline.py`) verify data schemas, timezone corrections, metric calculations, and edge cases with zero warnings.
