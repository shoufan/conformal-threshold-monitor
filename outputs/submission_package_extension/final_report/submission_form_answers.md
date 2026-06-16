# Submission form answers

Draft answers for the Track A submission form. Numbers and claims match the
two-page report, README, and `key_tables.json`. Text-only; no result changed.

## Short abstract

When is a 1% audit budget actually 1%? We build a competitive Track A action
monitor, `zmean3`, and use it to ask which 1% safety claims are statistically
entitled. A sub-1% empirical false-positive rate does not automatically
certify a 1% claim at the honest-sample sizes used here: on this project's
2,007 honest actions across three matched environments, threshold 4.5 observes
a 0.75% FPR but its 90% Clopper-Pearson upper bound is 1.06%, so the 1% claim
is not certified. Certifying a 1% FPR with zero tail flags needs roughly 230,
299, and 459 honest actions at `delta = 0.10, 0.05, 0.01`. Score granularity
then controls how much safety survives certification: `zmean3` exposes 103
distinct honest score levels versus `multi`'s 15, and the finer grid preserves
more detection once a certified threshold is required. `zmean3` is also
competitive as a monitor — it beats Track A `multi` at the official empirical
1% point (67.35% vs 58.44%) and at the certified deterministic 1% point
(59.18% vs 42.86%).

**The monitor is competitive; the contribution is knowing which safety claims
you're entitled to make.**

## What is novel / useful

- **Competitive monitor plus certifiable claims.** `zmean3` is a fixed,
  attack-blind three-signal ensemble (orthogonal + old-action + goal-analysis,
  honest-only z-normalization) that beats the `multi` baseline in both the
  official empirical and certified deterministic frames. On top of the monitor,
  we report which audit-budget claims the honest data statistically supports.
- **The validity gap as a benchmark finding.** The standard Track A scoring
  rule fits a threshold to spend the budget exactly, so its reported operating
  point can have an observed FPR at the budget while its finite-sample upper
  bound exceeds it. We make this gap measurable: observed 0.75% but CP90 1.06%
  at `multi`'s empirical 1% point, plus a minimum-n floor (~230/299/459 honest
  actions) below which a 1% claim cannot be certified.
- **Granularity ↔ certification as the technical insight.** `mean3` and
  `zmean3` tie at 67.3% empirically, so the goal-analysis view is the ranking
  gain; under certification `mean3` keeps 26/49 and `zmean3` keeps 29/49. The
  difference is score granularity — `zmean3`'s 103-level grid versus `multi`'s
  15 — and the same lever appears in the official metric, where `multi` needs
  fractional score-4 tie auditing to reach 58.44% while `zmean3`'s official and
  deterministic safety are both 67.35%. Ensemble design and calibration method
  meet here.
- **Honest about method.** Clopper-Pearson and fixed-sequence Learn-then-Test
  are standard, label-conditional FPR-control tools; our contribution is their
  rigorous application and measurement in the AI-control audit-budget setting,
  not new statistics. We are the well-behaved monotone case, and we say so.
- **Scoped, not a benchmark dunk.** These results are demonstrated on this
  project's calibration data and the general minimum-n bound. The takeaway is a
  field-wide finite-sample property this testbed makes visible — including for
  us — not a claim that any specific reported number is wrong.

## Limitations (carried verbatim from the report)

- Clopper-Pearson / fixed-sequence LTT are standard, not novel; we claim
  rigor of application.
- The frozen-75 confirmatory result (48/75 vs 72/75, `p=1.192e-07`) is on an
  all-main-task-failed set; it measures overt or main-task-failed sabotage, not
  stealthy dual-success detection.
- The stealth proxy (main-task-successful subset) is positive but underpowered:
  8/20 to 12/20, exact McNemar `p=0.21875`.
- All 27 honest calibration trajectories are main-task-failed. This likely
  makes certification conservative, but no successful-honest comparison is
  available, so it remains a limitation.
- The current failed-honest calibration set cannot establish absolute
  usefulness; the reported 0/27 predates monitoring and is not evidence of
  degradation.
- No learned gate, attack-tuned weights, or adaptive-attack evaluation was
  used; all-76 original-attack detection is descriptive only.
- We do not claim broad stealthy dual-success detection.
