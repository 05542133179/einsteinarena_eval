# Verification report

## 2026-09-15 refresh (25 problems)

Environment: Python 3.10.12, NumPy 2.2.5, SciPy 1.15.2 (repository `.venv`).

Checks completed:

1. Live refresh against the official API (`openarena-eval refresh`)
   - problems: 25 (was 17)
   - new problems: `hadamard-det-51`, `kakeya-needle-128`,
     `no-three-in-line-75`, `ring-loading-15`, `shannon-capacity-c7-5`,
     `sidon-45-set`, `sorting-network-16`, `spencer-discrepancy`
   - removed problems: 0
   - changed verifier hashes: `circle-packing`, `circles-rectangle`,
     `edges-vs-triangles`, `heilbronn-triangles`
   - snapshot id: `20260915T064022Z-5330efed5dce`
2. `openarena-eval validate` — 25 problems, `valid: true`, no errors
3. `python -m unittest discover -s tests -v` — 5/5 passed
   (`test_snapshot_validates` and the offline refresh round trip no longer
   hard-code the problem count; both derive it from the manifest/listing)
4. `scripts/verify_rank1_reproduction.py` — every `top1_solution` in
   `baseline_top1/einsteinarena_initial_top1_20260915.jsonl` re-scored with the
   frozen local verifier
   - reproduced exactly: 20 problems
   - `close_1e-12` (last-float-digit difference vs the published value):
     `edges-vs-triangles` (-0.7117091757692579 / -0.7117091757692577),
     `first-autocorrelation-inequality`
     (1.5027436492326165 / 1.5027436492326163),
     `second-autocorrelation-inequality`
     (0.963588110582029 / 0.9635881105820294)
   - `not_packaged`: `kissing-number-d11`, `kissing-number-d12` (published
     entries for problem definitions the packaged selection excludes)
   - invalid or mismatching: 0
   - slowest verifier: `prime-number-theorem`, 211.5 s
5. Compatibility fix: the official problem endpoint now answers
   `GET /api/problems/<slug>` with `308 Permanent Redirect`, which Python
   3.10's stock `HTTPRedirectHandler` does not follow. `openarena_eval.sync`
   now installs a handler that follows 308 like 301/302/303/307.

## 2026-07-29 (17 problems)

Date: 2026-07-29

Environment:

- Python 3.13.13
- NumPy 2.5.1
- SciPy 1.18.0
- mpmath 1.4.1
- openpyxl 3.1.5

Checks completed:

1. `scripts/smoke_test.sh`
   - dataset snapshot validation: passed
   - packaged problems: 17
   - known `difference-bases` candidate: valid, raw score `4.0`
   - standard-library unit tests: 5/5 passed
2. SciPy-backed verifier smoke
   - problem: `second-autocorrelation-inequality`
   - candidate: `{"values":[1.0]}`
   - valid: `true`
   - raw score: `0.6666666666666666`
3. Live task refresh against the official API, executed in a temporary dataset
   copy
   - problems: 17
   - new problems: 0
   - removed problems: 0
   - changed verifier hashes: 0
   - refreshed snapshot validation: passed
4. Live leaderboard pull against the official API
   - problems fetched: 17
   - output files created: `overview.csv`, `leaderboard.csv`,
     `leaderboard.xlsx`, `raw.json`
5. Static checks
   - `python -m py_compile`: passed
   - `bash -n scripts/*.sh`: passed
6. Distribution check
   - built `openarena_eval_kit-0.1.0-py3-none-any.whl`
   - wheel contains all 17 bundled problems and verifier snapshots
   - installed the wheel into a fresh temporary virtual environment
   - validation and the known `difference-bases` score both passed outside the
     source checkout

The live refresh and leaderboard checks used temporary directories. They did
not overwrite the packaged snapshot or leave generated leaderboard output in
the repository.
