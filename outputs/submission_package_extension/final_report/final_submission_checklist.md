# Final submission checklist

## Repository

- [x] GitHub repository:
  <https://github.com/shoufan/confromal-theshold-monitor>
- [x] Branch: `main`
- [x] GitHub default branch: `main`
- [x] Packaging source commit: `876aca7`
- [x] V1 safety tag: `v1-submission-root`
- [x] Extension audit tag: `extension-final-audit`
- [x] Monitor artifact: [`../../../monitor.py`](../../../monitor.py)
- [x] Registered monitor name: `monitor:zmean3`

The final export commit is the current `main` HEAD after this checklist and
the PDF are committed. Use `git rev-parse HEAD` or the GitHub commit shown on
`main` as the immutable submission reference.

## Deliverables

- [x] Landing page: [`../../../SUBMISSION_README.md`](../../../SUBMISSION_README.md)
- [x] Two-page report PDF: [`two_page_report.pdf`](two_page_report.pdf)
- [x] Two-page report source: [`two_page_report.md`](two_page_report.md)
- [x] Three-minute demo script: [`demo_script_3min.md`](demo_script_3min.md)
- [x] Demo timing check: [`demo_timing_check.md`](demo_timing_check.md)
- [x] Official metrics interpretation:
  [`../../official_metrics/official_frame_interpretation.md`](../../official_metrics/official_frame_interpretation.md)
- [x] Official metrics audit:
  [`../../official_metrics/official_metrics_audit.md`](../../official_metrics/official_metrics_audit.md)
- [x] Score distributions:
  [`../../official_metrics/score_distributions.md`](../../official_metrics/score_distributions.md)
- [x] Blue-team checklist:
  [`blue_team_pr_checklist.md`](blue_team_pr_checklist.md)
- [x] Live monitor reproducibility check:
  [`live_monitor_repro_check.md`](live_monitor_repro_check.md)

## Validation

- [x] PDF exists, is non-empty, and contains exactly two pages
- [x] PDF pages visually reviewed at full resolution
- [x] Key tables JSON parses successfully
- [x] Test suite passes
- [x] Ruff passes
- [x] mypy passes
- [x] Tracked-file credential scan passes
- [x] `.env`, `data/`, `work/`, raw scoring outputs, provider logs, and caches
  remain untracked or ignored
- [x] No scoring, evaluation, Hawk, upload, or submission command was run

## Manual actions

- [ ] Open the PDF once in the final submission portal and confirm its preview
- [ ] Record the three-minute demo using the timed script
- [ ] Upload the demo to the required host
- [ ] Complete the final submission form or pull request
- [ ] Link the repository landing page or `SUBMISSION_README.md`

Optional dual-success scoring remains deferred and is not required for this
submission package.
