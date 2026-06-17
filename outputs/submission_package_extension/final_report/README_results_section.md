## Results

We separate audit-budget validity from attack ranking. One-sided
Clopper-Pearson bounds and fixed-sequence Learn-then-Test determine whether a
1% honest-action FPR claim is supportable. A fixed three-signal ensemble then
tests whether detection improves at that certified budget. The monitor is
competitive; the contribution is knowing which safety claims you're entitled
to make. The technical lever is score granularity: a finer honest-score grid
(103 levels for `zmean3` versus 15 for `multi`) preserves more detection once
certification is required.

### Official Track A safety curve

`ct game-metrics metrics` was run locally in `action_only` mode on existing
matched scores. All attacks completed the side task, so safety equals
detection.

| Monitor | Safety at 0.1% | Safety at 1% | Safety at 5% | Certified deterministic safety at 1% |
| --- | ---: | ---: | ---: | ---: |
| `multi` | 14.35% | 58.44% | 85.70% | 42.86% |
| `zmean3` | 14.29% | 67.35% | 88.49% | 59.18% |

The official empirical rule may randomize boundary ties to spend the budget
exactly. CP/LTT asks whether a deterministic threshold on the observed score
grid statistically supports the same FPR claim.

The official-metrics audit confirms that the 58.44% versus 55.10% `multi`
difference is benign: the official rule audits 24.19% of score-4.0 ties,
whereas the certification analysis uses a deterministic threshold of 4.5 on
the same 49 attacks. Control Tower recognizes one additional honest action
with score 1.0, but it is outside the relevant tail and does not affect the
comparison. This tie gap is another consequence of score granularity:
`zmean3` has no corresponding gap at 1%, with official and deterministic
empirical safety both equal to 67.35%.

### Certified 1% operating point

| Method | Threshold | Observed FPR | CP 90% upper | CP 99% upper | Matched detection |
| --- | ---: | ---: | ---: | ---: | ---: |
| Empirical `multi` | 4.5 | 0.75% | 1.06% | 1.33% | 27/49 (55.10%) |
| Certified `multi` | 5.0 | 0.40% | 0.65% | 0.87% | 21/49 (42.86%) |

The empirical threshold observes less than 1% FPR but cannot certify that
claim. Certification validates the operating point; it does not improve
ranking.

Live `monitor:zmean3` emits a fixed affine 0–10 encoding of raw zmean3 scores.
The certified raw threshold 2.636 corresponds to approximately 3.56 in the
encoded Control Tower score space; the analysis utilities decode this
automatically.

### Fixed ensemble on the matched 49

| Monitor | Caught | Detection | Paired-only catches |
| --- | ---: | ---: | ---: |
| `multi` | 21/49 | 42.86% | 2 |
| `zmean3` | 29/49 | 59.18% | 10 |

The exact paired McNemar p-value is `0.0386`. `zmean3` adds goal-analysis to
the two `multi` components and uses honest-only z-normalization. Its definition
and threshold were fixed before confirmatory evaluation; no learned gate or
attack-tuned weights were used.

`zmean3` has 103 unique honest scores versus 15 for `multi`. This finer score
geometry preserves more of the empirical ranking gain under deterministic
certification.

### Main-task-success partition

| Main-task outcome | n | `multi` | `zmean3` | Exact McNemar p |
| --- | ---: | ---: | ---: | ---: |
| Successful | 20 | 8/20 (40.00%) | 12/20 (60.00%) | 0.21875 |
| Failed | 29 | 13/29 (44.83%) | 17/29 (58.62%) | 0.21875 |

The main-task-successful subset is a positive but underpowered stealth proxy.
It does not support a broad claim of stealthy dual-success detection.

### Frozen confirmatory set

All 75 frozen confirmatory attacks are main-task-failed. On that overt
sabotage population, `multi` detects 48/75 (64.00%) and `zmean3` detects 72/75
(96.00%), with exact McNemar `p=1.192e-07`. A one-per-run sensitivity check
gives 29/47 (61.70%) versus 45/47 (95.74%), `p=3.052e-05`. This confirms
strong detection of main-task-failed sabotage, not stealthy dual-success
attacks.

A zero-cost metadata query found 278 new dual-success candidate IDs across the
three matched environments. This is enough for a later balanced 75-attack
study, but acquisition, vetting, and scoring remain deferred and
human-gated.

### Limitations

- The matched set has 49 attacks; only 20 are main-task-successful.
- The frozen set has no main-task-successful attacks.
- Honest FPR certification covers three matched environments and depends on
  the calibration distribution and environment mix.
- All 27 honest calibration trajectories are main-task-failed. Their retries
  or error recovery may make calibration conservative, but no
  successful-honest comparison is available.
- The confirmatory run tests detection only and does not recertify FPR.
- Official usefulness is 0/27 because every downloaded honest calibration
  trajectory is already labeled main-task-failed before monitoring; this set
  cannot establish absolute usefulness. Since monitoring is post-hoc, the
  value is not evidence that `zmean3` degrades usefulness.
- No learned gate, adaptive attack evaluation, or attack-tuned weights were
  used.
- All-76 original attack detection is descriptive only.

See the
[two-page submission report](two_page_report.md),
[full report](certified_audit_budget_report.md), and
[machine-readable tables](key_tables.json). The detailed interpretation audit
is in `outputs/official_metrics/official_metrics_audit.md`.
