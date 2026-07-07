# Cluster-robust certification (reviewer i.i.d. critique)

**Branch:** `extension-v2` (submitted state `32b1ca8` on `main` is frozen as-judged).
**Scope:** pure analysis of existing local score files. No model calls, no scoring
runs, no uploads. Numbers here are *extensions*, not revisions, of the submitted
results.

Reproduce:

```bash
PYTHONPATH="$PWD" .venv/bin/python scripts/analyze_cluster_robust.py --seed 20260706 --reps 10000
```

Machine-readable tables: [`cluster_robust_tables.json`](cluster_robust_tables.json).

## What the reviewers said

All three reviewers made the same point: the CP/LTT certification treats honest
*actions* as i.i.d., but actions are correlated within trajectories — the 2,007
pooled honest actions come from only 27 trajectories, so the effective sample
size is smaller than the nominal count and the certified bounds may be
optimistic. This analysis quantifies the violation and recomputes the bounds
with two cluster-aware estimators.

## Data

| Monitor | Honest actions | Trajectories | Actions/trajectory (min/med/max) | Source |
| --- | ---: | ---: | --- | --- |
| `multi` | 2,008 | 27 | 48 / 67 / 143 | materialized matched inputs |
| `zmean3` (raw) | 1,989 | 27 | 47 / 67 / 142 | aligned ensemble components |

The `multi` set carries one more action (score 1.0, outside every relevant
tail) than the 2,007 used in the submitted certification — the same benign +1
noted in the official-metrics audit. Tail counts are identical to the reported
ones (15 at 4.5, 8 at 5.0; zmean3 19 at its empirical threshold 2.3693, 13 at
the certified 2.6364), and the matched-49 detection numbers reproduce exactly
(27/49, 21/49, 33/49, 29/49).

## ICC, design effect, effective sample size

One-way ANOVA ICC (unbalanced); DEFF = 1 + (m̄ − 1)·ρ with m̄ = mean cluster
size (≈ 74); n_eff = n / DEFF.

| Monitor | Quantity | ICC | DEFF | n_eff |
| --- | --- | ---: | ---: | ---: |
| `multi` | raw scores | 0.0528 | 4.88 | **412** |
| `multi` | tail indicator @4.5 | −0.0028 | 1.00 | 2,008 |
| `multi` | tail indicator @5.0 | −0.0043 | 1.00 | 2,008 |
| `zmean3` | raw scores | 0.0315 | 3.29 | **605** |
| `zmean3` | tail indicator @2.3693 (empirical) | 0.0056 | 1.41 | 1,411 |
| `zmean3` | tail indicator @2.6364 (certified) | 0.0048 | 1.35 | 1,475 |

**The key empirical fact:** the correlation lives in the score *levels*, not in
the tail *exceedances*. Trajectories share a suspicion level (raw-score ICC
0.03–0.05 → n_eff of only ~400–600), but which actions cross the audit
threshold is close to independent across trajectories — multi's 15 flags at
4.5 are spread over 12 of 27 trajectories, and its indicator ICC is slightly
negative. The FPR bound depends on the indicator, so the certified operating
points move far less than the raw-score DEFF alone would suggest. Both facts
are reported; each drives a different correction below.

## Corrected bounds at the operating points

`n` = 2,008 (multi) / 1,989 (zmean3). Bootstrap = trajectory-cluster bootstrap,
10,000 reps, seed 20260706, one-sided percentile upper bounds.
DEFF-CP = Clopper-Pearson at (k/DEFF, n/DEFF) with the threshold-specific
indicator DEFF (floored at 1).

| Monitor / threshold | k | Obs FPR | Naive CP 90/95/99 | Bootstrap 90/95/99 | DEFF-CP 90/95/99 | Certified ≤1%? (naive / boot / DEFF) |
| --- | ---: | ---: | --- | --- | --- | --- |
| multi 4.0 | 36 | 1.793% | 2.23 / 2.36 / 2.61% | 2.13 / 2.23 / 2.43% | 2.23 / 2.36 / 2.61% | no / no / no |
| multi 4.5 (empirical) | 15 | 0.747% | 1.06 / 1.15 / 1.33% | 0.96 / 1.02 / 1.13% | 1.06 / 1.15 / 1.33% | no / δ=.10 only / no |
| multi 5.0 (certified) | 8 | 0.398% | 0.65 / 0.72 / 0.86% | 0.56 / 0.60 / 0.69% | 0.65 / 0.72 / 0.86% | yes / yes / yes |
| multi 5.5 | 5 | 0.249% | 0.46 / 0.52 / 0.65% | 0.39 / 0.43 / 0.51% | 0.46 / 0.52 / 0.65% | yes / yes / yes |
| zmean3 2.3693 (empirical) | 19 | 0.955% | 1.30 / 1.40 / 1.60% | 1.30 / 1.41 / 1.62% | 1.38 / 1.50 / 1.75% | no / no / no |
| zmean3 2.4858 | 14 | 0.704% | 1.01 / 1.10 / 1.28% | 0.99 / 1.09 / 1.28% | 1.06 / 1.16 / 1.37% | no / δ=.10 only / no |
| zmean3 2.6364 (certified) | 13 | 0.654% | 0.95 / 1.04 / 1.21% | 0.94 / 1.04 / 1.22% | 1.01 / 1.12 / 1.33% | δ=.10 / δ=.10 / **no** |
| zmean3 2.8017 | 11 | 0.553% | 0.83 / 0.91 / 1.08% | 0.84 / 0.93 / 1.11% | 0.92 / 1.02 / 1.24% | δ≤.05 / δ≤.05 / δ=.10 |

Two readings, both honest:

- **multi's certified point (5.0) is cluster-robust.** Its tail flags are
  unclustered, so the DEFF adjustment changes nothing and the bootstrap agrees.
  The submitted 42.86% certified safety stands under every estimator here.
- **zmean3's certified point (2.6364) is *not* robust to the DEFF adjustment at
  δ=0.10:** adjusted CP90 = 1.013% > 1%. The cluster-robust scan moves the
  certified threshold up one grid step (see below).
- **Do not read the bootstrap column as a license to certify.** At multi 4.5 the
  bootstrap 90% upper (0.955%) sits *below* the naive CP90 (1.059%) — the
  percentile bootstrap is anti-conservative for rare events with 27 clusters
  (see limitations). We treat the DEFF-adjusted CP as the corrected bound and
  the bootstrap as a diagnostic.

## Cluster-robust certification scan (descending fixed-sequence LTT, δ = 0.10)

Same scan as `monitor_cert.thresholds.certified_threshold`, with the
DEFF-adjusted CP bound (threshold-specific indicator DEFF) as the p-value
source. Detection is per-attack-trajectory max ≥ threshold on the matched 49.

| Monitor | Certified threshold (naive → robust) | Certified matched-49 detection (naive → robust) |
| --- | --- | --- |
| `multi` | 5.0 → **5.0** (unchanged) | 21/49 = 42.86% → **21/49 = 42.86%** |
| `zmean3` | 2.6364 → **2.8017** (+1 grid step) | 29/49 = 59.18% → **28/49 = 57.14%** |

**zmean3's certified advantage survives the cluster correction:** 57.14% vs
42.86%, a +14.3pp gap (was +16.3pp). One attack (the one caught between 2.6364
and 2.8017) is the entire price of cluster-robustness at δ=0.10.

## Trajectory-level certification (secondary)

Trajectory-level FPR = P(honest trajectory has ≥1 flagged action); n = 27
trajectories.

| Quantity | δ=0.10 | δ=0.05 | δ=0.01 |
| --- | ---: | ---: | ---: |
| Zero-flag CP upper bound (k=0, n=27) | 8.17% | 10.50% | 15.68% |
| Observed: multi @5.0 flags 7/27 (25.9%) → CP upper | 39.7% | 43.2% | 49.8% |
| Observed: zmean3 @2.6364 flags 9/27 (33.3%) → CP upper | 47.5% | 50.9% | 57.4% |
| Minimum trajectories to certify a 1% trajectory-level claim | 230 | 299 | 459 |

Sanity check passes: 1 − 0.10^(1/27) = 8.17%. At the trajectory level nothing
approaching 1% is certifiable from 27 trajectories — even a monitor with zero
flagged trajectories could only claim ≤8.2% at δ=0.10, and ~230–459
*trajectories* (roughly 10–20× the current 27) would be needed. Per-action and
per-trajectory budgets are different claims; the submitted certification is
per-action, and this section quantifies how far the data are from supporting
the trajectory-level analogue.

## Corrected minimum-n floor (headline for the writeup)

The submitted floor — 230/299/459 honest actions at δ=.10/.05/.01 with zero
tail flags — counts *effective* (independent) actions. With the observed
clustering, the raw pooled-action requirement becomes DEFF × floor:

| Basis | DEFF | Raw actions needed, δ=0.10 | δ=0.05 | δ=0.01 |
| --- | ---: | ---: | ---: | ---: |
| i.i.d. (submitted) | 1.00 | 230 | 299 | 459 |
| `zmean3` boundary indicator DEFF | 1.50 | 346 | 450 | 690 |
| `zmean3` raw-score DEFF | 3.29 | 757 | 984 | 1,510 |
| `multi` raw-score DEFF | 4.88 | 1,122 | 1,458 | 2,238 |

Corrected claim for the writeup: **under trajectory clustering, the honest-data
cost of a certifiable 1% budget is roughly 1.5× (indicator-level) to 3–5×
(score-level) the i.i.d. floor** — for trajectories like these (~74 actions
each), that is on the order of 5–30 honest trajectories rather than 3–6, and
the i.i.d. floor of 230–459 actions is a lower bound that a handful of runs
clears even less often than the submitted report claimed. The validity gap
widens; the thesis strengthens.

## Takeaway

The reviewers' i.i.d. concern is real and quantifiable: honest scores are
trajectory-correlated (ICC 0.03–0.05; n_eff ≈ 412–605 of 2,008/1,989). But the
correlation concentrates in score *levels*, not tail *exceedances*, so the
certified operating points are far more robust than the raw design effect
suggests: multi's certified point is unchanged, zmean3's moves one grid step
(59.18% → 57.14% certified matched-49 safety), and zmean3's certified edge over
multi survives (+14.3pp). The min-n floor, restated in raw actions, grows by
1.5–5×, which *strengthens* the submitted headline that small honest samples
cannot support 1% claims. Both pillars of the submission survive their own
robustness audit — with one honest revision (zmean3 2.6364 → 2.8017 at δ=0.10)
that we adopt rather than defend.

## Limitations of this analysis

- **27 clusters is few.** The trajectory bootstrap resamples only 27 units; the
  percentile method is anti-conservative for rare-event proportions at this
  cluster count (visible above: bootstrap upper < naive CP at several rows).
  The DEFF-adjusted CP is the estimator we rely on; the bootstrap is a
  diagnostic.
- **ICC is estimated from the same small sample** it is meant to correct, and
  indicator ICCs rest on 8–19 flags; DEFF values of 1.3–1.5 are noisy. Negative
  ICC estimates are floored at zero (DEFF = 1), which is anti-conservative if
  the true indicator ICC is positive but masked by noise.
- **Rao-Scott scaling of CP is approximate** (continuous pseudo-counts in an
  exact binomial bound); it inherits the usual design-effect approximation
  error and is not an exact finite-sample guarantee under clustering.
- **Zero-flag bootstrap degeneracy:** where a resample draws no flagged
  trajectory the proportion is 0; at thresholds with concentrated flags this
  compresses lower quantiles. The zero-flag replicate share is reported per
  row in the JSON (nonzero only at multi 5.5: 1.3%).
- The `multi` set here has 2,008 actions vs the submitted 2,007 (one extra
  score-1.0 action outside every tail); bounds differ in the 4th decimal.
- Environment mix and the all-main-task-failed calibration caveats from the
  submitted report carry over unchanged.
