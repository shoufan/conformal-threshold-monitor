# Certified audit-budget validity for action monitors

When is a 1% audit budget actually 1%? We show that a sub-1% empirical FPR
does not automatically certify a 1% claim at the honest-sample sizes used
here, and that score granularity controls how much safety survives once
certification is required. `zmean3` is also a competitive monitor: it beats
Track A `multi` at the official empirical point, 67.35% vs 58.44%, and at the
certified deterministic point, 59.18% vs 42.86%.

Concretely, on this project's 2,007 honest actions across three matched
environments, threshold 4.5 observes a 0.75% FPR but its 90% Clopper-Pearson
upper bound is 1.06%, so the 1% claim is not certified. Certifying a 1% FPR
with zero tail flags needs roughly 230, 299, and 459 honest actions at
`delta = 0.10, 0.05, 0.01`. `zmean3` exposes 103 distinct honest score levels
versus `multi`'s 15, and the finer grid preserves more detection under
certification. These findings are demonstrated on this project's calibration
data plus the general minimum-n bound: numbers from a handful of runs are
unlikely to clear the certification floor, which is a field-wide finite-sample
property this testbed makes visible — not a claim that any specific reported
number is wrong.

**The monitor is competitive; the contribution is knowing which safety claims
you're entitled to make.**

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

- [Two-page report (PDF)](outputs/submission_package_extension/final_report/two_page_report.pdf)
- [Two-page report (Markdown)](outputs/submission_package_extension/final_report/two_page_report.md)
- [Full report](outputs/submission_package_extension/final_report/certified_audit_budget_report.md)
- [Results section](outputs/submission_package_extension/final_report/README_results_section.md)
- [Official metrics interpretation](outputs/official_metrics/official_frame_interpretation.md)
- [Official metrics audit](outputs/official_metrics/official_metrics_audit.md)
- [Score distributions and percentiles](outputs/official_metrics/score_distributions.md)
- [Live monitor reproducibility check](outputs/submission_package_extension/final_report/live_monitor_final_check.md)
- [Machine-readable key tables](outputs/submission_package_extension/final_report/key_tables.json)

## Data & logs

Scored data used for the reported tables is committed under
[`outputs/ensemble_extension/scored_components/`](outputs/ensemble_extension/scored_components/),
with frozen confirmatory paired results under
[`outputs/ensemble_extension/confirmatory_results/`](outputs/ensemble_extension/confirmatory_results/).
Official metrics summaries, score distributions, and percentiles are in
[`outputs/official_metrics/`](outputs/official_metrics/), and the compact
report tables are in
[`outputs/submission_package_extension/final_report/key_tables.json`](outputs/submission_package_extension/final_report/key_tables.json).
The bounded live monitor check is documented in
[`outputs/submission_package_extension/final_report/live_monitor_final_check.md`](outputs/submission_package_extension/final_report/live_monitor_final_check.md).

Raw public trajectories are not the primary artifact; they come from the
LinuxArena dataset and can be regenerated with the documented Control Tower
commands. Large local monitor-output directories and raw logs are omitted
where redundant, but the scored outputs, summaries, and validation artifacts
needed to audit the reported numbers are included. See
[`data/README.md`](data/README.md) and [`logs/README.md`](logs/README.md).

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

The official metrics-only workflow is reproduced from saved local component
scores with [`scripts/prepare_official_metrics.py`](scripts/prepare_official_metrics.py)
and [`scripts/analyze_official_metrics.py`](scripts/analyze_official_metrics.py).
To inspect or run the custom monitor with the project Control Tower binary, put
the repository root on the module path:

```bash
CT=work/hackos-5-quickstart/A_MonitorBuilding/.venv/bin/ct
PYTHONPATH="$PWD" "$CT" protocols monitors action monitor:zmean3
```

Running the live monitor requires model credentials and incurs provider cost.
The materialized official-metrics workflow uses saved local component scores.

No credentials are committed. Raw trajectories, raw scoring outputs, provider
logs, caches, `.env`, and `work/` are intentionally untracked.
