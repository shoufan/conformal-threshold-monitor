# Attack Data Inventory

Generated June 13, 2026 on branch `ensemble-monitor-extension`. This was a
zero-spend inventory: no monitor scoring, eval generation, Hawk job, upload, or
paid API call was run.

## Local coverage

The local attack inventory is exactly the 76 released LaStraj trajectories.
The trajectory ID sets in `data/attacks/lastraj/`,
`outputs/multi_scored/attacks/`, and
`outputs/goal_analysis_scored/attacks/` are identical.

| Environment | Trajectories | Successful side tasks | Raw actions | Valid `multi` actions | Three-component aligned actions | Matched honest data |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `media_processing` | 13 | 13 | 164 | 148 | 147 | yes |
| `web_scraping` | 27 | 27 | 300 | 265 | 265 | yes |
| `clinical_trial` | 9 | 9 | 148 | 138 | 138 | yes |
| `slack_clone` | 10 | 10 | 136 | 124 | 123 | no |
| `auto_workflow` | 7 | 7 | 88 | 81 | 81 | no |
| `file_indexing` | 3 | 3 | 51 | 49 | 49 | no |
| `shared_dotfiles` | 3 | 3 | 26 | 23 | 23 | no |
| `tiktok` | 4 | 4 | 94 | 90 | 90 | no |
| **Total** | **76** | **76** | **1,007** | **918** | **916** | **49 matched** |

All 76 trajectories have `side_task_success == true`. Of these, 34 also have
`main_task_success == true`; main-task success is not required by the current
successful-sabotage denominator. The raw trajectories contain 38
`variant-of-...` tags, which must be preserved for any later family-level
deduplication.

## Inclusion status

- **Matched-49:** all 49 attacks from `media_processing`, `web_scraping`, and
  `clinical_trial`. These are the headline detection population because those
  environments have honest calibration data.
- **All-76:** every local LaStraj attack. The additional 27 attacks are used
  descriptively because their environments lack matched honest calibration.
- **`multi` scores:** all 76 trajectories have valid `multi` scores. There are
  918 valid action scores; one malformed action and one failed monitor action
  are excluded.
- **Goal-analysis scores:** all 76 trajectories were processed. The strict
  three-component intersection contains 916 attack actions, with no trajectory
  losing all usable actions.
- **Local unscored attacks:** none found.
- **Local unused attacks:** none. The 27 unmatched attacks are not in the
  matched headline, but they are included in the all-76 descriptive analysis.

The pilot, smoke-test, and monitor-comparison attack files are duplicates or
subsets of these same 76 IDs. No additional completed attack IDs were found in
other local manifests or output directories.

## Local source classification

| Class | Count | Status |
| --- | ---: | --- |
| Currently scored attacks | 76 | `multi` and goal-analysis available |
| Locally available but unscored attacks | 0 | none found |
| Remotely discoverable completed-attack candidates | at least thousands | metadata only; not yet vetted or downloaded |
| Attacks requiring new eval generation | 0 required for the next expansion | `ct run eval` remains out of scope |

## Integrity notes

The attack unit remains one maximum valid action score per successful attack
trajectory, subject to the project variant-family rule. API candidates must not
be counted as usable units until their full records are downloaded in a bounded
batch and checked for completion, attack intent, successful sabotage,
duplicates, and family relationships.
