# Goal-Analysis Component Alignment

The join uses `(trajectory_id, action_index)` and checks `tool_call_id` when both sources provide it. Only finite, non-errored scores from all three components are kept.

## Coverage

| Population | Expected reusable multi actions | Three-component aligned actions | Lost |
| --- | ---: | ---: | ---: |
| Honest | 2,007 | 1,989 | 18 |
| Attacks | 918 | 916 | 2 |

## Honest alignment by environment

| Environment | Aligned actions |
| --- | ---: |
| `media_processing` | 1,299 |
| `web_scraping` | 354 |
| `clinical_trial` | 336 |

## Attack alignment by environment

| Environment | Aligned actions |
| --- | ---: |
| `auto_workflow` | 81 |
| `clinical_trial` | 138 |
| `file_indexing` | 49 |
| `media_processing` | 147 |
| `shared_dotfiles` | 23 |
| `slack_clone` | 123 |
| `tiktok` | 90 |
| `web_scraping` | 265 |

## Exclusions

| Reason | Actions |
| --- | ---: |
| `missing_or_invalid_goal_analysis` | 20 |

## Integrity checks

- Trajectories losing all usable actions: none.
- Reconstructed `multi_baseline` equals the stored parent score for every aligned action.
- Submit actions, malformed source actions, monitor skips, errored responses, incomplete member sets, and failed-member placeholder zeroes are excluded by the v1 reusable-action allowlist and the new response validation.
- No placeholder score entered either aligned array.
- Recorded goal-analysis scoring cost across saved trajectories: $1.779366.
- Token-priced reusable multi-member cost: $4.634845.
- Token-priced goal-analysis cost for final saved responses: $4.906685.
- Estimated extra spend from aborted non-cache-key recovery calls: $0.042500.
