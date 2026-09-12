# Protocol correction: v1 (VOID) → v2 (blind task)

**Date**: 2026-09-12 · **Trigger**: adversarial gate R1/R3 (`review-stage/ADVERSARIAL_R1-R7.md`)

## What was wrong with v1

v1 evaluated `|B_hat − B_nom|` with the estimation window centred on `B_nom` = 1071.4·n nT,
i.e. **the applied setpoint itself**. The applied field equals the setpoint to within the
instrument systematic (median 51 nT across the 40 columns), so the constant estimator
"return the prior centre" scored better than every real estimator:

- untrained (uniform-posterior) network → median 3.5 nT (the posterior mean collapses to
  the prior centre = the ground truth);
- all ladder numbers in v1 measured "how far from the setpoint", not estimator precision.

**v1 is void.** All v1 numbers (`results/ladder_eval.json`, `results/pilot_gpos.json`)
are retained in the repository for the audit trail but must not be quoted as results.

## Second defect found by the same gate (also fixed)

`joint_lm` was bounded to `B ∈ [0.75, 1.25]·B_nom` (±268 nT), whereas `lm_free` searched
±3214 nT. The pooled estimator therefore had a ~12× tighter prior than its comparator
and railed on the bound for column 1 (returned exactly 1.25 × 1071.4 in sheets 1 and 2).
Any "gain" from a tighter bound is not an estimator gain. v2 gives every classical method
the identical initialisation and the identical window.

## v2 protocol (frozen 2026-09-12, `src/blind_eval.py`)

1. **Task**: estimate an UNKNOWN field from one full 300-point real trace. The estimator
   receives B ∈ [500, 45000] nT (instrument range) and the calibrated conventions
   (τ_off = 18.6 ns; envelope population from high-rep fits) — never the setpoint.
2. **Shared initialisation**: every classical method starts from the same blind
   FFT+Rife estimate of the same trace (standard practice; the comparison isolates the
   refinement step).
3. **Metric**: `|B_hat − B_true|`, `B_true = 1071.4·n` nT (the applied field). The ~51 nT
   setpoint systematic is 2 orders of magnitude below low-budget errors; it is reported
   as a caveat and defines the high-budget floor.
4. **Non-degeneracy check** (required before any claim): a constant estimator must be
   catastrophically bad. Under v2 the best constant is the range centre → ~20 000 nT
   median error. Verified.
5. **Estimators**: FFT+Rife (blind), per-trace LM refinement, session-pooled LM
   (shared envelope + phase frame), amortized neural posterior (per-trace and
   set-conditioned), all on identical data.

## Consequence for the science

Under v2 the pooled-vs-per-trace comparison survives and sharpens, and a *new* structure
appears that v1 could not see: the pooled estimator has a **bias floor** set by the
real spread of the relaxation envelope across the field range (T2* = 5.40 ± 0.29 µs,
p = 2.01 ± 0.42), so pooling wins at low photon budget and loses at high photon budget.
The synthetic control with exact ground truth (`results/control_pooling_bias.json`)
reproduces this crossover:

| reps | per-trace LM | pooled (shared T2*) | pooled (free T2*) |
|---|---|---|---|
| 5 000 | 520.7 | **374.5** | 414.4 |
| 10 000 | 415.8 | **270.0** | 280.8 |
| 40 000 | **248.8** | 257.7 | 271.2 |
| 160 000 | **91.3** | 235.9 | 235.2 |
| 640 000 | **51.7** | 217.8 | 235.3 |

Crossover at r* ≈ 20–40 k repetitions; the pooled floor ≈ 220 nT is set by envelope
inhomogeneity, not by photons. This is the physical content of the L5 paper: the
sensitivity-optimal estimator is photon-budget-dependent.

## Rule adopted

Any metric of the form |estimate − value that the estimator was told in advance| is
forbidden in this project. Every evaluation must include a non-degeneracy check: a
constant / prior-returning estimator must be demonstrably worse than the real estimators.
