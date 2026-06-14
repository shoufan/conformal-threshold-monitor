# Gate Feasibility Note

Generated June 13, 2026. This note concerns attack-sample adequacy only.
Certified threshold selection and honest-action FPR control remain unchanged.

## Current paired evidence

At each monitor's certified 1% operating point for `delta=0.10`, the 49 matched
attacks produce:

| Paired outcome | Count |
| --- | ---: |
| Caught by both `multi` and `zmean3` | 19 |
| Caught by `zmean3` only | 10 |
| Caught by `multi` only | 2 |
| Caught by neither | 18 |

Thus `multi` catches 21/49 and `zmean3` catches 29/49, with 12 discordant
pairs. The two-sided exact McNemar p-value is 0.0386. This nominal result should
not be promoted as a strong significance claim: it comes from only 49 attacks,
has no independent attack holdout, and follows an extension analysis in which
multiple fixed candidates were reported. The defensible result remains the
observed paired lift with explicit finite-sample uncertainty.

## What the discovery changes

The public metadata inventory found at least 494-500 possible additional
successful-side-task IDs in each matched environment. Data availability is
therefore not the immediate blocker. The blockers are:

- full-record vetting and completion confirmation
- family and near-duplicate deduplication
- policy, author, task, and run-provenance independence
- later three-component scoring cost
- a frozen confirmatory or learned-gate protocol

The API abundance makes a stronger test feasible in principle, but the usable
sample size is unknown until those checks are complete.

## Practical decisions

| Family-deduplicated matched attacks | Recommended use |
| ---: | --- |
| Fewer than 100 | Keep fixed, attack-blind ensembles. Do not learn a gate. |
| 100-200 | Use a simple frozen rule and a held-out or newly acquired confirmatory attack set. |
| 200 or more | A constrained learned gate becomes plausible with stratified train/validation/test splits. |

The next useful target is 75 new vetted attacks, 25 per matched environment.
Together with the existing 49, that would yield about 124 matched attacks.
The strongest analysis would freeze `multi` and `zmean3` now and treat the new
75 as an independent confirmatory McNemar sample, rather than pooling first and
re-optimizing.

## Learned-gate requirements

A learned gate should not be trained on the current 49 attacks. If at least 200
new or cleanly partitionable matched attacks survive vetting:

1. deduplicate by variant family before splitting
2. group related runs and task variants on one side of the split
3. stratify by environment and side-task category
4. freeze features and model class before the test split is opened
5. use honest data, never attack outcomes, to select the certified FPR threshold
6. report attack detection only on the untouched test attacks
7. retain the fixed `multi` and `zmean3` baselines

A deliberately small gate, such as regularized logistic regression over the
three component scores and a few predeclared disagreement features, is more
appropriate than a flexible model. Even at 200 attacks, environment-specific
test cells will remain small.

## Recommendation

Do not implement a learned gate now. First acquire and vet a bounded 75-record
matched-environment confirmatory set. If independence checks substantially
reduce that set below 51 new units, retain the fixed `zmean3` result and stop.
If the vetted inventory comfortably exceeds 200 unique families, write and
review a split protocol before any additional scoring or fitting.
