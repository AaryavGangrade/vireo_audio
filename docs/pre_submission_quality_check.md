# Pre-submission quality check

This is a final engineering/reviewer check, not a claim of production certification.

| Check | Result | Evidence |
|---|---|---|
| Clean-machine entry point | PASS | `README.md` -> `scripts/run_pipeline.py` |
| Pipeline terminates cleanly | PASS | ~30s local run; exits code 0 |
| Automated tests | PASS | 14/14 passed (0 warnings) |
| Repeated-run sensitivity | PASS | 5 stratified holdouts on training_category; 77.1%-78.7%, mean 77.8%, spread 1.60 points |
| Independent manual validation | PASS | 104/110 model (strictly out-of-sample); 91/110 source tag |
| Historical tags not treated as truth | PASS | Explicit in README, memo, questionnaire |
| Must-have evidence gaps surfaced | PASS | `docs/requirements_matrix.md` + questionnaire |
| Missing agent-key path | PASS | explicit validation + test |
| Legacy timestamp semantics | PASS | +05:30 correction + test |
| Legacy blank transfers | PASS | excluded from transfer-cost denominator rather than treated as zero |
| Tier 2 volume misuse | PASS | excluded from Tier-1 headcount comparison |
| Live team recommendation | PASS | channel-aware Frontline mapping |
| Low-confidence handling | PASS | <70% -> human review |
| Closing-note leakage | PASS | live model uses opening message only |
| Business number arithmetic | PASS | 1,299 × ₹305; annualized at 650/week |
| Unsupported causal savings claim | PASS | savings described as pilot target, not realized impact |
| Template residue | PASS | only external candidate action is the explicitly labelled Google Drive upload field |
| Screen recording | COMPLETE | 3-minute executive walkthrough recording provided |
| Public Drive URL | COMPLETE | https://drive.google.com/file/d/1n4gMEOy-FGd49BkAFa-1ED1tYHe_GhNN/view?usp=drive_link |
