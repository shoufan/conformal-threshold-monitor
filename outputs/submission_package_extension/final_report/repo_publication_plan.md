# Repository publication plan

## Current state

- Public remote:
  `https://github.com/shoufan/confromal-theshold-monitor.git`
- Current branch: `ensemble-monitor-extension`
- Audited implementation commit: `36cdc7a`
- Local `main`: `4cb4b82`, the clean certified-thresholding v1
- The v1 package remains available under `outputs/submission_package/`
- No merge, upload, or submission is part of this audit

The readiness commit that contains this note adds only audit and package text.
Use the latest pushed extension commit shown by Git after the readiness commit
as the final pin.

## Publication choices

### Merge the extension into main

This is the clearest option when judges will open the repository root or
follow the default branch. Before merging, confirm that the v1 package remains
available as the baseline and restore point.

### Submit the exact extension branch and commit

This avoids changing `main`, but the submission must link directly to
`ensemble-monitor-extension` and name the exact commit. Pin that commit in the
submission text and teammate-review notes.

## Risks

- If the default branch still presents v1, judges may miss the ensemble,
  official-metrics, and live-monitor work.
- A branch-only submission is fragile if the link points to the repository
  root instead of the exact branch or commit.
- A merge should preserve the clean v1 history and package rather than
  replacing it.
- The untracked local package zip is stale. The committed
  `outputs/submission_package_extension/` directory is authoritative.

## Recommendation

For public submission, merge `ensemble-monitor-extension` into `main` after
teammate review. If time is too tight for a reviewed merge, submit the exact
extension branch and commit instead. Do not leave the choice implicit.
