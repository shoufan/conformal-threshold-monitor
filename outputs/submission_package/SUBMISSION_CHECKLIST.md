# Submission checklist

## Validation

- [x] `pytest`: 35 tests passed.
- [x] `ruff check .`: passed.
- [x] `mypy .`: passed.
- [x] Submission package JSON parses successfully.
- [x] All packaged SVG files parse successfully.
- [x] All relative links in the packaged report resolve.
- [x] Source score files match their pre-packaging SHA-256 hashes.

## Security and infrastructure

- [x] No credential-shaped values were found in the source/package scan.
- [x] Root `.env` is ignored by `.gitignore`.
- [x] `.env` is not included in the submission package.
- [x] No uploads have been performed.
- [x] No submission has been performed.
- [x] No Hawk jobs were used.
- [x] No monitor scoring or model calls were run during final packaging.

## Required materials

- [x] Final report exists:
  `final_report/certified_audit_budget_report.md`.
- [x] README results snippet exists:
  `final_report/README_results_section.md`.
- [x] Three-minute demo script exists:
  `final_report/demo_script_3min.md`.
- [x] Machine-readable tables exist:
  `final_report/key_tables.json`.
- [x] Official metric alignment check exists:
  `final_checks/game_metrics_alignment.md`.
- [x] Excluded attack action check exists:
  `final_checks/excluded_attack_action_check.md`.
- [x] Every plot referenced by the report or demo is packaged.
- [x] Analysis and threshold-selection scripts are packaged.
- [x] Method assumptions and limitations are stated in the final report.

## Commit boundary

Recommended for a submission commit:

- Source code under `monitor_cert/`, `scripts/`, and `tests/`.
- Project metadata: `README.md`, `pyproject.toml`, `uv.lock`, `.gitignore`,
  and `.env.example`.
- Compact final analyses and `outputs/submission_package/`.

Keep out of the submission commit unless the organizers explicitly require
them:

- `.env` and any credentials.
- `.venv/`, `work/.uv-cache/`, `.pytest_cache/`, `.mypy_cache/`,
  `.ruff_cache/`, and `__pycache__/`.
- `work/hackos-5-quickstart/`, including its virtual environment.
- Raw downloaded trajectories under `data/`.
- Raw monitored trajectory directories under `outputs/multi_scored/`,
  `outputs/multi_scored_crossenv/`, `outputs/monitor_smoke/`,
  `outputs/monitor_comparison/`, and `outputs/pilot_scored/`.
- Large raw page/API captures such as `outputs/honest_media_processing_page.json`.
- Provider logs or traces, if any are added later.

No source, score, or result file was deleted. With approval, the review removed
only generated package bytecode and duplicate test copies that interfered with
repository test discovery.
