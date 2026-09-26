# Requirements coverage / reviewer checklist

| Brief requirement | Evidence | Status | Known gap |
|---|---|---|---|
| Working AI-assisted tool | `app.py`, `src/pipeline.py`, local model artifact | Complete | Pilot only; no production auth/monitoring |
| Starts from README on clean machine | `README.md`, `requirements.txt`, `scripts/run_pipeline.py` | Complete | Requires Python 3.11+ |
| Business goal with number + money | `docs/memo_to_priya.md`, `outputs/business_metrics.json` | Complete | Savings is a pilot target, not causal proof |
| Show it works | 2,307-ticket holdout + 110-ticket independent manual audit | Complete | Manual benchmark is small |
| Error rate + wrong-case type | `outputs/model_metrics.json`, questionnaire | Complete | Historical-label error is not truth error |
| Monthly category chart | app + `outputs/monthly_by_category.csv` | Complete | None |
| Monthly team chart | app + `outputs/monthly_by_team.csv` | Complete | Tier 2 not used for headcount ranking by policy |
| Read email thread | scope decision + memo | Complete | None |
| Respect policy costs/definitions | `src/config.py`, tests | Complete | Legacy transfer cost unavailable |
| Explicit must-have gaps | this document + questionnaire | Complete | None |
| Repeated-run calibration/sensitivity | `outputs/repeated_run_metrics.json` | Complete | Measures split sensitivity, not temporal drift |
| Missing-key path | `validate_input_keys()` + test | Complete | Runtime returns a clear error rather than silently joining nulls |
| Honest scope cuts | `docs/decisions_and_scope.md` | Complete | None |
| AI-use disclosure | `docs/ai_prompt_log.md` | Complete | Screen recording must be recorded by candidate |
