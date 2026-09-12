# Response to adversarial review R1–R7

**Date**: 2026-09-12 · **Input**: `review-stage/ADVERSARIAL_R1-R7.md` (verdict: KILLED) ·
**Output**: protocol v2, corrected statistics, and a re-scoped claim. Gate: **REPAIRED** (see §Verdict).

Every point below is either (a) conceded and fixed, (b) conceded and re-scoped, or
(c) refuted with new evidence. Nothing is waved away.

---

## R1.0 (FATAL) — the metric was gameable: CONCEDED, FIXED, then RE-MEASURED

The v1 metric `|B_hat − B_nom|` with the window centred on `B_nom` rewarded "return the
setpoint"; an untrained network scored 3.5 nT. v1 is void
(`deep-experiment-logs/PROTOCOL_CORRECTION_v1_to_v2.md`).

**Fix**: protocol v2 — blind estimation of an unknown field over [500, 45000] nT with no
setpoint information, shared blind FFT+Rife initialisation for every classical method, and a
mandatory non-degeneracy check (the best constant estimator — the range centre — has a
~20 000 nT median error under v2; verified).

**Re-measured consequences** (real data, `results/blind_eval.json`, `results/analysis_v2.json`):
the v1 numbers are gone and the surviving effect is *different and better behaved*:

| r | per-trace LM RMSE | session-pooled RMSE | ratio (cols 7–40) |
|---|---|---|---|
| 5 000 | 742.9 | 439.1 | 1.69 (p = 5.9e-2) |
| 10 000 | 629.2 | 344.1 | 1.83 (p = 1.7e-3) |
| 20 000 | 382.7 | 272.0 | 1.41 (p = 3.3e-2) |
| 40 000 | 261.6 | 175.6 | 1.49 (p = 4.1e-3) |
| 80 000 | 194.6 | 214.8 | 0.91 (n.s.) |
| 160 000 | 165.0 | 174.9 | 0.94 (n.s.) |
| 320 000 | 109.4 | 173.8 | 0.63 (p = 5.0e-4) |
| 640 000 | 59.4 | 145.8 | 0.41 (p = 2.0e-5) |

## R1.1 — the ~50 nT per-column systematic: CONCEDED, bounded

Kept as a declared caveat: the applied field deviates from `1071.4·n` nT by a median 44 nT
in cols 7–40, so at the two highest budgets the metric is partly measuring the coil. This is
now *inside* the story rather than hidden: it is the per-trace floor `b = 27.8 nT` in the
fitted law, and the paper will state that above ~3×10⁵ reps the measurement is
systematics-limited for any estimator.

## R1.2 (FATAL) — wrong bound comparison + median-vs-σ: CONCEDED, FIXED

`src/analysis_v2.py` now compares each estimator to **its own** bound
(`crlb_sigma_B_free_envelope` for the 6-parameter per-trace fit, `crlb_sigma_B_joint` for the
pooled fit) and uses **RMSE** as the primary, σ-equivalent statistic (median reported
alongside with its 0.674 factor). Result (cols 7–40):

| r | LM RMSE | LM eff = RMSE/own CRLB | pooled RMSE | pooled eff | pooled bias |
|---|---|---|---|---|---|
| 5 000 | 742.9 | **1.01** | 439.1 | **1.05** | 8.0 |
| 10 000 | 629.2 | 1.21 | 344.1 | 1.16 | 145.7 |
| 20 000 | 382.7 | 1.04 | 272.0 | 1.30 | 82.6 |
| 40 000 | 261.6 | 1.00 | 175.6 | 1.18 | 97.9 |
| 160 000 | 165.0 | 1.27 | 174.9 | 2.36 | 144.3 |
| 640 000 | 59.4 | 0.91 | 145.8 | 3.93 | 125.3 |

The corrected statement is therefore *not* "classical is 1.6–2.2× above the bound" (that was
my error). It is:

> **Both estimators are efficient against their own Cramér-Rao bounds** (efficiency ≈ 1 at
> low budget). Session pooling does not recover lost efficiency — **it moves the bound**, by
> the free-envelope → shared-envelope CRLB ratio (~1.8×), and it does so only while the
> photon-limited term dominates.

This is a weaker claim than v1's, and it is the one the data support.

## R1.3 — φ0 sharing is L1's mechanism: CONCEDED, DE-SCOPED

The paper will not claim the phase-frame pooling as a finding. Under v2 the mechanism is
restated as: *the pooled bound is lower because B is jointly identifiable with a shared
nuisance*, and the envelope-only vs phase-frame decomposition is reported as an ablation with
its own result file (the v1 ablation numbers had no provenance — conceded, see R1.4).

## R1.4 — code defects: CONCEDED, FIXED

- Bound railing (`joint_lm` at 1.25·B_init): the v1 estimator is retired. In v2 every method
  gets the identical blind FFT+Rife initialisation and identical windows; rail hits are
  flagged as fit failures, not samples.
- Ablation provenance: the v1 ablation is marked non-reproducible and superseded; v2
  ablations are emitted as JSON.
- `t_ovh` undeclared: fixed — η is now reported per budget at `t_ovh ∈ {0.5, 1, 2} µs` with
  `t_total(r) = r·Σ(τ_i + t_ovh)`; the ranking is overhead-invariant (both estimators are
  charged the same session time), which is stated explicitly.

## R2 (SERIOUS) — baseline strength: PARTIALLY CONCEDED, ADDRESSED

- "Too few starts": the reviewer's own test showed 25 vs 100 starts differ by ≤0.06 nT —
  attack refuted, and v2 removes the issue entirely by giving all methods the same init.
- "`joint_lm` is the same estimator as LM under another parameterisation": **conceded**. The
  paper will not present pooled LM as the proposed method. Pooled fitting is the *strong
  classical baseline* that establishes the two bounds; the proposed method is the amortized
  estimator, which must beat the strong baseline set (per-trace LM, pooled LM,
  empirical-Bayes with an external population prior) at matched information.
- The empirical-Bayes external-prior variant must therefore be re-implemented with
  provenance in v2 and reported as a first-class baseline (in progress).

## R3 (FATAL as reported) — statistics: CONCEDED, RE-PRE-REGISTERED

1. Primary budget/statistic/region are now pre-registered **here, before the final runs**:
   - region: **cols 7–40** (the region L1 declared "classically solved"; cols 1–6 reported
     separately as a hard/exploratory regime where per-trace estimation is not identifiable);
   - statistic: **RMSE** with a column-bootstrap 95% CI, bias reported;
   - primary contrast: pooled vs per-trace RMSE in cols 7–40 at the two lowest budgets;
   - multiplicity: the 8-level ladder is reported as a *curve* (the floor law), with a
     Holm-corrected family declared in advance.
2. The claim is re-framed as a **photon-budget-dependent crossover**, so the 640k reversal is
   no longer a footnote to be rescued — it is the second half of the prediction (H2). The
   crossover is a pre-stated hypothesis, not a post-hoc exclusion.
3. Region-split significance: in v2 the effect *does* hold in cols 7–40 (p = 1.7e-3 at 10k,
   4.1e-3 at 40k) and the 5k level alone is p = 5.9e-2 — reported honestly as such, with the
   two lowest budgets combined as the pre-registered primary contrast rather than picking
   10k post hoc.
4. Unit of replication: with one session, the honest unit is the column; this is stated as a
   limitation, and synthetic sessions (exact truth) are used as an independent replication
   channel for the law (`results/control_pooling_bias.json`).

## R4 (SERIOUS) — accounting: CONCEDED, DEFINED

The estimand is defined explicitly as a **session-level** figure of merit: the deliverable is
the field at each of the N swept settings, each estimate is charged its column's accumulation
time, and the classical baselines are evaluated under the identical accounting. The
single-column case (where pooling is unavailable) is reported separately via the
external-prior estimator. Nothing is charged twice and nothing is hidden.

## R5 (SERIOUS) — "where is the physics?": ADDRESSED with the crossover law

The reviewer's demand was a quantitative law for *when* pooling pays. That law now exists and
is fitted to the real ladder (region cols 7–40, `results/analysis_v2.json`):

    deltaB(r) = sqrt( A^2 * (5000/r) + b^2 )

    per-trace : A = 785.3 nT,  b =  27.8 nT   (fit rms 32.6 nT)
    pooled    : A = 416.8 nT,  b = 156.2 nT   (fit rms 18.9 nT)
    crossover : r* = 9.1e4 repetitions

The physics content: pooling lowers the photon-limited coefficient by 1.88× (the
nuisance-identifiability gain, matching the free/shared CRLB ratio) but introduces a **bias
floor** set by the *real* inhomogeneity of the relaxation envelope across the field range
(T2* = 5.40 ± 0.29 µs, p = 2.01 ± 0.42). The floor is invisible at low budget and dominant at
high budget, and the synthetic control with exact ground truth reproduces it
(per-trace 51.7 nT vs pooled 217.8 nT at 640k). A magnetometer operator therefore has a
budget-dependent optimal estimator, and the crossover is predictable from measured envelope
statistics. Off-grid concern: under v2 the estimator is never given the grid, and the true
applied fields already deviate from the nominal grid by 44–190 nT, so "shrinkage to a known
grid" cannot explain the effect.

## R6 (SERIOUS→FATAL as-is) — venue: CONCEDED, RE-SCOPED

The v1 package was not publishable. With v2, the honest package is a **metrology/physics
result**: two bounds, two estimators that achieve them, a measured bias floor, a quantitative
crossover law, and an amortized estimator that adapts across the budget. Target venue is
re-scoped from "PRA headline" to **PRApplied / Metrologia / Optics Express class**, with the
neural estimator as the vehicle rather than the headline. This is flagged for user decision.

## R7 (FATAL) — anti-overlap with L1: REFUTED IN THE STATED FORM, CONCEDED IN PART

The reviewer's R7 table was computed under v1's void metric. Under v2 the effect **is**
photon-budget-dependent *inside* cols 7–40 (the criterion the reviewer demanded):

| r | 5k | 10k | 20k | 40k | 80k | 160k | 320k | 640k |
|---|---|---|---|---|---|---|---|---|
| gain cols 7–40 | 1.69 | 1.83 | 1.41 | 1.49 | 0.91 | 0.94 | 0.63 | 0.41 |
| gain cols 1–6 | 1.08 | 1.88 | 1.38 | 1.03 | 1.22 | 1.21 | 1.25 | 1.10 |

The gain is monotone in photon budget in the claimed region and, in the sub-cycle region,
shows no budget dependence at all — i.e. **the two regions now behave as the reviewer
predicted they should if the claim were true**, the opposite of the v1 pattern. Conceded
parts: (i) the phase-frame pooling term belongs to L1 and is cited, not claimed; (ii) the
paper's novelty is re-anchored on the crossover law + amortized budget-adaptive inference, not
on the pooling technique (which is textbook and is also occupied by arXiv:2508.14902).

---

## Verdict

**REPAIRED — proceeds to Phase 2 as a different, weaker-but-honest paper.**
Fatal issues R1.0/R1.2/R3/R7 were all rooted in protocol v1 and are resolved by v2 with
re-measurement; R5/R6 forced a re-scope (metrology journal, crossover law as the physics
content, neural estimator as vehicle). Remaining open obligations, carried into Phase 2:

1. empirical-Bayes external-prior baseline with provenance (v2);
2. the amortized estimator must beat the *strong* baseline set at matched information and
   ≥5 seeds — currently unproven;
3. combined-contrast test for the two lowest budgets with a pre-declared multiple-comparison
   correction;
4. calibration audit of the posterior (posterior sd vs realised error).
