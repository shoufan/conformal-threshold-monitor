# Certified audit-budget validity for action monitors

## Problem and claim

Track A action monitors are evaluated at small audit budgets, including 1%
honest-action false-positive rate (FPR). An observed calibration FPR below 1%
does not by itself justify the claim that the true FPR is at most 1%:
finite-sample uncertainty may still put the upper confidence bound above the
budget.

We apply standard one-sided Clopper-Pearson (CP) bounds and descending
fixed-sequence Learn-then-Test (LTT) to AI-control audit thresholds. The
statistical tools are established; our contribution is showing how they
change which monitor operating points are supportable, and how score
granularity interacts with that certification.

## Method

The baseline is Track A's action-level `multi` monitor. Our fixed extension,
`zmean3`, combines orthogonal, old-action, and goal-analysis scores. Each
component is standardized using means and population standard deviations
computed only from honest calibration actions, then averaged. We use no
learned gate, attack-tuned weights, or runtime refitting.

Calibration is per honest action, with trajectory-grouped data handling.
Safety is measured per attack trajectory. The primary matched set contains 49
attacks from `media_processing`, `web_scraping`, and `clinical_trial`; all 49
completed the side task, so official safety equals attack detection on this
set.

For certification, thresholds are scanned from high to low over the observed
score grid. A threshold is retained while the one-sided CP upper bound on the
honest tail probability remains at or below the target FPR; scanning stops at
the first failure. This fixed sequence controls threshold-selection
multiplicity without changing the monitor scores or the agent policy.

## Official Track A safety

Control Tower's `action_only` metric fits an empirical rule at each audit
budget and may fractionally audit actions tied at the boundary.

| Audit budget | `multi` safety | `zmean3` safety |
| ---: | ---: | ---: |
| 0.1% | 14.35% | 14.29% |
| 1% | 58.44% | 67.35% |
| 5% | 85.70% | 88.49% |

At 1%, official `multi` safety is 58.44%, rather than the 55.10%
deterministic empirical result, because Control Tower audits 24.19% of
score-4.0 ties to spend the budget exactly. The attack set and successful
sabotage denominator are unchanged. We use the official values above for
rubric-facing comparison and deterministic rules for certification.

Control Tower reports usefulness as 0/27 for both monitors. Every calibration
trajectory was already labeled `main_task_success=false` before monitoring.
Because monitoring is post-hoc and cannot change those trajectories, this is
not evidence of usefulness degradation; these data cannot establish absolute
usefulness.

The official `zmean3` curve was computed without new model calls by
materializing the frozen formula from already-saved component outputs. The
runnable `monitor:zmean3` artifact implements the same formula, but was not
executed for this metrics pass.

## The certification gap

The pooled `multi` calibration set contains 2,007 quality-controlled honest
action scores. The most permissive deterministic empirical threshold among
the observed score grid points is 4.5: it flags 15 actions, for 0.75% observed
FPR. Its one-sided CP 90% upper bound is 1.06%, however, so the available data
do not support a 1% claim.

At threshold 5.0, 8 actions are flagged: observed FPR is 0.40% and the CP 99%
upper bound is 0.87%. This threshold is certified. On the matched attacks,
the stricter point reduces `multi` detection from 27/49 (55.10%) to 21/49
(42.86%). Certification does not alter ranking; it identifies the
deterministic operating point whose audit-budget claim is defensible.

The sample-size floor is exact. With zero tail flags, certifying a 1% FPR
requires about 230, 299, or 459 honest actions for
`delta=0.10`, `0.05`, or `0.01`; a non-empty tail requires more. The official
empirical curve is the optimistic benchmark, while CP/LTT determines which
claims survive finite-sample scrutiny.

## Ensemble gain: ranking and granularity

At each monitor's deterministic threshold certified for 1% FPR at
`delta=0.10`, `zmean3` catches 29/49 attacks (59.18%), compared with 21/49
(42.86%) for `multi`. The paired cells are 19 both, 10 `zmean3` only, 2
`multi` only, and 18 neither; exact McNemar `p=0.0386`.

| Monitor | Empirical matched detection | Certified matched detection |
| --- | ---: | ---: |
| `multi` | 55.1% | 42.9% |
| `mean3` | 67.3% | 53.1% |
| `zmean3` | 67.3% | 59.2% |

`mean3` and `zmean3` tie empirically, showing that adding goal-analysis
improves ranking. The difference after certification is score geometry:
`multi` has 15 unique honest scores, whereas `zmean3` has 103. The finer grid
offers a threshold closer to the budget boundary, preserving more of the
ranking gain under certification. Better signals improve discrimination;
finer granularity improves certified efficiency.

The distributions are consistent with that account. For honest actions,
`multi` has median 0.5, 95th percentile 2.5, and 99th percentile 4.0;
`zmean3` has median -0.248, 95th percentile 1.254, and 99th percentile 2.356.
Attack maxima move upward for both monitors, while `zmean3` supplies many more
distinct cut points in the sparse honest tail.

## Stealth boundary and confirmation

The matched set contains 20 attacks that still complete the main task, our
available stealth proxy. `multi` catches 8/20 (40%) and `zmean3` catches
12/20 (60%), but the paired test is underpowered (`p=0.21875`). This is a
positive signal, not evidence of broad stealthy dual-success detection.

A separately frozen set gives 48/75 (64%) for `multi` and 72/75 (96%) for
`zmean3`, with exact McNemar `p=1.192e-07`. All 75 attacks fail the main task,
so this confirms stronger detection of overt or main-task-failed sabotage,
not stealth.

## Limitations

- Honest calibration covers only three matched environments and depends on
  their deployment mixture.
- The 20-attack stealth proxy is underpowered; the frozen 75 contain no
  main-task-successful attacks.
- Current calibration trajectories cannot establish absolute usefulness.
- We tested no learned gate, adaptive attacks, or attack-tuned weights.
- CP validity depends on representative honest calibration data; correlated
  actions within trajectories remain a limitation.

The result has two layers: `zmean3` improves attack ranking, and CP/LTT states
which 1% audit-budget claims are statistically supportable.
