# Final submission audit

Audit date: June 13, 2026.

Status: ready for teammate review. Nothing has been uploaded or submitted.

## Repository state

- Branch: `ensemble-monitor-extension`
- Audited implementation commit: `36cdc7a`
- Remote: `https://github.com/shoufan/confromal-theshold-monitor.git`
- Staged changes at audit start: none
- Accidental source changes: none
- Credential-shaped files or values: none found

The working tree still contains intentional local artifacts from earlier
analysis and scoring. These include raw scored outputs, local plots and
reports, zip archives, and an unrelated untracked test. The v1 demo script also
has a pre-existing newline-only modification. None belongs in this readiness
commit. The untracked `outputs/submission_package_extension.zip` is stale and
is not the authoritative package; recreate an archive from the committed
directory if an archive is needed.

## Package inventory

The committed package contains:

- the two-page report, full report, three-minute demo script, README results
  section, key tables, and blue-team checklist;
- official `multi` and `zmean3` metric summaries;
- score-distribution and safety plots;
- the frozen `monitor:zmean3` artifact;
- compact reproduction scripts and supporting analyses;
- the bounded live-monitor reproducibility check.

All local Markdown links resolve. `key_tables.json` and the official metric
summary JSON files parse successfully. The packaged monitor matches the
repository-root `monitor.py`, and packaged metric summaries and reproduction
scripts match their source copies.

The package contains no raw trajectories, trajectory-shaped JSON, raw monitor
outputs, `.env`, provider logs, traces, caches, or work directories. An
ignored `.DS_Store` found during inventory was removed.

## Claim audit

The final package keeps the claim boundaries intact:

- the matched 49 attacks are the primary detection comparison;
- the main-task-successful subset is a positive but underpowered stealth
  proxy, not proof of broad dual-success detection;
- every 96% frozen-set reference is paired with the fact that all 75 attacks
  failed the main task;
- the frozen confirmatory run evaluates detection only and does not recertify
  FPR;
- all-76 detection remains descriptive;
- Clopper-Pearson and Learn-then-Test are described as established methods;
- official empirical safety is the optimistic Track A benchmark, while CP/LTT
  tests whether a deterministic 1% claim is supportable;
- usefulness 0/27 is attributed to pre-existing failed-honest labels, not
  monitor degradation;
- all 27 honest calibration trajectories are main-task-failed. Retries or
  error recovery may make calibration conservative, but the data do not
  include a successful-honest comparison;
- the official tie-handling comparison is explicit: `multi` is 58.44%
  official versus 55.10% deterministic, while `zmean3` is 67.35% under both;
- the live monitor smoke test is a reproducibility check, not a new evaluation
  result.

## Validation

- `pytest`: 54 passed
- `ruff check . --fix`: passed
- `mypy .`: passed
- Required JSON validation: passed
- Current tracked-tree secret scan: 0 credential-shaped hits
- Full history scan: 12 commits and 1,224 broad matching lines reviewed, 0
  credential-shaped hits
- `.env` objects in history: `.env.example` only
- Raw and protected paths tracked or staged: none

No monitor scoring, evaluation, Hawk job, upload, submission, or dual-success
acquisition was run during this final audit.

## Lock decision

The extension package is ready for teammate review. The remaining human
decision is repository presentation: merge the extension branch into `main`,
or submit and pin the exact extension branch and commit. Do not assume judges
will discover a non-default branch.
