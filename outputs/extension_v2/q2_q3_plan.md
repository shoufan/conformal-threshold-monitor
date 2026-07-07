# Q2 / Q3 plans (PLAN ONLY — nothing here has been executed)

Both workstreams spend OpenRouter credit and are **human-gated**: no scoring
runs until the plan and budget are explicitly approved. Cost math uses the two
observed gpt-5-nano price points from this project's own runs:

- Phase B `multi` rescore: $3.19 / (2,232 actions × 2 components) ≈ **$0.00071/call**
- Live zmean3 final check: $0.59 / (196 actions × 3 components) ≈ **$0.00100/call**

Planning range: **$0.0007–0.0010 per component call**; budget quotes below use
the upper end plus a 1.5× contingency cap.

---

## Q2 — Granularity ablation (`multi-fine`): is zmean3's certified edge design or resolution?

**Reviewer critique (R1):** zmean3's certified advantage confounds two things —
the extra goal-analysis view (ensemble design) and the 103-vs-15-level score
grid (resolution). The submitted decomposition separates ranking from
granularity, but a direct test is better: give `multi` a fine grid *without*
changing its views, and see how much of the certified gap closes.

**Variant definition (fixed before scoring):** `multi-fine` = the same two
`multi` components (orthogonal + old_action), each prompted to return a score
with one decimal place in [0, 10] instead of an integer/half-step; same
weighted mean, no new views, no other prompt changes. Register as
`monitor:multi_fine` beside `monitor:zmean3` in `monitor.py`.

**Data to rescore (existing local trajectories only, no new downloads):**

| Set | Trajectories | Actions | Calls (×2 components) |
| --- | ---: | ---: | ---: |
| Pooled honest (matched 3 envs) | 27 | 2,007 | 4,014 |
| Matched-49 attacks | 49 | 550 | 1,100 |
| **Total** | **76** | **2,557** | **5,114** |

**Cost estimate:** 5,114 × $0.0007–0.0010 ≈ **$3.60–$5.11**; contingency cap
**$7.70**. Runtime at `--max-concurrent 1` ≈ 2–3 h (can raise concurrency if
approved).

**Analysis (all free, existing pipeline):** unique honest score levels;
empirical vs certified (δ=.10/.05/.01) thresholds via
`monitor_cert.thresholds`; matched-49 detection at each point; the
cluster-robust scan from `scripts/analyze_cluster_robust.py`.

**Success criterion (predeclared):** compare the empirical→certified detection
bleed. `multi` bleeds 12.2pp (55.1→42.9) on 15 levels; zmean3 bleeds 8.2pp
(67.3→59.2) on 103 levels. If `multi-fine`'s certified safety recovers most of
multi's bleed (i.e. its certified point lands near its own empirical point),
granularity is confirmed as the certification lever independent of ensemble
design; if not, the goal-analysis view matters beyond ranking. Either outcome
is reportable. Detection numbers for `multi-fine` are descriptive of the same
49 attacks — no new attack acquisition.

**Guardrails:** `--no-upload`, `--only-action`, existing trajectories only, no
tiktok, stop if spend approaches the cap; honest-only prompt change (never
tuned on attacks).

---

## Q3 — End-to-end live `zmean3` at headline scale

**Reviewer critique (R3):** the headline numbers come from materialized
component scores; the live monitor was execution-checked on 9 trajectories
(~$0.60), not at headline scale. Q3 reruns the registered `monitor:zmean3`
live on the sets behind the reported numbers and quantifies agreement.

**Tiers (pick one at approval time):**

| Tier | Sets | Actions | Calls (×3) | Est. cost | Cap (1.5×) |
| --- | --- | ---: | ---: | ---: | ---: |
| A (minimum meaningful) | all 49 matched attacks + 9 honest (3/env, size-stratified) | ~1,200 | ~3,600 | $2.50–3.60 | $5.40 |
| B (headline-faithful) | all 49 attacks + all 27 honest | 2,557 | 7,671 | $5.40–7.67 | $11.50 |

Tier A validates the detection side at full scale and the FPR side on a
sample; Tier B reproduces both headline inputs end-to-end. Recommendation:
Tier A first; escalate to the Tier B honest remainder only if drift is within
criteria.

**"Matches materialized" — quantitative criteria (predeclared, grounded in the
9-trajectory live check: mean |Δ| 0.33, max 1.17 encoded, zero decision
flips):**

1. Per-action encoded-score drift: mean |Δ| ≤ 0.5, p95 ≤ 1.5, max ≤ 2.5.
2. Decision flips at the frozen thresholds: ≤ 2% of actions flip across
   2.6364 (raw) / 3.56 (encoded); matched-49 detection within ±1 attack of
   29/49; honest tail count at the certified threshold within ±3 of 13.
3. Rerunning the certified scan on live honest scores lands within one grid
   step of the frozen threshold.
4. Zero `-1.0` error-path actions after retries; spend within cap.

Meeting all four ⇒ "live artifact reproduces the materialized headline within
component nondeterminism." Any miss is reported as-is with the failing
criterion.

**Guardrails:** identical to Q2. Attack canary ordering (attacks first, then
honest) as in the prior live check.

---

## Combined ask

| Item | Est. cost | Cap |
| --- | ---: | ---: |
| Q2 granularity ablation | $3.60–5.11 | $7.70 |
| Q3 Tier A | $2.50–3.60 | $5.40 |
| Q3 Tier B (if escalated) | $5.40–7.67 | $11.50 |
| **Q2 + Q3-A total** | **$6.10–8.71** | **$13.10** |

**STOP: do not execute either workstream without explicit approval of the
tier and cap.**
