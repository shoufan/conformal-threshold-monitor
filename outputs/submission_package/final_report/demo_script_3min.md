# Three-minute demo script

## 0:00-0:40 - The problem

**Show:** Title and the empirical-versus-certified result table.

"Action monitors are usually calibrated by taking the top one percent of
honest scores. But an observed rate below one percent is not automatically a
statistically supportable one-percent claim.

Our contribution is threshold validity, not a new ranking model. We keep the
Track A `multi` monitor fixed and ask: when can we honestly say this threshold
respects a one-percent audit budget?"

## 0:40-1:20 - Minimum sample size

**Show:** `../validity_gap/minimum_certifiable_fpr_vs_n.svg`

"Clopper-Pearson gives an exact finite-sample answer. In the best case, with
zero honest tail flags, a one-percent claim needs 230 actions at 90 percent
confidence, 299 at 95 percent, and 459 at 99 percent.

One tail flag raises those requirements to 388, 473, and 662. The honest tail
and sample size directly determine whether the budget is supportable. Small
calibration sets can report one percent empirically even when the data cannot
back that statement."

## 1:20-2:10 - Core result

**Show:** Core pooled operating-point table and
`../crossenv_analysis/pooled_threshold_scan.svg`.

"We scored 2,007 honest actions from media processing, web scraping, and
clinical trial with the `multi` baseline.

The empirical threshold is 4.5. It flags 0.75 percent of honest actions, but
its upper bound is 1.06 percent at 90 percent confidence and 1.33 percent at
99 percent. So the one-percent claim is not certified.

The certified threshold is 5.0. It flags 0.40 percent, and even its 99 percent
upper bound is 0.87 percent.

On 49 attacks from matched environments, detection moves from 55.1 percent to
42.9 percent. That 12.2-point difference comes from using an operating point
whose one-percent claim is supported by the data. It is not a ranking change
or generic certification overhead."

## 2:10-2:45 - Cross-environment check

**Show:** `../crossenv_analysis/observed_fpr_by_environment.svg`.

"We expected possible cross-environment FPR drift, but did not observe it:
threshold 4.5 gives 0.91 percent in media, 0.84 percent in web, and zero in
clinical.

The validity issue still appears through sample size. Web at threshold 5.0
observes only 0.28 percent FPR, but with 356 actions its 90 percent upper bound
is 1.09 percent, so the environment-specific claim remains uncertifiable.

Pooling raises n from 1,314 to 2,007 and lowers the strict certified threshold
from 5.5 to 5.0. The finite-sample penalty becomes less restrictive with more
representative honest data, although the realized threshold changes in
half-point steps."

## 2:45-3:00 - Takeaway

**Show:** Final one-line takeaway.

"Certification does not make the monitor rank attacks better. It tells us
which audit-budget claims the data can support. It converts an observed rate
into an auditable finite-sample claim."
