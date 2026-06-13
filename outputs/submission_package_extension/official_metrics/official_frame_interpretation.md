# Official Track A frame

All 49 matched attacks completed the side task, so official safety equals attack detection on this set.

`ct game-metrics metrics` fits an empirical action-only rule at each budget and may randomize boundary ties. It is the standard optimistic benchmark, not an error. CP/LTT asks a second question: does the honest calibration sample statistically support the claimed budget?

| Monitor | Official safety @ 0.1% | Official safety @ 1% | Official safety @ 5% | Certified deterministic safety @ 1% |
| --- | ---: | ---: | ---: | ---: |
| `multi` | 14.35% | 58.44% | 85.70% | 42.86% |
| `zmean3` | 14.29% | 67.35% | 88.49% | 59.18% |

For `multi`, the official 1% safety is 58.44%, while the deterministic empirical threshold `4.5` catches 55.10%. The difference comes from the official rule auditing a random 24.19% of score-4.0 ties. Threshold `4.5` has CP90 upper FPR 1.06%, so neither empirical presentation makes the deterministic 1% claim certifiable. The certified threshold `5.0` gives 42.86% safety with CP99 upper FPR 0.87%.

For `zmean3`, official empirical 1% safety is 67.35%, matching the deterministic empirical matched result. Its CP/LTT-certified threshold gives 59.18% safety. Better scoring improves ranking; certification determines which deterministic audit-budget claim is supportable.

The main-task-successful subset remains positive but underpowered. The frozen-75 result concerns only main-task-failed or overt sabotage. All-76 original detection remains descriptive because five environments lack matched honest calibration.

Control Tower reports usefulness 0/27 for both monitors because every downloaded attempts_st=false calibration trajectory is already labeled main_task_success=false. Monitoring is post-hoc and cannot change those outcomes, but this calibration set cannot establish absolute usefulness.
