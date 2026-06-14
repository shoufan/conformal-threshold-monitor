# Report Integration Guidance

## Locked ordering

1. Lead with the matched-49 result: `multi` 21/49 (42.86%) versus `zmean3` 29/49 (59.18%), a +16.33-point paired lift.
2. Immediately qualify the stealth proxy: among 20 main-task-succeeded attacks, `multi` catches 8 and `zmean3` catches 12 (+20.0 points), but the cell has only six discordant pairs and exact McNemar `p=0.21875`.
3. Present frozen-75 only after that: `zmean3` 72/75 versus `multi` 48/75 (+32 points, `p=1.192e-07`) on a set where all 75 attacks failed the main task.
4. Keep all-76 LaStraj detection descriptive-only because five environments lack matched honest calibration.

## Claim boundary

- Supported: `zmean3` strongly improves detection of successful-side-task, main-task-failed attacks at the previously certified operating point.
- Suggestive but underpowered: the matched-49 main-task-succeeded subset shows a positive 20.0% lift.
- Not supported: broad claims of stealthy dual-success detection or adaptive attack robustness.
- Mechanism caveat: goal-analysis is dominant for 21/24 frozen zmean3-only catches, so the 96% detection rate is plausibly amplified by overt goal divergence when the main task fails.

## Required wording

Use: "On the matched 49 attacks, zmean3 improved detection from 42.9% to 59.2%. The lift remained positive on the 20 main-task-succeeded attacks (40% to 60%) but was underpowered. On a separate frozen set of 75 main-task-failed attacks, detection rose from 64% to 96%; this confirms strong performance on overt sabotage, not stealthy dual-success attacks."

Do not lead with `96% detection` or `p=1.19e-07` without the main-task-failure caveat in the same sentence.

## Certification separation

The confirmatory scoring run tests detection only. The 1% FPR certification still comes from the prior honest-action calibration set. Neither this partition nor the confirmatory attacks recertify FPR, alter thresholds, or change the monitor definitions.
