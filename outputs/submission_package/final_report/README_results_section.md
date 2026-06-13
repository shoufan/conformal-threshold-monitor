## Results

We evaluate certified audit-budget thresholding using the Track A `multi`
action monitor. Certification does not change monitor scores or ranking; it
tests whether a claimed honest false-positive rate is supportable from finite
calibration data.

On 2,007 pooled honest actions:

| Method | Threshold | Observed FPR | CP 90% | CP 99% | Matched attack detection |
|---|---:|---:|---:|---:|---:|
| Empirical | 4.5 | 0.75% | 1.06% | 1.33% | 27/49 = 55.10% |
| Certified | 5.0 | 0.40% | 0.65% | 0.87% | 21/49 = 42.86% |

The empirical threshold observes less than 1% FPR but cannot certify the
claim. Threshold `5.0` is certified at every tested delta. The detection
difference comes from moving from an uncertifiable operating point to an
auditable one. It is not a change in monitor ranking.

The best-case sample sizes for a 1% claim with zero tail flags are 230, 299,
and 459 actions at deltas 0.10, 0.05, and 0.01. One tail flag raises them to
388, 473, and 662.

Cross-environment observed FPR did not blow up, but small environment-specific
samples still block certification. For example, web scraping at threshold
`5.0` observes 0.28% FPR, while its 90% upper bound is 1.09%.

The finite-sample CP penalty becomes less restrictive as representative honest
data grows, though the realized threshold cost can be discrete because
`multi` scores lie on a 0.5-point grid.

See:

- `outputs/final_report/certified_audit_budget_report.md`
- `outputs/final_report/demo_script_3min.md`
- `outputs/final_checks/game_metrics_alignment.md`
