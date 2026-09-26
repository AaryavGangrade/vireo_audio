# Pre-submission quality check

This is a final engineering/reviewer check, not a claim of production certification.

| Check | Result | Evidence |
|---|---|---|
| Clean-machine entry point | PASS | `README.md` -> `scripts/run_pipeline.py` |
| Pipeline terminates cleanly | PASS | ~30s local run; exits code 0 |
| Automated tests | PASS | 14/14 passed (0 warnings) |
| Repeated-run sensitivity | PASS | 5 stratified holdouts; 81.4%-83.2%, spread 1.73 points |
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
| Screen recording | CANDIDATE ACTION | record using `docs/screen_recording_script.md` |
| Public Drive URL | CANDIDATE ACTION | paste after upload into `docs/submission-form.md` |
