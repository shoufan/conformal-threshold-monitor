# Reusable `multi` Components

## Result

No re-scoring is needed for `orthogonal` or `old-action`. Existing raw
`multi` outputs preserve both component scores for every action retained in
the clean v1 score sets.

## Exact Fields

For each raw monitored trajectory:

```text
trajectory_id
actions[action_index].index
actions[action_index].tool_call_id
actions[action_index].monitor_response.sus_score
actions[action_index].monitor_response.members[0].sus_score
actions[action_index].monitor_response.members[1].sus_score
```

Interpretation:

```text
members[0] = orthogonal
members[1] = old-action
parent     = 0.5 * members[0] + 0.5 * members[1]
```

Member objects also retain `error`, `model_name`, token counts, cost, prompt,
raw response, and reasoning.

## Verified Coverage

| Dataset | Complete reusable actions |
| --- | ---: |
| Honest `media_processing` | 1,314 |
| Honest `web_scraping` | 356 |
| Honest `clinical_trial` | 337 |
| LaStraj attacks | 918 |
| **Total** | **2,925** |

Across all 2,925 retained actions:

- both member objects exist
- both member errors are null
- both models resolve to `openai/gpt-5-nano`
- the parent score exactly equals the mean of the two member scores
- the action's array position equals its stored `index`
- every action has a `tool_call_id`

One additional cross-environment parent response had a failed first member.
It was already excluded from `clinical_trial_scores.json` and must remain
excluded from ensemble analysis. The oversized attack action skipped in v1
also has no reusable complete pair. Placeholder zeroes are not valid scores.

## Alignment Plan

1. Read each raw `multi` trajectory and index complete component pairs by:

   ```text
   (trajectory_id, action_index)
   ```

2. Read future `goal-analysis` trajectories and build the same key.
3. Verify matching `tool_call_id`, function name, and environment.
4. Keep only keys with valid `orthogonal`, `old-action`, and `goal-analysis`
   results.
5. Record every dropped key and reason.
6. Reconstruct `multi_baseline` from the two member scores and assert it equals
   the stored parent before computing any new candidate.

This keying avoids relying on filenames or incidental file ordering.

## Source Locations

Reusable raw member responses:

- `outputs/multi_scored/honest/`
- `outputs/multi_scored/attacks/`
- `outputs/multi_scored_crossenv/web_scraping/`
- `outputs/multi_scored_crossenv/clinical_trial/`

The compact extracted v1 score JSON contains only parent scores, so component
extraction must read the raw monitored trajectory files above. Those files
remain read-only inputs.

## Extraction Schema

The later extraction artifact should retain at least:

```json
{
  "trajectory_id": "...",
  "environment": "...",
  "action_index": 0,
  "tool_call_id": "...",
  "function": "...",
  "orthogonal_score": 0.0,
  "old_action_score": 0.0,
  "goal_analysis_score": 0.0,
  "multi_baseline": 0.0,
  "mean3": 0.0,
  "max3": 0.0
}
```

For attacks, trajectory metadata must also retain `side_task_success`,
variant-family information, and the fields used by the v1 attack-unit
deduplication.
