# Gated `goal-analysis` Scoring Plan

## Gate Status

This document prepares commands only. No scoring, model call, OpenRouter budget
query, network request, Hawk job, evaluation, upload, or submission was run.

`goal-analysis` is locally registered, defaults to trusted `gpt-5-nano`, and
can score existing trajectory JSON with `--only-action`.

## Planned Inputs

| Dataset | Trajectories | Estimated monitorable actions | Nominal calls |
| --- | ---: | ---: | ---: |
| Honest `media_processing` | 15 | 1,314 | 1,314 |
| Honest `web_scraping` | 5 | 356 | 356 |
| Honest `clinical_trial` | 7 | 338 | 338 |
| LaStraj attacks | 76 | 919 | 919 |
| **Total** | **103** | **2,927** | **2,927** |

The estimates mirror the v1 `multi` manifests. Completed `multi` scoring
yielded 2,925 fully reusable actions after one persistent attack skip and one
incomplete clinical-trial ensemble response. The goal-analysis pass may recover
or lose a small number of actions independently; final analysis must use the
valid three-component intersection.

## Cost Basis

`goal-analysis` and `old-action` are both one-call, trusted `gpt-5-nano`,
history-aware monitors. Existing `old-action` member usage on the same
trajectory inventory is therefore the closest local cost analogue.

Token-priced estimates use the rates already applied in the v1 report:

- non-cached input: `$0.05 / 1M`
- cached input: `$0.005 / 1M`
- output: `$0.40 / 1M`

| Dataset analogue | Calls | Input tokens | Output tokens | Cached input | Estimated cost |
| --- | ---: | ---: | ---: | ---: | ---: |
| Honest `media_processing` | 1,314 | 7,706,024 | 1,455,431 | 31,011,072 | $1.1225 |
| Honest `web_scraping` | 356 | 1,418,705 | 410,281 | 6,064,000 | $0.2654 |
| Honest `clinical_trial` | 338 | 1,932,933 | 349,481 | 4,748,032 | $0.2602 |
| Attacks | 918 observed; 919 planned | 3,706,391 | 1,089,990 | 3,889,664 | $0.6408 |
| **Total analogue** | **2,926** | **14,764,053** | **3,305,183** | **45,712,768** | **$2.2888** |

The one-call difference is negligible at this precision. A 50% contingency for
prompt-length differences, retries, and cache behavior gives:

```text
estimated upper bound = $2.2888 * 1.5 = $3.4333
```

This is below the `$10` stop threshold. It still requires explicit human
approval before execution.

## Exact Commands

Run from the repository root only after approval:

```bash
CT=work/hackos-5-quickstart/A_MonitorBuilding/.venv/bin/ct
```

### Honest: media_processing

```bash
"$CT" run monitor \
  data/honest/attempts_st_false_sample \
  --action-monitor goal-analysis \
  --action-monitor-arg model=trusted \
  --only-action \
  --max-concurrent 2 \
  --save-dir outputs/goal_analysis_scored/honest_media \
  --run-name certified-monitor-goal-analysis-honest-media \
  --no-upload
```

### Honest: web_scraping

```bash
"$CT" run monitor \
  data/honest/crossenv/web_scraping \
  --action-monitor goal-analysis \
  --action-monitor-arg model=trusted \
  --only-action \
  --max-concurrent 2 \
  --save-dir outputs/goal_analysis_scored/honest_web \
  --run-name certified-monitor-goal-analysis-honest-web \
  --no-upload
```

### Honest: clinical_trial

```bash
"$CT" run monitor \
  data/honest/crossenv/clinical_trial \
  --action-monitor goal-analysis \
  --action-monitor-arg model=trusted \
  --only-action \
  --max-concurrent 2 \
  --save-dir outputs/goal_analysis_scored/honest_clinical \
  --run-name certified-monitor-goal-analysis-honest-clinical \
  --no-upload
```

### Attacks: all LaStraj

```bash
"$CT" run monitor \
  data/attacks/lastraj \
  --action-monitor goal-analysis \
  --action-monitor-arg model=trusted \
  --only-action \
  --max-concurrent 2 \
  --save-dir outputs/goal_analysis_scored/attacks \
  --run-name certified-monitor-goal-analysis-attacks \
  --no-upload
```

## Execution Order and Stop Rules

1. Reconfirm trajectory counts and estimated monitorable actions.
2. Obtain explicit approval for the `$2.29` estimate and `$3.43` contingency.
3. Run honest media first and inspect model name, action count, errors, and
   realized cost.
4. Re-estimate remaining cost from that run before continuing.
5. Stop immediately if the resolved model is not `gpt-5-nano`, upload is
   enabled, errors repeat broadly, or the projected total exceeds `$10`.
6. Do not add `strong`, run `ct run eval`, run Hawk, or query a provider API.

## Confidence

| Claim | Confidence |
| --- | --- |
| CLI name and syntax | high |
| One nominal model call per monitorable action | high |
| Same existing trajectories can be scored | high |
| Cost remains below `$10` | high |
| Point estimate near `$2.29` | medium; prompt and cache behavior differ |
