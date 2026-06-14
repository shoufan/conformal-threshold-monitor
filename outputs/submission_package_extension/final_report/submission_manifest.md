# Submission manifest

## Repository

- Branch: `main`
- Audited merge commit: `e43bc795936381389c8b5d23eba2532e4395d3f1`
- Remote: `https://github.com/shoufan/confromal-theshold-monitor.git`
- V1 safety tag: `v1-submission-root` at `4cb4b82`
- Extension audit tag: `extension-final-audit` at `a2f04dd`

This manifest and the landing-page files are committed as a descendant of the
audited merge commit above.

## Deliverables

- Monitor: [`../../../monitor.py`](../../../monitor.py)
- Submission index: [`../../../SUBMISSION_README.md`](../../../SUBMISSION_README.md)
- Two-page report: [`two_page_report.md`](two_page_report.md)
- Three-minute demo script: [`demo_script_3min.md`](demo_script_3min.md)
- Full report: [`certified_audit_budget_report.md`](certified_audit_budget_report.md)
- README results section: [`README_results_section.md`](README_results_section.md)
- Key tables: [`key_tables.json`](key_tables.json)
- Blue-team checklist: [`blue_team_pr_checklist.md`](blue_team_pr_checklist.md)
- Live monitor check: [`live_monitor_repro_check.md`](live_monitor_repro_check.md)
- Official metrics interpretation:
  [`../../official_metrics/official_frame_interpretation.md`](../../official_metrics/official_frame_interpretation.md)
- Score distributions:
  [`../../official_metrics/score_distributions.md`](../../official_metrics/score_distributions.md)

## Validation

- `pytest`: 54 passed
- `ruff check .`: passed
- `mypy .`: passed
- Key tables JSON: valid
- Current tracked-tree and full-history credential scans: passed
- Raw trajectories and raw monitor outputs: intentionally untracked
- `.env`, provider logs, caches, and `work/`: intentionally untracked

No scoring, evaluation, Hawk job, Control Tower upload, or submission command
was run while preparing this landing page.

## Manual GitHub setting

GitHub's symbolic default branch currently points to
`ensemble-monitor-extension`. For the clearest judge experience, set the
default branch to `main` in **GitHub Settings > Branches**, unless the team
deliberately chooses to keep the extension branch as default.
