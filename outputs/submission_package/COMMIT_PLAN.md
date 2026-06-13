# Commit plan

## Purpose

Bank a clean v1 of the certified audit-budget thresholding project before any
ensemble or detection-extension work begins.

Recommended commit message:

```text
Add certified audit-budget thresholding submission v1
```

## Staged content

Before adding this plan, the index contains 45 files and 12,449 added lines:

- Python package code under `monitor_cert/`.
- Reproducible analysis scripts under `scripts/`.
- Unit and integration tests plus small handwritten fixtures under `tests/`.
- Project metadata: `README.md`, `pyproject.toml`, `uv.lock`, `.gitignore`, and
  `.env.example`.
- The compact, self-contained submission package under
  `outputs/submission_package/`.

The submission package is about 324 KB. It includes the final report, README
results section, demo script, key tables, validation notes, four referenced SVG
plots, threshold utilities, analysis scripts, and dependency metadata.

## Intentionally excluded

The following paths are not staged:

- `.env`, `.venv/`, caches, bytecode, and package metadata caches.
- `data/` and all downloaded trajectories.
- `work/`, including the quickstart checkout and its virtual environment.
- Raw monitored outputs:
  - `outputs/multi_scored/`
  - `outputs/multi_scored_crossenv/`
  - `outputs/monitor_smoke/`
  - `outputs/monitor_comparison/`
  - `outputs/pilot_scored/`
- Large page/API captures.
- Compact intermediate analyses and reports outside
  `outputs/submission_package/`.
- `docs/`, which is not in the requested commit allowlist.
- The existing `outputs/submission_package.zip`.

No excluded file was deleted.

## Largest staged files

Sizes are Git blob sizes before this plan was added.

| Bytes | Path |
|---:|---|
| 71,554 | `uv.lock` |
| 71,554 | `outputs/submission_package/uv.lock` |
| 43,659 | `scripts/analyze_validity_gap.py` |
| 43,659 | `outputs/submission_package/scripts/analyze_validity_gap.py` |
| 41,031 | `scripts/analyze_multi.py` |
| 41,031 | `outputs/submission_package/scripts/analyze_multi.py` |
| 34,532 | `scripts/build_multi_dataset.py` |
| 34,532 | `outputs/submission_package/scripts/build_multi_dataset.py` |
| 30,952 | `scripts/analyze_crossenv.py` |
| 30,952 | `outputs/submission_package/scripts/analyze_crossenv.py` |
| 16,397 | `scripts/run_analysis.py` |
| 13,712 | `outputs/submission_package/validity_gap/minimum_certifiable_fpr_vs_n.svg` |
| 11,277 | `scripts/analyze_pilot.py` |
| 11,025 | `monitor_cert/data.py` |
| 8,321 | `outputs/submission_package/final_report/certified_audit_budget_report.md` |
| 7,931 | `tests/test_build_multi_dataset.py` |
| 6,192 | `outputs/submission_package/crossenv_analysis/pooled_threshold_scan.svg` |
| 5,493 | `outputs/submission_package/crossenv_analysis/observed_fpr_by_environment.svg` |
| 5,475 | `outputs/submission_package/crossenv_analysis/attack_detection_by_environment.svg` |
| 5,240 | `outputs/submission_package/monitor_cert/thresholds.py` |

No staged file exceeds 72 KB.

## Security and index audit

- The exact allowlist was scanned for `sk-`, provider names, API-key terms,
  authorization headers, bearer tokens, passwords, and secrets.
- `.env.example` contains dummy placeholder values only.
- No credential-shaped token was found.
- `.env` is ignored and not staged.
- No raw trajectory or monitored-output JSON is staged.
- No cache, provider log, trace, virtual environment, `data/`, or `work/` path
  is staged.
- Every staged path is inside the requested allowlist.

## Validation results

- `pytest`: 35 passed.
- `ruff check .`: passed.
- `mypy .`: passed for 17 source files.
- `git diff --cached --check`: passed.
- Submission package imports, JSON, links, and SVG files were validated during
  packaging.

## Remaining risks

- This is the repository's initial commit; there is no earlier Git history to
  compare against or roll back to.
- Several useful intermediate reports remain untracked outside the compact
  submission package. They are retained locally but intentionally omitted from
  this v1 commit.
- The package duplicates a few analysis scripts and dependency files so it is
  self-contained. Future changes must keep root and packaged copies in sync.
- Raw score and trajectory files are local-only. Reproducing every numeric
  output from scratch requires those local inputs or reacquiring them.
- No remote push, upload, or hackathon submission has been performed.
