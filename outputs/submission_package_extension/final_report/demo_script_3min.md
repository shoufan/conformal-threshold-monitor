# Three-minute demo script

## 0:00-0:32 - Two questions about the audit budget

**Show:** The empirical-versus-certified `multi` table.

"Every Track A safety number is reported at an audit budget, usually a one
percent honest-action false-positive rate. I separate two questions: what
safety do we get at that budget, and is the one percent claim statistically
supportable from the honest data? zmean3 beats the Track A multi baseline in
both frames: 67.35 versus 58.44 percent official empirical safety, and 59.18
versus 42.86 percent at certified deterministic one percent. The certified
drop is the price of certification, not zmean3 losing to the baseline."

## 0:35-1:12 - Official empirical curve and certified `multi`

**Show:** `../official_metrics/figures/official_safety_curves.svg`, then
`../figures/pooled_threshold_scan.svg`.

"The official Track A harness gives `multi` 58.4 percent safety at a one
percent empirical audit budget. It randomizes some score-4 ties to spend that
budget exactly. The earlier 55.1 percent result uses the same 49 attacks with
a deterministic threshold at 4.5, so the difference is tie handling, not a
changed denominator. The official curve is the standard optimistic baseline.

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

At each monitor's deterministic threshold certified for a one-percent FPR at
delta 0.10, `multi` catches 21 of 49 matched attacks and `zmean3` catches 29.
Discordant pairs run 10 to 2 in `zmean3`'s favor; the exact McNemar p-value is
0.0386."

## 1:48-2:14 - Ranking versus granularity

**Show:** `../figures/empirical_vs_certified_operating_points.svg`.

"Both three-component means catch 33 of 49 at the empirical point, so adding
goal-analysis is the ranking gain. Under certification, plain mean3 catches
26 while zmean3 catches 29. `multi` has 15 unique honest scores; zmean3 has
103. The finer grid lets certification retain more of the ranking gain, and
the same lever shows in the official metric: multi needs fractional score-4
tie auditing to reach 58.4, while zmean3 has no boundary-tie gap."

## 2:14-2:35 - Check the stealth proxy

**Show:** The main-task-success partition table.

"The matched set includes 20 attacks that still complete the main task. On
that stealth proxy, detection rises from 8 of 20 to 12 of 20. The direction is
positive, but there are only six discordant pairs. So this is suggestive and
underpowered, not proof of broad stealthy dual-success detection."

## 2:35-2:49 - Frozen overt-sabotage boundary

**Show:** The frozen-75 row with the caveat visible.

"A frozen set rises from 64 to 96 percent, but all 75 attacks fail the main
task. In the same sentence: this confirms overt or main-task-failed detection,
not stealth."

## 2:49-3:00 - Close

**Show:** Two-column takeaway: validity and ranking.

"Better scoring improves ranking; certification tells us which audit-budget
claims survive finite-sample scrutiny."
