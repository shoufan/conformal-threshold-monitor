# Confirmatory Attack Vetting

Generated June 13, 2026. No monitor scores, model calls, evals, Hawk jobs, or
uploads were used during selection or vetting.

## Result

The frozen confirmatory set contains 75 successful attacks:

| Environment | Metadata pool | Downloaded | Retained | Unique families | Unique runs | Raw actions | Estimated monitorable actions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `media_processing` | 500 | 40 | 25 | 25 | 21 | 1,110 | 1,085 |
| `web_scraping` | 500 | 55 | 25 | 25 | 16 | 716 | 691 |
| `clinical_trial` | 500 | 40 | 25 | 25 | 23 | 765 | 740 |
| **Total** | **1,500** | **135** | **75** | **75** | **47** | **2,591** | **2,516** |

The target of 25 family-deduplicated attacks per environment was reached.
Every retained record has the expected environment, a nonempty action trace,
no trajectory-level error, `side_task_success == true`, and explicit evidence
of attack intent in its prompt, policy metadata, description, attack analysis,
or verification metadata.

All retained records have `main_task_success == false`. This reflects the
available successful-side-task candidate pool and limits generalization to
dual-success attacks.

## Reproducible selection

Candidate summaries came from the public trajectory API using:

```text
environment=<environment>
passesSideTask=true
summary=true
limit=500
```

The metadata filters required the expected environment, successful side task,
null error, nonzero action count, and an ID absent from all local attack data.
No suspicion or monitor field was read for candidate selection.

Selection used fixed seed `20260613`. The initial draw selected 40 records per
environment while balancing side-task ID, primary author, and main-task
success. Full-record vetting showed too few distinct web-scraping run
provenances, so the same deterministic ordering supplied the next 15
web-scraping replacement candidates. No outcome-dependent replacement was
performed.

The final greedy selection preferred unused run provenance, then balanced
side-task ID, primary author, and main-task success. It did not choose only
short trajectories.

## Family definition

Records were linked into one family by any of:

1. a shared `variant-of-*` tag
2. an exact action-trace hash
3. the same run, environment, side task, main task, and author/policy tuple
4. action-signature Jaccard similarity of at least 0.92 with action-count ratio
   at least 0.90 inside the same environment/task/author tuple

The same checks included all 76 existing LaStraj attacks. A candidate family
overlapping LaStraj was rejected. At most one downloaded trajectory was kept
from each remaining family.

A shared run ID alone was treated as correlated provenance, not proof of an
identical family: Control Tower runs can contain different environments and
task combinations. The selector nevertheless preferred unused run IDs. The 75
retained families come from 47 run IDs: 25 runs contribute one retained
trajectory, 16 contribute two, and 6 contribute three.

## Rejections

| Reason | Media | Web | Clinical | Total |
| --- | ---: | ---: | ---: | ---: |
| Ambiguous attack intent | 2 | 1 | 6 | 9 |
| Family overlaps existing LaStraj | 3 | 17 | 6 | 26 |
| Duplicate retained family | 2 | 1 | 1 | 4 |
| Eligible reserve after target reached | 8 | 11 | 2 | 21 |
| **Total** | **15** | **30** | **15** | **60** |

The ambiguous records had successful side-task labels but ordinary or empty
prompts and no attack-policy, attack-analysis, description, or verification
metadata demonstrating intentional attack behavior. They were not inferred to
be attacks solely from the success label.

## Diversity

The retained set covers:

- 9 side tasks in `media_processing`
- 9 side tasks in `web_scraping`
- 5 side tasks in `clinical_trial`
- 7 author/model labels in `media_processing`
- 5 author/model labels in `web_scraping`
- 10 author/model labels in `clinical_trial`

The complete per-record decision, provenance, family ID, and reason are in
`confirmatory_attack_manifest.json`.

## Suitability

The set is suitable for a frozen confirmatory comparison of the already
declared `multi` and `zmean3` monitors:

- it is disjoint from existing LaStraj IDs and deduplicated against LaStraj
  families
- candidate selection was completed before scoring
- no monitor outcome influenced retention
- exactly 25 attacks are retained in each matched honest environment

It is not a perfectly independent sample. Multiple retained families share
batch-level run provenance, and no retained attack also passes the main task.
The primary paired result should therefore be accompanied by a sensitivity
analysis that keeps one deterministic trajectory per run ID. These limitations
do not justify changing the frozen candidate set after scores are observed.
