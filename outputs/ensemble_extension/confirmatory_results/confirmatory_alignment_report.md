# Confirmatory Component Alignment

The 75-unit manifest was frozen before scoring. Scores are joined on `(trajectory_id, action_index)` with `tool_call_id` checked when available.

## Coverage

- Retained trajectories scored: 75/75
- Valid aligned actions: 2,275
- Trajectories losing all usable actions: none

| Environment | Aligned actions |
| --- | ---: |
| `media_processing` | 1,034 |
| `web_scraping` | 618 |
| `clinical_trial` | 623 |

## Exclusions

| Reason | Actions |
| --- | ---: |
| `missing_or_invalid_goal_analysis` | 14 |
| `missing_or_invalid_multi_component` | 227 |

## Integrity and spend

- Every aligned score is finite and non-errored.
- Reconstructed `multi_baseline` equals the stored parent score.
- Submit actions, malformed actions, skipped monitor calls, incomplete component sets, and failed-member placeholder zeroes are excluded.
- No placeholder score entered the aligned arrays.
- Multi recorded cost: $3.490389.
- Goal-analysis recorded cost: $3.204446.
- Total incremental recorded cost: $6.694835.
- The 11-trajectory recovery reused provider cache and added $0.00.
- Goal-analysis input tokens: 21,486,713.
- Goal-analysis output tokens: 6,673,362.
- Goal-analysis cached input tokens: 32,223,744.
- Both monitor commands used `--no-upload`; no upload was requested.
