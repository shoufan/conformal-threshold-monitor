# Dual-success metadata count

This was a bounded metadata-only count. It made no model calls, downloaded no full trajectories, and did not use TikAPI, Hawk, or OpenRouter.

## Counts

| Environment | Returned | Page capped? | LaStraj overlap | Frozen-75 overlap | Other local overlap | New IDs | Actions min/median/max | Side tasks |
| --- | ---: | :---: | ---: | ---: | ---: | ---: | --- | ---: |
| `media_processing` | 122 | no | 8 | 0 | 1 | 113 | 3/9.0/13 | 1 |
| `web_scraping` | 90 | no | 6 | 0 | 1 | 83 | 10/13.0/14 | 2 |
| `clinical_trial` | 93 | no | 6 | 0 | 5 | 82 | 6/10.0/30 | 3 |
| `slack_clone` | 62 | no | 6 | 0 | 0 | 56 | 14/15.5/17 | 5 |
| `auto_workflow` | 60 | no | 4 | 0 | 0 | 56 | 8/9.5/10 | 1 |
| `file_indexing` | 30 | no | 2 | 0 | 0 | 28 | 17/17.5/18 | 2 |
| `shared_dotfiles` | 0 | no | 0 | 0 | 0 | 0 | - | 0 |
| `tiktok` | 32 | no | 2 | 0 | 0 | 30 | 24/24.0/40 | 2 |

The matched environments return 305 dual-success summaries and 278 new IDs after exclusions. None of the three pages hit the 500-row limit, so these are complete counts for the current query rather than lower bounds. The frozen confirmatory set has no overlap because all 75 of its retained attacks are main-task-failed.

Author labels are absent in the newly returned summaries. Attempts metadata is also mostly null; 33 matched records explicitly report `attempts_mt=true`, `attempts_st=true`, and `attempts_sneaky=true`. These fields cannot support reliable stratification without full-record vetting.

## Decision

Enough matched dual-success candidates exist for a later 75-record set, ideally 25 per environment. The underpowered stealth cell is therefore a vetting, scoring-budget, and schedule problem, not a raw data-availability problem.

Do not start that cycle now. It remains gated on a final report and demo, PR-template completion, public-repository/branch choice, one approved live `monitor:zmean3` check, and explicit human budget approval.

Using current per-environment action means, a 25/25/25 set is expected to contain about 884 raw actions and 858 monitorable actions. The three-component cost model gives $2.83, or $4.25 with 50% contingency. This is a planning estimate, not approval.

The metadata volume exceeds 200 matched candidates, but a learned gate is still out of scope. Candidate-family deduplication, independence checks, and frozen train/validation/test assignments would be prerequisites.
