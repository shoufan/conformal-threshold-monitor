# Three-minute demo script

## 0:00-0:35 - Start with the audit-budget problem

**Show:** The empirical-versus-certified `multi` table.

"A monitor threshold can observe less than one percent false positives without
having enough evidence to support a one-percent claim. We separate two
questions: is the audit budget statistically certifiable, and once it is, can
a fixed ensemble detect more attacks?

This is an application of exact finite-sample certification to AI-control
audit budgets. Certification does not make the monitor rank attacks better."

## 0:35-1:12 - Official empirical curve and certified `multi`

**Show:** `../official_metrics/figures/official_safety_curves.svg`, then
`../figures/pooled_threshold_scan.svg`.

"The official Track A harness gives `multi` 58.4 percent safety at a one
percent empirical audit budget. It randomizes some score-4 ties to spend that
budget exactly. That is the standard optimistic baseline.

For a deterministic rule on 2,007 honest actions, threshold 4.5 observes 0.75
percent FPR, but its 90 percent upper bound is 1.06 percent. Threshold 5.0
observes 0.40 percent and has a 99 percent upper bound of 0.87 percent. Its
42.9 percent safety is the auditable deterministic point. Certification is
not correcting the official metric; it is testing the statistical claim
behind a deployable threshold."

## 1:12-1:48 - Fixed ensemble on matched attacks

**Show:** The official safety table, then
`../figures/matched_detection_certified_delta_10.svg`.

"We then froze `zmean3`, which adds goal-analysis to `multi`'s orthogonal and
old-action components. Its normalization comes only from honest actions. We
did not train a gate or tune weights on attacks.

Official one-percent empirical safety rises from 58.4 percent for `multi` to
67.3 percent for `zmean3`. At each monitor's deterministic threshold certified
for a one-percent FPR at delta 0.10, `multi` catches 21 of 49 matched attacks
and `zmean3` catches 29.
The paired cells are 19 both, 10 `zmean3` only, 2 `multi` only, and 18 neither.
The exact McNemar p-value is 0.0386."

## 1:48-2:14 - Ranking versus granularity

**Show:** `../figures/empirical_vs_certified_operating_points.svg`.

"Both three-component means catch 33 of 49 at the empirical point, so adding
goal-analysis is the ranking gain. Under certification, plain mean3 catches
26 while zmean3 catches 29. `multi` has 15 unique honest scores; zmean3 has
103. The finer grid lets certification retain more of the ranking gain."

## 2:14-2:35 - Check the stealth proxy

**Show:** The main-task-success partition table.

"The matched set includes 20 attacks that still complete the main task. On
that stealth proxy, detection rises from 8 of 20 to 12 of 20. The direction is
positive, but there are only six discordant pairs. So this is suggestive and
underpowered, not proof of broad stealthy dual-success detection."

## 2:35-2:49 - Frozen overt-sabotage boundary

**Show:** The frozen-75 row with the caveat visible.

"A frozen set also rises from 64 to 96 percent, but all 75 attacks fail the
main task. That confirms overt or main-task-failed detection, not stealth."

## 2:49-3:00 - Close

**Show:** Two-column takeaway: validity and ranking.

"The result has two clean layers. Exact certification tells us whether the
one-percent audit-budget claim survives finite-sample scrutiny. The fixed
ensemble improves attack ranking under that certified budget.

Better scoring improves ranking; certification tells us which audit-budget
claims survive finite-sample scrutiny."
