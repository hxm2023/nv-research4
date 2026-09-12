# CANDIDATE_KILL_LOG — L5 (nv-research4)

Direction (LOCKED by user): estimate high-precision B from LOW-SNR (low photon budget)
Ramsey data; metric sensitivity η = δB·√t_total; full 300-point τ sweep fixed; only the
photon-budget axis may vary; positive-result paper, physics journal.

Protocol discipline: every candidate gets a **score**, a **kill-condition check**, a
**decision**, **evidence**, **alternatives**, and a **falsification condition** (a concrete
observation that would kill it). Kill is not waste — killed candidates are recycled as
baselines or ablation rungs.

Date of evaluation: 2026-09-12. Phase: 0→1. Compute spent at log time: 0 GPUh on jindun,
local RTX-5060 smoke only (pilot-scale, <1 GPUh).

---

## W1 — Pooled instrument-nuisance inference at low photon budget (PRIMARY)

**Statement.** At low photon budget the dominant estimator error for Ramsey field
estimation is not shot noise but the *identifiability of B jointly with the instrument's
nuisance structure* (shared relaxation envelope A, C, T2*, p and the calibrated phase
frame φ0, τ_off). Per-trace estimation spends its scarce photons on nuisance parameters;
pooling the shared structure across the sweep's field columns recovers the achievable
bound. A budget-conditioned amortized posterior makes this practical and calibrated.

**Evidence (real data, this repo).**
- Full 8-level ladder, 40 real columns each, median |ΔB| vs nominal (nT):

| r | lm_free | joint (pooled) | CRLB(known env) | η ratio | paired Wilcoxon p |
|---|---|---|---|---|---|
| 5 000 | 569.9 | 307.0 | 415.2 | 1.86 | 1.4e-2 |
| 10 000 | 455.0 | 207.7 | 293.6 | 2.19 | 2.8e-5 |
| 20 000 | 295.1 | 154.4 | 207.6 | 1.91 | 1.9e-3 |
| 40 000 | 234.3 | 85.8 | 146.8 | 2.73 | 1.7e-6 |
| 80 000 | 158.1 | 73.2 | 103.8 | 2.16 | 2.2e-4 |
| 160 000 | 148.8 | 84.5 | 73.4 | 1.76 | 3.2e-4 |
| 320 000 | 78.5 | 49.9 | 51.9 | 1.57 | 4.4e-3 |
| 640 000 | 51.0 | 60.4 | 36.7 | 0.84 | 0.51 (n.s.) |

- Ablation (share envelope only, φ0 free per column): 5k 570→443 (1.29×); 10k 455→405 (1.12×).
- External-prior variant (no within-sheet pooling; population-mean envelope from real
  high-rep fits + calibrated φ0): 5k 570→374 (1.52×), 10k 455→227 (2.00×).
- Physical justification checked: φ0 is a shared instrument property — circular
  concentration |R| = 0.955 (5k), 0.971 (10k), 0.993 (320k), 0.992 (640k); mean φ0
  −0.05…+0.02 rad across all sheets.
- The ablation shows the claim is NOT reducible to phase-frame calibration alone:
  envelope-only pooling contributes a real gain (1.29×/1.12×) on top.

**Anti-overlap check (R7 pre-check).** L1 owns "calibration anchoring" (τ_off/φ0 as its
*discovery*) and explicitly cedes "cols 7+ classically solved" (its CLAUDE.md). W1 is
about a region L1 declared solved, at photon budgets L1 did not study (its sensitivity
section used a √N proxy, cols 3–6, n=4/level). W1 injects no external field knowledge
(anchoring does); it *pools* a shared nuisance. The phase-frame part is attributed to
L1's calibration convention (cited), and the paper reports the envelope-only ablation
separately. L3/L4 own sparse τ design/aliasing: W1 keeps the full 300-point sweep and
varies only the photon budget. Verdict: distinct, provided the framing stays on
estimator-limited sensitivity at low photon budget.

**Kill condition.** (a) A classical hierarchical-Bayes baseline with the same information
reaches the same δB as the amortized estimator ⇒ the ML claim dies (idea survives as a
statistics result but AI-novelty collapses). (b) The effect disappears on held-out
columns/fields. (c) Scoop: any paper doing full-sweep low-photon η benchmarking on real
data with pooling (none found, see SCOOP_CHECK).

**Decision: PURSUE (primary).**

**Falsification.** If, after matched information and matched tuning budget, the pooled
estimator's advantage over per-trace classical fitting is < 1.2× at 5k–20k on real data,
the claim is not paper-worthy and L5 pivots (see W4).

**Alternatives.** If the neural estimator underperforms joint LM on real data, keep the
pooled result classical and re-scope the ML contribution to calibration/UQ or W3.

---

## W2 — Amortized instrument-anchored posterior (sim-to-real via real-data-derived training)  [derived from initial advice]

**Statement.** A budget-conditioned amortized posterior q(B | trace) trained on
*instrument-anchored* data achieves the pooled bound at O(1) inference cost and provides
calibrated uncertainty, closing the sim-to-real gap that the 2026 literature flags as the
blocker for learned NV estimators.

**Evidence (pending).** Smoke training (local, 4k steps): loss 5.486 (uniform) → 4.02,
synthetic validation median error 1.6 µT → [in progress]. Full seed-0 run at 12k steps
in flight at log time.

**Kill condition.** Trained posterior fails to reach joint-LM performance on real
sheets 1–2 (within ~10%): then W2 is demoted to a supporting implementation detail.

**Decision: PURSUE (primary, as the ML vehicle of W1).**

**Falsification.** If the neural posterior is systematically beaten by classical joint LM
on real data across ≥5 seeds, the AI contribution is not the estimator but the analysis;
report honestly and pivot the AI claim to W3/W4.

---

## W3 — Sensitivity-oriented training objective (bias/η-optimal ≠ MSE-optimal)  [fresh]

**Statement.** At low photon budget the sensitivity-optimal estimator is *biased*
(shrinkage toward the prior), because δB is a variance-dominated functional, so training
for MSE is not training for η. A loss that directly targets the budget-conditioned
sensitivity yields strictly better η than an MSE-trained network of identical capacity.

**Evidence.** To be measured in Phase 2 (cheap): two identical networks trained with
MSE vs posterior-NLL/sensitivity loss, compared on real sheets 1–2. Downstream of W2.

**Kill condition.** If η(MSE-trained) ≈ η(NLL-trained) within CI at all budgets, the
claim is void.

**Decision: PURSUE as a secondary claim (cheap to test, no extra data needed).**

**Falsification.** Any budget where the sensitivity-trained net is worse by more than the
paired CI would refute the "η-optimal is systematically different" framing.

---

## W4 — Identifiability atlas over the (field, photon-budget) plane  [fresh]

**Statement.** Map where field estimation is *bound-limited* vs *nuisance-limited* across
the 40 real field columns × 8 repetition levels, using the gap between achieved error and
the known-envelope CRLB. Prediction: the nuisance-limited region is a coherent block
(low r, all fields), and its boundary is the operational answer to "when does structured
inference matter?".

**Evidence.** The ladder table above already shows the structure (gain 1.6–2.7× for
r ≤ 320k, collapse at 640k where the ≈50 nT instrument systematic floor dominates).

**Kill condition.** If the atlas shows no coherent regime boundary (gain randomly
scattered across columns/reps), there is no framing device and W1 loses its figure.

**Decision: PURSUE as the framing/analysis layer (it is the pivot target if W2 fails).**

**Falsification.** A shuffled-columns control reproducing the same "structure" would show
the atlas is an artifact.

---

## W5 — Tail-robustness framing (failure-rate-limited sensitivity)  [fresh]

**Statement.** Practical low-budget sensitivity is set by the failure tail, not the
median: classical per-trace fitting produces catastrophic decodes at a rate that makes
the *usable* δB much worse than its median. The pooled/amortized estimator removes the
tail.

**Evidence.** frac(|ΔB| < 500 nT) at 5k: lm_free 42%(nom) vs joint 68%; at 10k 55% vs 85%.
Heavy-tail structure visible in per-column error lists (results/pilot_gpos.json).

**Kill condition.** If, at matched median error, tail fractions are statistically
indistinguishable, the tail claim is decoration, not content.

**Decision: PURSUE as a supporting claim (feeds the η definition with a risk-aware
variant: δB at the 90th percentile).**

**Falsification.** A tail-matched comparison (subsample classical errors to matched
median) erasing the difference.

---

## W6 — Photon-budget transfer: train on real high-rep sheets, evaluate at low reps  [fresh]

**Statement.** Instead of pure simulation, training data can be built from *real*
high-repetition sheets with synthetic noise added to the target budget; this removes the
sim-to-real signal-model gap, leaving only the (measured) noise-model assumption.

**Evidence.** To be tested in Phase 2 by comparing W2 trained with vs without real-derived
training traces; leakage controlled by the frozen column split (holdout columns never
contribute training traces).

**Kill condition.** If real-derived training gives no measurable advantage over
anchored-synthetic training, drop it (simpler paper).

**Decision: PURSUE as an ablation of W2 (data-efficiency claim, not a headline).**

**Falsification.** A leakage audit showing the gain comes from the model recognizing
training columns (test: holdout-column performance must show the same gain).

---

## KILLED

**K1 — Sparse / adaptive τ allocation at low photon budget.**
Killed: duplicates L3 (archived) and L4 (submitted design-boundary line); forbidden by the
L5 constitution ("L5 固定全 τ 扫描，只调光子预算维度"). Also the central mechanism of the
scoop alarms 2602.00679 / 2506.13469 / 2512.11300.

**K2 — Re-selling τ_off / φ0 calibration anchoring as the main effect.**
Killed: that is L1's discovery (its `confirm_tau_off`, slope 0.0031308 ± 0.0003699,
t = 8.46). L5 may cite it as a known convention only. Recycled as: known-convention input
to W1/W2, and as the envelope-only ablation that separates W1's contribution from L1's.

**K3 — Speed/throughput as the headline ("amortized inference is 100× faster").**
Killed: explicitly forbidden as a headline by CLAUDE.md (速度当头条). Recycled as
supporting evidence in W2's deployment discussion only.

**K4 — Uncertainty calibration (conformal) as the headline.**
Killed: L1 owns calibrated UQ (conformal 88.8% (142/160) coverage). L5 only *uses*
uncertainty for the η definition and reports coverage as a diagnostic.

---

## Scoring (6-dim, gate ≥26/30 with AI-novelty ≥4) — to be finalized in PHASE1_DECISION

Preliminary (evidence-based, not aspirational):
W1: novelty 5 (cell verified empty by scoop check), AI-novelty 4 (amortized estimator is
the vehicle; the *finding* is physics/statistical), feasibility 5 (already measured),
rigor-tractability 5, impact 4, story 5 → 28/30.
Full table with justifications after the adversarial round.


---

# ADDENDUM (2026-09-12, after the adversarial gate) — evidence rebuilt under protocol v2

The adversarial gate (`review-stage/ADVERSARIAL_R1-R7.md`, verdict KILLED) invalidated
protocol v1 (see `PROTOCOL_CORRECTION_v1_to_v2.md`). All W1 evidence was re-measured under
the blind v2 protocol on the same real data. The responses are in
`review-stage/ADVERSARIAL_RESPONSE.md`. Summary of what changed:

## W1 — revived in a different, budget-dependent form

Under v2 (blind task, unknown field, shared FFT+Rife init, RMSE as the primary statistic,
each estimator compared to its OWN CRLB), region cols 7–40:

| r | per-trace RMSE (nT) | pooled RMSE | ratio | pooled bias | per-trace eff. | pooled eff. |
|---|---|---|---|---|---|---|
| 5 000 | 742.9 | **439.1** | 1.69 | 8.0 | 1.01 | 1.05 |
| 10 000 | 629.2 | **344.1** | 1.83 | 145.7 | 1.21 | 1.16 |
| 20 000 | 382.7 | **272.0** | 1.41 | 82.6 | 1.04 | 1.30 |
| 40 000 | 261.6 | **175.6** | 1.49 | 97.9 | 1.00 | 1.18 |
| 80 000 | **194.6** | 214.8 | 0.91 | 185.5 | 1.06 | 2.05 |
| 160 000 | **165.0** | 174.9 | 0.94 | 144.3 | 1.27 | 2.36 |
| 320 000 | **109.4** | 173.8 | 0.63 | 151.2 | 1.19 | 3.31 |
| 640 000 | **59.4** | 145.8 | 0.41 | 125.3 | 0.91 | 3.93 |

*"eff." = RMSE / that estimator's own CRLB (free-envelope for the 6-parameter per-trace fit,
shared-envelope joint CRLB for the pooled fit).*

**The claim is now**: both estimators are efficient against their own bounds; pooling moves
the bound (free → shared envelope CRLB ratio ≈1.8) but carries a **bias floor** from real
envelope inhomogeneity, so the sensitivity-optimal estimator is **photon-budget-dependent**.

Fitted law in cols 7–40 (`results/analysis_v2.json`):

    deltaB(r) = sqrt( A^2 * (5000/r) + b^2 )
    per-trace : A = 785.3 nT,  b =  27.8 nT  (fit rms 32.6)
    pooled    : A = 416.8 nT,  b = 156.2 nT  (fit rms 18.9)
    crossover : r* = 9.1e4 repetitions

Independent confirmation with exact ground truth (synthetic control,
`results/control_pooling_bias.json`): per-trace 51.7 nT vs pooled 217.8 nT at 640k; pooled
46.8 nT vs per-trace 520.7 nT at 5k. Same crossover.

**R7 status**: refuted in its stated form. The v1 pattern ("gain tracks fringe order, absent
in cols 7–40 at high budget") was an artefact of the void metric. Under v2 the gain in
cols 7–40 is monotone in photon budget (1.69 → 0.41) and the sub-cycle region shows no budget
dependence — the opposite of what v1 showed. The phase-frame pooling term remains L1's and is
cited as a convention only.

## What is now carried as baselines (per R2)

per-trace LM (blind, FFT-init) · session-pooled LM · external-prior empirical Bayes (to be
implemented with provenance) · FFT+Rife · amortized per-trace network · amortized
set-conditioned network. The **proposed method is the amortized estimator**; pooled LM is a
baseline, not the proposal.

## Falsification conditions (updated)

- If the amortized estimator cannot match the best classical estimator at each budget
  (oracle-best = min(per-trace, pooled) per budget) within CI, the AI contribution is demoted
  to a supporting role and the paper is a metrology/statistics paper.
- If the crossover law fails out-of-sample (held-out columns or the synthetic control), the
  paper's central quantitative claim is withdrawn.
