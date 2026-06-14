# Final extension sanity check

## Scope

This check covers the Phase H extension report package at
`outputs/submission_package_extension/`. It does not alter thresholds,
normalization constants, candidate definitions, manifests, scored data, or the
frozen v1 package.

## Framing checks

- The report separates honest-action FPR certification from attack detection.
- The primary detection headline is the matched-49 result: `multi` 21/49
  (42.86%) versus `zmean3` 29/49 (59.18%).
- The main-task-successful subset is labeled positive but underpowered:
  8/20 versus 12/20, exact McNemar `p=0.21875`.
- Every report or demo passage that presents 72/75 (96.00%) also states that
  all 75 frozen attacks are main-task-failed.
- The frozen result is described as evidence for overt or main-task-failed
  sabotage, not stealthy dual-success attacks.
- All-76 original attack detection is descriptive only.
- The report makes no learned-gate, adaptive-attack, or broad stealth claim.
- The confirmatory run is described as a detection test, not an FPR
  recertification.
- Clopper-Pearson and Learn-then-Test are presented as established methods
  applied to AI-control audit budgets, not as new methods.

## Package checks

- Final report, demo script, README results section, and valid JSON tables are
  present.
- Four referenced SVG figures are included locally.
- Compact supporting analyses are included as markdown references.
- Package size is approximately 96 KB.
- No raw trajectories, raw monitor outputs, provider logs, caches, work
  directories, or environment files are included.

## Frozen v1 check

All files under `outputs/submission_package/` are byte-identical to the
task-start hash snapshot. A pre-existing worktree modification to
`outputs/submission_package/final_report/demo_script_3min.md` remains present
and unstaged; this task did not alter or stage it.

## Validation

- `pytest`: 45 passed.
- `ruff check --fix .`: passed with no changes.
- `ruff check .`: passed.
- `mypy .`: no issues in 23 source files.
- `outputs/submission_package_extension/final_report/key_tables.json`:
  valid JSON.
- `.env`, `data/`, `work/`, and `outputs/confirmatory_scored/`: untracked.
- Secret scan: no token-shaped credentials found.
- No files were staged before the extension-only staging step.

## Remaining limitations

- The matched sample has 49 attacks, with 20 main-task-successful attacks.
- The frozen confirmatory set has no main-task-successful attacks.
- Honest calibration covers three matched environments.
- FPR certification depends on exchangeability and the deployment environment
  mix.
- Raw confirmatory monitor outputs remain local and untracked.
