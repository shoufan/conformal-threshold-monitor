# Three-minute demo script

## 0:00-0:35 - Start with the audit-budget problem

**Show:** The empirical-versus-certified `multi` table.

"A monitor threshold can observe less than one percent false positives without
having enough evidence to support a one-percent claim. We separate two
questions: is the audit budget statistically certifiable, and once it is, can
a fixed ensemble detect more attacks?

This is an application of exact finite-sample certification to AI-control
audit budgets. Certification does not make the monitor rank attacks better."

## 0:35-1:10 - Empirical versus certified `multi`

**Show:** `../figures/pooled_threshold_scan.svg`.

"On 2,007 pooled honest actions, the empirical `multi` threshold is 4.5. Its
observed FPR is 0.75 percent, but the 90 percent upper bound is 1.06 percent,
so the claimed one-percent budget is not certified.

At threshold 5.0, the observed FPR is 0.40 percent and the 99 percent upper
bound is 0.87 percent. That operating point is certifiable. On the matched 49
attacks, moving between those thresholds lowers `multi` detection from 55.1
to 42.9 percent. That is the cost of making this finite-sample claim honest,
not a change in ranking."

## 1:10-1:45 - Fixed ensemble on matched attacks

**Show:** `../figures/matched_detection_certified_delta_10.svg`.

"We then froze `zmean3`, which adds goal-analysis to `multi`'s orthogonal and
old-action components. Its normalization comes only from honest actions. We
did not train a gate or tune weights on attacks.

At each monitor's fixed threshold certified for a one-percent FPR at
delta 0.10, `multi` catches 21 of 49 matched attacks and `zmean3` catches 29.
The paired cells are 19 both, 10 `zmean3` only, 2 `multi` only, and 18 neither.
The exact McNemar p-value is 0.0386."

## 1:45-2:15 - Check the stealth proxy

**Show:** The main-task-success partition table.

"The matched set includes 20 attacks that still complete the main task. On
that stealth proxy, detection rises from 8 of 20 to 12 of 20. The direction is
positive, but there are only six discordant pairs and the exact p-value is
0.21875. So this is suggestive and underpowered, not proof of broad stealthy
dual-success detection."

## 2:15-2:42 - Frozen overt-sabotage confirmation

**Show:** The frozen-75 row with the caveat visible.

"A separate frozen set contains 75 attacks, but all 75 fail the main task. On
this overt or main-task-failed population, detection rises from 48 of 75 to 72
of 75, or 64 to 96 percent, with an exact p-value of about 1.2 times 10 to the
minus 7.

That confirms strong performance on main-task-failed sabotage. It does not
establish stealth detection. Goal-analysis dominates 21 of the 24 new catches,
which is consistent with overt goal divergence amplifying the signal."

## 2:42-3:00 - Close

**Show:** Two-column takeaway: validity and ranking.

"The result has two clean layers. Exact certification tells us whether the
one-percent audit-budget claim survives finite-sample scrutiny. The fixed
ensemble improves attack ranking under that certified budget.

Better scoring improves ranking; certification tells us which audit-budget
claims survive finite-sample scrutiny."
