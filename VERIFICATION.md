# Verification report

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
