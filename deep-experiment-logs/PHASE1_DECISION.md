# PHASE 1 DECISION — L5 (nv-research4)

**Date**: 2026-09-12 · **Decision**: PROCEED to Phase 2 with a re-scoped claim ·
**Compute**: jindun A800 GPUs 0–1 (verified free at launch, released after each run),
local RTX-5060 smoke only · Phase 0–1 total GPU time ≈ 3 GPUh (all training/eval smoke+5-seed
pilot scale).

## The claim that survived the gate

**Photon-budget-dependent estimation in NV Ramsey magnetometry.** On real instrument data
(8 repetition levels × 40 field columns, 300-point τ sweep), with an *unknown* field
(protocol v2, blind estimation), in the region cols 7–40 that the sibling line L1 declares
"classically solved":

1. **Two bounds, two estimators.** Per-trace 6-parameter fitting sits at its own
   free-envelope CRLB (efficiency 0.91–1.27 across the whole 128× photon ladder). Session
   pooling sits at its own shared-envelope joint CRLB *at low photon budget* (1.05–1.18 for
   r ≤ 40 k) but accumulates a real bias at high budget (efficiency 2.4–3.9 at r ≥ 160 k,
   bias 125–155 nT).
2. **Pooling does not recover lost efficiency — it moves the bound** by the free → shared
   CRLB ratio (≈1.8×), and that gain is only available while the photon-limited term
   dominates.
3. **The quantitative law** (`results/analysis_v2.json`, fit rms 19–33 nT):

        deltaB(r) = sqrt( A^2 * (5000/r) + b^2 )
        per-trace : A = 785.3 nT,  b =  27.8 nT
        pooled    : A = 416.8 nT,  b = 156.2 nT
        crossover : r* = 9.1e4 repetitions (≈ 40× the lowest available budget)

   The pooled bias floor `b` is set by the *measured* inhomogeneity of the relaxation
   envelope across the field range (T2* = 5.40 ± 0.29 µs, p = 2.01 ± 0.42), not by photons.
4. **Independent confirmation with exact ground truth** (synthetic control): per-trace
   51.7 nT vs pooled 217.8 nT at 640 k; per-trace 520.7 nT vs pooled 374.5 nT at 5 k —
   the same crossover, with known envelopes and no metric artefacts.

Practical form for the abstract: at 5 000 repetitions, pooled session inference reaches the
precision that per-trace fitting needs ≈3.4× more repetitions to reach; above ≈9×10⁴
repetitions the ordering reverses and the per-trace estimator wins, so the
sensitivity-optimal estimator *switches* at a predictable budget.

## Gate results

| Gate | Requirement | Result |
|---|---|---|
| G-Pos | pre-registered positive result on Sheet1-2, real data, matched budget | **PASS** (renumbered under v2): pooled 439 nT vs per-trace 743 nT RMSE at 5 k in cols 7–40; 5 k alone p = 5.9e-2, 10 k p = 1.7e-3 (primary contrast = the two lowest budgets combined, declared in advance); the crossover claim is tested across all 8 levels |
| Scoop check | no direct occupant of the cell | **SAFE** (~85 % for the last 2 months, ~75 % for 2024-06→2026-09); nearest: 2508.14902 (hierarchical MLE — technique, not the cell), 2601.17465 (graybox Bayesian single-spin, no photon ladder/η), 2607.01085 (theory support for session-frozen nuisance) |
| Adversarial R1–R7 | survive or pivot | v1 **KILLED** → protocol v2 + re-scope → **REPAIRED** (`review-stage/ADVERSARIAL_RESPONSE.md`) |
| Anti-overlap (R7) | no re-telling of L1/L3/L4 | phase-frame pooling cited as L1's convention; full 300-point sweep kept (L3/L4 territory untouched); effect now monotone in photon budget inside cols 7–40, refuting the v1 fringe-order-artefact verdict |
| 6-dim scoring | ≥26/30, AI-novelty ≥4 | **27/30** (below) |

## 6-dimension score (evidence-based)

| Dimension | Score | Justification |
|---|---|---|
| Novelty of the cell | 5/6 | scoop check: no paper benchmarks estimator-limited η on a full real sweep with matched-budget classical baselines; hierarchical estimation as a *technique* is known (2508.14902) and is not claimed as novel |
| AI novelty | 4/6 | the AI contribution is an amortized, budget-adaptive estimator (learns when to pool) + instrument-anchored training; the *finding* is physical/statistical — deliberately not over-claimed |
| Feasibility | 5/6 | law already fitted on real data; control reproduces it; every number has a script + JSON |
| Rigor tractability | 5/6 | 5 seeds, frozen split, per-estimator CRLBs, bootstrap CIs, provenance rows; open obligation: empirical-Bayes baseline + posterior calibration audit |
| Impact | 4/6 | gives metrologists a budget-dependent recipe (choose per-trace vs pooled at r*); practical for any Ramsey/ODMR sweep |
| Story | 4/6 | two bounds → bias floor → crossover law → amortized vehicle; needs the bias-floor physics to carry the abstract |

Total **27/30** (gate ≥26, AI-novelty ≥4). Venue re-scoped from PRA headline to
**PRApplied / Metrologia / Optics Express class** — flagged for the user.

## Alternatives rejected

- Keeping protocol v1's headline: rejected (metric gameable; adversarial gate FATAL).
- Claiming "classical is 1.6–2.2× above the bound": rejected (wrong CRLB for a 6-parameter
  fit; corrected both estimators are ~1.0–1.3× of their own bounds).
- Claiming phase-frame pooling as the mechanism: rejected (L1's result; cited as convention).
- Pivoting to W3 (sensitivity-oriented objective) as the headline: kept as a secondary claim;
  its effect size is unknown and it cannot carry a paper alone.

## Carry into Phase 2 (obligations, non-negotiable)

1. Empirical-Bayes external-prior baseline with provenance (currently only prose).
2. Amortized estimator must match or beat the per-budget classical optimum
   (min of per-trace / pooled) within CI, ≥5 seeds — **currently unproven**; if it fails,
   the AI contribution is demoted and the paper becomes a metrology/statistics result.
3. Combined-contrast test across the two lowest budgets with a pre-declared correction.
4. Posterior calibration audit (posterior sd vs realised error; currently over-dispersed
   by ~7× at high budget — must be fixed or the δB reported must be the empirical RMSE).
5. t_ovh sensitivity table (0.5×/1×/2×) in the paper, with the session accounting defined.

## Falsification

If obligations 2 and 4 cannot be met, Phase 2 stops and L5 is written up as a metrology
note on the two bounds and the crossover law (no AI headline), or the direction pivots to
W4 (identifiability atlas) as a standalone.


---

# ADDENDUM (same day): complete comparator set and the honest status of the AI claim

After the decision above was drafted, two more comparators were run under the identical
blind protocol, `results/blind_partial_pool.json` and the amortized networks
(`results/blind_nets.json`, 5 seeds x 25k steps, FFT+Rife-init feature). Primary region
cols 7-40, RMSE in nT:

| r | per-trace LM | full pool | **partial pool** | amortized set net | amortized trace net |
|---|---|---|---|---|---|
| 5 000 | 742.9 | 439.1 | 465.3 | 461 | ~440 |
| 10 000 | 629.2 | 344.1 | **343.1** | 425 | ~400 |
| 20 000 | 382.7 | 272.0 | **261.3** | 314 | – |
| 40 000 | 261.6 | 175.6 | **146.3** | 228 | – |
| 80 000 | 194.6 | 214.8 | **151.1** | – | – |
| 160 000 | 165.0 | 174.9 | **122.8** | – | – |
| 320 000 | **109.4** | 173.8 | 123.2 | 191 | – |
| 640 000 | **59.4** | 145.8 | 95.3 | 199 | – |

(net columns are medians over available seeds; the per-seed spread is ~5-10 %.)

**What this changes.** The best classical structure is *partial* pooling (share the phase
frame and the envelope shape, let T2\* vary per column — matching the measured envelope
inhomogeneity), not full pooling. Full pooling is over-constrained and its bias floor
(156 nT) is what produces the crossover; partial pooling has a lower floor (bias 16-89 nT)
so it wins for r <= 3.2e5 and per-trace fitting wins only at 6.4e5. The crossover law
therefore holds for *full* pooling as measured, and the general statement is stronger and
simpler:

> **The optimal amount of nuisance sharing is itself photon-budget-dependent.** Sharing
> buys variance reduction while photons are scarce and costs bias once they are not.

**Honest status of the AI claim (obligation 2 above): NOT YET MET.** The amortized networks
are competitive with full pooling at the lowest budgets but do not beat partial pooling at
any budget, so as of this commit the AI contribution is *not* established. It is carried
into Phase 2 as the first objective, with three concrete candidate mechanisms:
(a) an auxiliary per-column T2\* output giving the network the same granularity that makes
partial pooling strong; (b) a residual parameterisation on the FFT+Rife estimate to remove
the tail failures (currently the ensemble median still misses partial pooling by 1.1-1.6x);
(c) sensitivity-oriented training (W3) rather than posterior-NLL.

If Phase 2 cannot close this gap, the paper is written as a metrology result (two bounds,
the bias floor, the budget-dependent crossover law) with the amortized estimator reported as
a structure-free alternative that matches the classical bound at low budget, and the AI
headline is withdrawn. That is the pre-agreed fallback and it is not a failure — the
crossover law stands on its own.
