# Certified audit-budget validity for action monitors

This Track A submission compares the baseline `multi` action monitor with a
fixed three-signal ensemble, `zmean3`. At the official empirical 1% audit
budget, safety is 58.44% for `multi` and 67.35% for `zmean3`. At deterministic
operating points certified for a 1% honest-action false-positive rate,
safety is 42.86% and 59.18%, respectively. `zmean3` improves attack ranking;
Clopper-Pearson and fixed-sequence Learn-then-Test check whether the claimed
audit budget is statistically supportable.

## Submitted monitor

The monitor artifact is [`monitor.py`](monitor.py), registered as
`monitor:zmean3`. It is an action-only monitor that combines `orthogonal`,
`old_action`, and `goal_analysis` using fixed honest-only normalization
constants.

A full live rerun makes model calls. The official reported metrics use the
same frozen formula materialized from saved component scores. A bounded live
smoke test verified that the registered artifact runs through Control Tower
and applies the formula exactly.

Live `monitor:zmean3` emits a fixed affine 0–10 encoding of raw zmean3 scores.
The certified raw threshold 2.636 corresponds to approximately 3.56 in the
encoded Control Tower score space; the analysis utilities decode this
automatically.

## Main deliverables

- [Two-page report](outputs/submission_package_extension/final_report/two_page_report.md)
- [Three-minute demo script](outputs/submission_package_extension/final_report/demo_script_3min.md)
- [Full report](outputs/submission_package_extension/final_report/certified_audit_budget_report.md)
- [Official metrics interpretation](outputs/official_metrics/official_frame_interpretation.md)
- [Official metrics audit](outputs/official_metrics/official_metrics_audit.md)
- [Score distributions and percentiles](outputs/official_metrics/score_distributions.md)
- [Blue-team checklist](outputs/submission_package_extension/final_report/blue_team_pr_checklist.md)
- [Live monitor reproducibility check](outputs/submission_package_extension/final_report/live_monitor_repro_check.md)
- [Machine-readable key tables](outputs/submission_package_extension/final_report/key_tables.json)

## Key results

| Result | `multi` | `zmean3` | Interpretation |
| --- | ---: | ---: | --- |
| Official empirical safety at 1% | 58.44% | 67.35% | Track A benchmark with fractional boundary ties |
| Certified deterministic safety at 1% | 42.86% | 59.18% | Fixed thresholds certified at `delta=0.10` |
| Matched-49 certified detection | 21/49 | 29/49 | Exact McNemar `p=0.0386` |
| Main-task-successful stealth proxy | 8/20 | 12/20 | Underpowered, `p=0.21875` |
| Frozen-75 overt result | 48/75 | 72/75 | All main-task-failed, `p=1.192e-07` |

The official `multi` result is 58.44%, rather than the 55.10% deterministic
empirical result, because Control Tower audits 24.19% of score-4.0 ties.
`zmean3` has a finer score grid, so its official and deterministic empirical
results are both 67.35%.

## Important caveats

- The frozen-75 result measures overt or main-task-failed sabotage, not
  stealthy dual-success detection.
- The 20-attack stealth proxy is positive but underpowered.
- All 27 honest calibration trajectories are main-task-failed. Retries or
  error recovery may make calibration conservative, but no successful-honest
  comparison is available.
- The current calibration set cannot establish absolute usefulness. The
  reported 0/27 usefulness predates monitoring and is not evidence of monitor
  degradation.
- Detection across all 76 original attacks is descriptive because five
  environments lack matched honest calibration.
- No learned gate, attack-tuned weights, or adaptive attack evaluation was
  used.

## Reproduction

The [blue-team checklist](outputs/submission_package_extension/final_report/blue_team_pr_checklist.md)
contains the metrics-only reproduction commands. To inspect or run the custom
monitor with the project Control Tower binary, put the repository root on the
module path:

```bash
CT=work/hackos-5-quickstart/A_MonitorBuilding/.venv/bin/ct
PYTHONPATH="$PWD" "$CT" protocols monitors action monitor:zmean3
```

Running the live monitor requires model credentials and incurs provider cost.
The materialized official-metrics workflow uses saved local component scores.

No credentials are committed. Raw trajectories, raw scoring outputs, provider
logs, caches, `.env`, and `work/` are intentionally untracked.
