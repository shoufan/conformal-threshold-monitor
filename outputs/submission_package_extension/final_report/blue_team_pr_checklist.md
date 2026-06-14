# Blue-team PR checklist

This checklist maps the extension package to the local Track A blue-team PR
template.

## Summary and configuration

- [x] Monitor artifact: [`../monitor.py`](../monitor.py), registered as
  `monitor:zmean3`.
- [x] Baseline: Track A `multi`.
- [x] Mode: action-level monitoring and `ct game-metrics --mode action_only`.
- [x] Honest calibration: 27 trajectories from `media_processing`,
  `web_scraping`, and `clinical_trial`.
- [x] Primary attack set: 49 successful-sabotage trajectories from the same
  three environments.
- [x] Audit budgets: 0.1%, 1%, and 5%.
- [ ] Uploaded Control Tower run links: intentionally absent before final
  submission.

## Score distributions

- [x] Multi honest and matched-attack distributions:
  [`../official_metrics/score_distributions.md`](../official_metrics/score_distributions.md).
- [x] Zmean3 honest and matched-attack distributions: same table.
- [x] Histograms:
  [`../official_metrics/figures/multi_score_distribution.svg`](../official_metrics/figures/multi_score_distribution.svg)
  and
  [`../official_metrics/figures/zmean3_score_distribution.svg`](../official_metrics/figures/zmean3_score_distribution.svg).

## Percentiles

- [x] Count, min, p50, p75, p90, p95, p99, p99.9, max, unique-score count,
  and observed score step are in
  [`../official_metrics/score_distributions.md`](../official_metrics/score_distributions.md).

## Safety metrics

- [x] Official multi safety at 0.1%, 1%, and 5%:
  [`../official_metrics/multi_baseline/official_metrics_summary.md`](../official_metrics/multi_baseline/official_metrics_summary.md).
- [x] Official zmean3 safety at 0.1%, 1%, and 5%:
  [`../official_metrics/zmean3/official_metrics_summary.md`](../official_metrics/zmean3/official_metrics_summary.md).
- [x] Official baseline comparison and certified 1% operating points:
  [`../official_metrics/official_frame_interpretation.md`](../official_metrics/official_frame_interpretation.md).
- [x] All 49 primary attacks completed the side task, so safety equals
  detection on this set.

## Usefulness

- [x] Control Tower reports 0/27 for both monitors.
- [x] Limitation stated: every downloaded calibration trajectory is already
  labeled `main_task_success=false` before monitoring, so these data cannot
  establish absolute usefulness.
- [x] Both monitors use the same unchanged trajectories; monitoring is
  post-hoc.

## Findings and limitations

- [x] Full backing report:
  [`certified_audit_budget_report.md`](certified_audit_budget_report.md).
- [x] Three-minute demo:
  [`demo_script_3min.md`](demo_script_3min.md).
- [x] README-ready results:
  [`README_results_section.md`](README_results_section.md).
- [x] Machine-readable tables: [`key_tables.json`](key_tables.json).
- [x] Matched-49 result leads.
- [x] Main-task-successful stealth proxy is labeled underpowered.
- [x] Frozen-75 result is labeled main-task-failed/overt only.
- [x] FPR certification is separated from ranking and detection.
- [x] All-76 result remains descriptive only.

## Reproduction

Prepare local, metrics-only copies from existing scores:

```bash
.venv/bin/python scripts/prepare_official_metrics.py
```

Run the official action-only metrics with the project Control Tower binary:

```bash
CT=work/hackos-5-quickstart/A_MonitorBuilding/.venv/bin/ct
"$CT" game-metrics metrics \
  --honest outputs/official_metrics/multi_baseline/matched_inputs/honest \
  --attack outputs/official_metrics/multi_baseline/matched_inputs/attacks \
  --mode action_only \
  --audit-budgets 0.1 --audit-budgets 1 --audit-budgets 5 \
  --output-dir outputs/official_metrics/multi_baseline

"$CT" game-metrics metrics \
  --honest outputs/official_metrics/zmean3_materialized_inputs/honest \
  --attack outputs/official_metrics/zmean3_materialized_inputs/attacks \
  --mode action_only \
  --audit-budgets 0.1 --audit-budgets 1 --audit-budgets 5 \
  --output-dir outputs/official_metrics/zmean3

.venv/bin/python scripts/analyze_official_metrics.py
```

The materialization script reads existing local monitor responses. It does not
call models, generate evaluations, upload runs, or change source score files.
The live `monitor:zmean3` artifact was separately smoke-tested on one honest
and one attack trajectory. It called three component monitors per eligible
action, applied the frozen formula exactly, cost $0.175424, and did not upload.
See [`live_monitor_repro_check.md`](live_monitor_repro_check.md). The official
reported values still use the materialized frozen scores; a full live rerun
remains human-gated.

## Test plan

- [x] Unit tests cover frozen zmean3 arithmetic, score transport, and official
  metrics summaries.
- [x] `monitor:zmean3` resolves through Control Tower and completed a bounded
  `--no-upload` live smoke test.
- [x] `pytest`, `ruff check .`, and `mypy .` are required before commit.
- [x] Raw materialized trajectories and raw monitor outputs remain ignored.
- [ ] Full live rerun and any upload remain human-gated.
