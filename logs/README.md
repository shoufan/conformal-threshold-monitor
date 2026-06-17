# Logs policy for this public repo

No raw execution logs are committed in this folder. The local workspace
contains large raw monitor-output directories and transient execution traces,
but those are noisy, redundant with the committed score summaries, and not
needed to audit the reported numbers.

Judge-facing proof and summaries are committed here instead:

- `outputs/submission_package_extension/final_report/live_monitor_final_check.md`
  documents the bounded live `monitor:zmean3` execution check.
- `outputs/official_metrics/` contains the official metrics summaries and
  score-distribution artifacts.
- `outputs/ensemble_extension/scored_components/` contains compact aligned
  scored components backing the ensemble analysis.
- `outputs/ensemble_extension/confirmatory_results/` contains the frozen
  confirmatory paired-result artifacts.

Large local run directories such as `outputs/confirmatory_scored/`,
`outputs/goal_analysis_scored/`, `outputs/multi_scored/`,
`outputs/multi_scored_crossenv/`, and `outputs/live_monitor_final_check/` are
intentionally omitted from git. They can be regenerated with the documented
Control Tower commands if credentials and budget are available.

No credentials, `.env` files, provider logs, or local caches are committed.
