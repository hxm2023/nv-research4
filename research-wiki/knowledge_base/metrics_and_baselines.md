# Metrics and Baselines — NV-Center Ramsey Magnetometry Estimation

Knowledge-base note for NV×AI Line #5 (sensitivity-optimal low-SNR Ramsey estimation).
Compiled 2026-09-12 from web/literature search; every citation below was seen in search
results. Values marked **approx** are approximate or derived, not quoted verbatim.

> **Project protocol (fixed, for orientation).** One estimate is produced from a **fixed
> full 300-point τ sweeps** at repetition level *r*, so
> `t_total ≈ r · Σ_i (τ_i + t_ovh)`, with `t_ovh` the per-point readout/pulse overhead
> (must be declared; sensitivity analysis over 0.5×/1×/2×). Metric:
> **η = δB · √t_total**. Operational low-photon-budget comparator: **reps-to-target
> precision δB\*** (how many repetitions to reach δB\*). All comparisons use the **same
> data, same τ grid, same evaluation protocol**; classical baselines get full tuning budget.

---

## Standard Evaluation Metrics

### 1. Point accuracy of the field estimate — δB

| Metric | Definition | When to use | Notes |
|---|---|---|---|
| `std(δB)` | Standard deviation of B̂ over posterior or over seeds | Headline when errors are Gaussian / unimodal | Used e.g. as per-axis σ_B in Rieckmann et al. 2026 (arXiv:2606.02749) |
| `RMSE` | √(mean (B̂ − B_true)²) | Penalizes bias + variance jointly | Common in NN papers; conflates the two |
| `MAE` / **median abs. error** | median \|B̂ − B_true\| | Robust to heavy tails; **preferred at low SNR** | Low-SNR estimators fail in bursts; median ≠ mean |
| `bias` | mean(B̂) − B_true | Must be reported separately from variance | Rieckmann et al. 2026 explicitly characterize their NN as a **biased estimator** (residual ΔB even for noiseless inputs) and show the bias can be pushed below the noise level |
| `relative fitting error` | \|p̂−p\|/p per parameter | ODMR/NV spectral fitting | Yao et al. 2026 (arXiv:2603.14728) report relative fitting error vs SNR |

**Discipline:** report `median + IQR` *and* `mean ± std`. A learned estimator that wins on
median but has a 5 % catastrophic-failure tail is not a win at low photon budget.

### 2. Uncertainty quality — posterior std and interval coverage

- **Posterior std** δB_post: the Bayesian analogue of std; the quantity that enters η.
- **Coverage of credible intervals**: fraction of trials where the true B lies inside the
  nominal (e.g. 68 % / 95 %) credible interval. Below-nominal coverage = **overconfident**
  posterior, which silently corrupts any η claim. Hincks et al. (arXiv:1705.10897,
  *New J. Phys.* **20**, 013022, 2018) supply the NV-specific Bayes estimator + error
  propagation and compare it to weighted least squares.
- Diagnostic machinery (from the general SBI literature, directly reusable here):
  - **SBC** — Simulation-Based Calibration (Talts et al., arXiv:1804.06788): marginal
    rank-uniformity test, finds *which* parameter is miscalibrated.
  - **Expected Coverage** (Deistler et al., arXiv:2210.04815): average joint-posterior
    narrowness/broadness; catches wrong correlations.
  - **TARP** (Tests of Accuracy with Random Points; Lemos, Coogan et al. 2023) — global
    diagnostic that works with sampling-only posteriors.
  - Tooling: the `sbi` Python package implements `run_sbc`, `run_tarp`
    (https://sbi.readthedocs.io/en/stable/api_reference/_autosummary/sbi.diagnostics.run_tarp.html).
  - Physics-journal precedent for coverage reporting: Phys. Rev. C **103**, 065501 (2021)
    defines a Bayesian "model coverage" C from pseudoexperiments with uncertainty
    √(C(1−C)/N_trial), and stresses that empirical coverage ≠ nominal credibility in general.

### 3. Sensitivity — η = δB · √t_total

- Unit: nT/√Hz (equivalently T/√Hz, fT/√Hz, pT/√Hz). It is the **minimum detectable field
  per root averaging time**, not a per-shot number.
- Equivalent definitions seen in the literature:
  - `δB_min = η/√t` (arXiv:2604.20901).
  - `η = σ_B √T_m = σ_B/√(2Δf)` (arXiv:2009.02371, DQ 4-Ramsey).
  - Slope-based (device papers): `η(f) = noise_PSD(f) / slope[B/nT]`, take the median over
    the spectrum (protocol described in arXiv:2305.06269, "Sensitive AC and DC Magnetometry
    with NV Center Ensembles").
- **T₂\*-limited Ramsey reference formula** (search-derived; matches the form in several
  sources incl. arXiv:2604.20901 and the AI-Terakoya NV chapter):

  ```
  η_Ramsey(τ) = √(τ + t_d) · exp[(τ/T₂*)^p] / (2π γ C₀ τ)
  ```

  where `t_d` = dead time (init + readout), `p` = decay exponent (1 exponential, 2 Gaussian),
  `C₀` contrast. Optimizing gives **τ_opt ≈ T₂\*/2** for negligible dead time (both p = 1 and
  p = 2), and `η_min ∝ 1/√T₂*`. With T₂* = 1 µs, τ_opt shifts from 0.50 T₂* (t_d = 0) to
  0.657 T₂* (t_d = 0.3 µs) and 0.886 T₂* (t_d = 3 µs), with η_min degrading roughly
  13.2 → 16.3 → 30.7 **nT/√Hz approx** (single-NV numbers from the search summary of the
  Jülich/PRApplied-class treatment).
- **Readout penalty σ_R**: `σ_R = √(1 + 2(α₀+α₁)/(α₀−α₁)²) ≥ 1` where α₀, α₁ are mean
  photons per shot for the two spin states. σ_R = 1 only in the projective limit. For a
  single NV with α₀ ≈ 0.03, α₁ ≈ 0.02 → **σ_R ≈ 31.6 approx**, i.e. >10× worse η than the
  spin-projection limit. This is the factor that most often separates a quoted sensitivity
  from the spin-projection bound (Barry et al., *Rev. Mod. Phys.* **92**, 015004 (2020),
  arXiv:1903.08176, uses the same σ_R notation).

### 4. Reps-to-target-precision δB\* (the L5 headline comparator)

- Definition: smallest number of repetitions `r*` such that the achieved δB(r*) ≤ δB\*.
- Two curves are drawn: **η(r)** and **reps-to-δB\***, on the 8-level repetition ladder
  (5k → 640k), same τ grid, same estimator protocol.
- Positive result = strictly fewer repetitions (less `t_total`) to hit the same δB\*.
- **Must be paired**: same data realization / same seed set for both arms; report the
  paired difference distribution, not two independent CIs.

### 5. CRLB — the reference floor (see dedicated section below)

Report `CRLB(f)` / `CRLB(B)` alongside every achieved δB. Also report the **efficiency**
`CRLB_std / achieved_std` (dimensionless) so that comparisons survive unit-system mistakes.

### 6. Failure rate / large-error fraction

- `failure rate = fraction( |B̂ − B_true| > k·δB* )`, with k declared (e.g. 3 or 5).
- At low SNR the dominant failure modes are (a) LM convergence to a local minimum,
  (b) FFT peak-picking the wrong spectral line / wrong Nyquist branch, (c) **phase wrapping**
  in Hilbert-style phase extraction, (d) NN out-of-distribution collapse.
- **Never report a mean error without the failure fraction.** The classical literature
  convention is to plot error vs SNR with the estimator variance *and* the CRLB on the same
  axes so the threshold region is visible (see the Rife-family simulations,
  Aboutanios & Mulgrew 2005).

### How the field reports these (observed patterns)

| Community | Default metric reported | Citation exemplars |
|---|---|---|
| NV device / magnetometry | η in nT/√Hz or pT/√Hz, plus Allan deviation minimum detectable field | Wolf et al. PRX **5**, 041001 (2015) + Erratum PRX **13**, 029903 (2023); Adv. Quantum Technol. 202300456; arXiv:2309.04093; arXiv:2305.06269 |
| NV quantum-metrology theory | Fisher information, CRB / quantum CRB, η ∝ 1/√T₂* | SciPost Phys. **17**, 004; npj Quantum Inf. **8** (2022) 10.1038/s41534-022-00547-x |
| NV + ML | RMSE / per-axis σ_B / R², ± uncertainty in K or nT | arXiv:2606.02749; arXiv:2409.09487; arXiv:2603.14728 |
| NV + adaptive/Bayesian | Bayesian CRB (van Trees), posterior std, sensing-time budget | arXiv:2312.16985; arXiv:2510.11884; arXiv:2506.13469 |

---

## SOTA Baselines

Baselines that must receive **full tuning budget** in every L5 comparison.

| Method | Citation (real, year) | Key performance | Code availability |
|---|---|---|---|
| Levenberg–Marquardt multi-start NLS on Ramsey fringe | Standard practice; the fit model `C + A e^{−(τ/T₂)^p} cos(2πfτ+φ)` is the field convention (Barry et al., RMP **92**, 015004, 2020) | Near-CRLB when initialized well and SNR is adequate; degrades at low SNR where local minima appear | ubiquitous (SciPy `curve_fit`, MATLAB `fit`) |
| FFT peak + **Rife** double-spectral-line interpolation | Rife & Vincent, *Bell Syst. Tech. J.* **49**(2), 197–228 (1970), DOI 10.1002/j.1538-7305.1970.tb01766.x | Near-CRB in the *mid-bin* region; **degrades near DFT bins and at low SNR** (interpolation direction misjudged) | reference implementations in most DSP toolboxes |
| Iterative DFT-interpolation (Aboutanios–Mulgrew) | Aboutanios & Mulgrew, *IEEE Trans. Signal Process.* **53**(4), 1237–1242 (2005), DOI 10.1109/TSP.2005.843719 | Asymptotically unbiased, variance **1.0147× the asymptotic CRB**, uniformly over the frequency range | widely re-implemented |
| Grid / particle-filter **Bayes** on the full model | Hincks et al., arXiv:1705.10897, *New J. Phys.* **20**, 013022 (2018) | MLE risk well-approximated by a simple CRB formula; Bayes estimator slightly better risk + clean error propagation; demonstrated on real NV data vs weighted least squares | analysis code released with the paper (Jupyter/AFQ) |
| Particle-filter Bayes + optimal adaptive τ | Belliardo, Zoratti, Marquardt, Giovannetti, arXiv:2312.16985; *Quantum* **8**, 1555 (2024), DOI 10.22331/q-2024-12-10-1555 | Beats previous experimental-design SOTA; reports sensor precision and/or CRB via Fisher information; handles non-differentiable estimators | **public Python package `qsensoropt`** (with NV-center applications) |
| EKF / cubature Kalman tracking with Bayesian CRB | Dilcher, Bania, Mendez-Avalos, Sierant, Mitchell, Kołodynski, arXiv:2510.11884 | Derives Bayesian CRB (attained by prediction-error method); EKF/CKF near-optimal and cheap for FID spin-precession tracking | not stated in sources consulted |
| EKF + LQR closed-loop tracking (atomic magnetometer) | arXiv:2503.14793 | Riccati evolved with the estimate; simultaneously estimates state and field | not stated in sources consulted |
| Extended Kalman / adaptive EKF field tracking beyond prior waveform constraints | arXiv:2605.17784 (Wang, Jin, Ming, Miao, Lu, Mitchell, Kong) | Sage–Husa-style adaptive noise covariance; tracks seismo-magnetic-like signals beyond conventional spin-noise sensitivity | not stated in sources consulted |
| Feedforward NN vector-field regression (NV, broadband MW) | Rieckmann, Afshar, Goldberg, Childress, Scheel, Heshami, arXiv:2606.02749 (v1, 1 Jun 2026) | ~5–100 pT/√Hz depending on field component; ~nT accuracy at ~70 dB SNR; contrasted with MLE based on KL minimization (both reach <1 nT/√Hz); NN is **biased**, bias reducible below the noise floor | simulated data only; code availability not stated in sources consulted |
| Bayesian NN (coarse) + federated RL (fine) for wide-range single-electron DC sensing | Guo, Liu, Le, Dai, arXiv:2506.13469 (v1 16 Jun 2025, v2 9 Aug 2025) | Single-shot NV readout under a total sensing-time budget; reported gains in accuracy + resource efficiency with faster convergence (~40 vs ~90 experiments vs the re-implemented baseline) | not stated in sources consulted |
| 1D-CNN for direct ODMR parameter inference | Yao et al., arXiv:2603.14728 (v1, 16 Mar 2026) | Real-time, guess-free, GPU-parallel; beats nonlinear least squares mainly at **low SNR**; demoed on intracellular nanodiamond thermometry and widefield vortex imaging | not stated in sources consulted |
| Probabilistic (auto-diff likelihood) inference for CW-ODMR | Rajpal, Ahmed, Berry, arXiv:2409.09487 (v1 14 Sep 2024, v2 12 Apr 2025) | ±1 K over 243–323 K; beats PCR and 1D-CNN when **extrapolating** outside the training range (CNN/PCR up to **10× worse** outside it) | not stated in sources consulted |
| Quantum-kernel / QML regression under measurement-induced information loss | arXiv:2608.23934 (Bhowmik, Thapliyal) | Frames NV field sensing as supervised regression; theoretical upper bound only achievable with coherent (pre-measurement) state access | *(arXiv ID seen in search index only; not independently verified)* |
| Sequential quantum Hamiltonian learning, NV spin-1 | Yamauchi, Stearn, Tovey, arXiv:2605.23455 | Sequential Bayesian field-map reconstruction; final-frame RMSE ≈ 7.037e-7 T on synthetic maze-like fields; explicit Fisher-information / leakage trade-off diagnostics | not stated in sources consulted |
| Real-time dark-state (CPT) Bayesian estimator | arXiv:2111.09943 | Field update from a **single photon** in an Ornstein–Uhlenbeck field | not stated in sources consulted |

**Search gap:** no paper was found that benchmarks an ML/amortized estimator against
classical baselines **at matched information budget on a fixed full τ sweep under explicit
photon-budget control**. That is precisely the L5 cell; it also means the L5 paper must
supply the protocol itself rather than inherit one.

---

## Classical Methods — when, how well, and where they break

| Method | Use when | Expected performance | Limitations |
|---|---|---|---|
| **LM multi-start NLS** (`C + A e^{−(τ/T₂)^p} cos(2πfτ+φ)`) | Mid/high SNR; single dominant fringe frequency; you need calibrated parameter uncertainties | With enough restarts, achieves ≈ CRLB; χ²/dof acts as a fit-quality gate | Cost scales linearly with #starts (MC fitting, 200 rounds used as a baseline in arXiv:2603.14728); at low SNR it lands in local minima → burst failures; needs initial guesses |
| **FFT peak + Rife** | Very fast coarse/absolute frequency; wide capture range; low SNR where you cannot afford iteration | Near-CRB mid-bin; **bias/error floor near bins and at low SNR** (Rife & Vincent 1970) | Bin-edge misjudgement; no uncertainty quantification; does not fit decay/contrast jointly → biased f when the envelope decays |
| **Aboutanios–Mulgrew / I-Rife / ASIQ-Rife / PAI-Rife iterative interpolation** | Same as Rife but you need close-to-CRLB variance | 1.0147× CRB asymptotically (Aboutanios & Mulgrew 2005); modified Rife variants (I-Rife, ASIQ-Rife, PAI-Rife, CQRE, HAQSE) report variance approaching CRLB at low SNR at ~13–89 % extra cost vs plain Rife | Still a single-tone estimator; needs the fringe to be a clean sinusoid; multiparameter/decay correlation not modelled |
| **Grid Bayes** (discretized posterior over (B, A, C, T₂, φ)) | Low SNR, multimodal posterior, small parameter box, you want a *calibrated* uncertainty | Global (no local minima); exact given grid; cost = grid size × 300 τ points | Grid explosion with dimension; discretization bias; requires prior declaration; poor tail resolution unless grid is refined |
| **MCMC** | Same as grid Bayes but higher dimension / continuous | Asymptotically exact posterior | Burn-in cost per estimate; harder to get <5 seeds × 8 rep levels within budget; rank/coverage diagnostics still required |
| **Particle filter (SMC)** | Sequential / adaptive protocols; real-time posterior updates | Posterior covariance from weighted-particle sample covariance; used with particle-guess heuristics (τ ≈ 1/σ_P) in adaptive Ramsey | Particle depletion; cost grows with #particles; the L5 setting (fixed full sweep, no adaptivity) is *not* its natural niche |
| **Hilbert phase unwrapping** | Dense τ grids; phase-vs-τ slope extraction | Fast, non-iterative; effective at high SNR | **Wraps** whenever \|Δφ\| exceeds π between samples; extremely fragile at low SNR. No dedicated NV citation found in this search round — treat as a DSP technique, and if used, validate failure rate explicitly |
| **Prony / matrix-pencil** | Exponentially damped sinusoid models (NMR/NQR-like data) | Non-iterative; **statistically inefficient** — variance well above the CRB and growing faster than CRB as SNR falls (Steedly & Moses TLS-Prony analysis, *Automatica* **30**(1), 115–129, 1994); pencil > polynomial variants (Hua 1988 dissertation, Syracuse) | High variance / noise sensitivity; needs model order; no natural uncertainty output |
| **ESPRIT / ET-ESP (echo-train ESPRIT)** | Multi-line exponentially damped sinusoids; you need good initialization for a statistically efficient refinement | Frequency estimates **close to the CRB** (CRB derived via Slepian–Bangs), requires only the number of lines K (Gudmundson, Wirfält, Jakobsson, Jansson, IEEE SSP 2012, DOI 10.1109/SSP.2012.6319820) | Subspace methods need a Hankel/Toeplitz structure and enough samples; precision degrades without a clean multi-line assumption; typically a *precursor* to NLS, not a final estimator |
| **Maximum-likelihood fitting (direct MLE)** | You can write the likelihood (Poisson/binomial photon counts) and can afford an optimizer | Hincks et al. (arXiv:1705.10897): MLE risk is well approximated by a **simple CRB formula**; Bayes estimator slightly better | Non-convex in f at low SNR → same multi-start problem; needs the correct noise model (three-Poisson-rate NV readout model from Hincks et al.) |

---

## Learned / Bayesian Estimators

| Family | Citation | What it does | Reported result |
|---|---|---|---|
| Amortized NN regression (feedforward) | Rieckmann et al., arXiv:2606.02749 (2026) | Maps time-domain transmission → (B_x, B_y, B_z, \|B\|) | 5–100 pT/√Hz per component (simulated); ~nT at 70 dB SNR; NN found **biased**, bias reduceable below noise |
| Bayesian NN + federated RL | Guo et al., arXiv:2506.13469 (2025) | BNN narrows the field range, RL fine-tunes (τ, φ) | Faster convergence + better accuracy/resource efficiency under a total time budget; explicit **fair-comparison** re-implementation of the Bonato et al. baseline inside the same RL framework/loss/particle count |
| 1D-CNN direct inference | Yao et al., arXiv:2603.14728 (2026) | ODMR spectra → resonance parameters, no initial guess | Largest gains vs NLS **at low SNR**; real experimental validation |
| Probabilistic auto-diff likelihood model | Rajpal et al., arXiv:2409.09487 (2024/25) | CW-ODMR → temperature with principled uncertainty | ±1 K; **generalizes out of training range**, CNN/PCR up to 10× worse there |
| Model-aware RL for Bayesian experimental design | Belliardo et al., arXiv:2312.16985, *Quantum* **8**, 1555 (2024) | Adaptive/non-adaptive τ design with particle-filter posteriors | Surpasses prior experimental-design SOTA; CRB/Fisher comparison |
| Quantum Hamiltonian Learning (Bayesian, NV spin-1) | Yamauchi et al., arXiv:2605.23455 | Sequential spatiotemporal field reconstruction | RMSE ≈ 7.0e-7 T final frame (synthetic); Fisher-information/leakage diagnostics |
| Quantum kernel methods | arXiv:2608.23934 | Supervised regression; bounds the cost of measurement-induced information loss | Theoretical bound; *(ID from search index, unverified)* |
| **SBI toolbox** (NPE / NLE / NRE, normalizing flows) — general, not NV-specific | Cranmer, Brehmer, Louppe, "The frontier of simulation-based inference", arXiv:1911.01429; *PNAS* **117**, 30055–30062 (2020) | Amortized posterior/likelihood/ratio estimation when the likelihood is intractable but the simulator is available | The methodological template for "train on synthetic, evaluate on real" NV pipelines; carries the coverage caveat below |
| Coverage calibration for the above | Talts et al. arXiv:1804.06788 (SBC); Deistler et al. arXiv:2210.04815 (expected coverage); Lemos et al. 2023 (TARP); Falkiewicz et al., NeurIPS 2023 (differentiable coverage objective) | Diagnose / fix overconfident amortized posteriors | Necessary but not sufficient; passing global diagnostics does not prove the posterior is right |

**Hard rule for L5:** any amortized estimator must report (i) coverage on real held-out data,
(ii) failure fraction, (iii) results at ≥5 seeds, (iv) a paired comparison against the
classical baselines at matched `t_total`.

---

## Evaluation Protocols in the Field

1. **Same data, same τ grid, same protocol.** Losers must not get a worse grid. The L5
   protocol fixes a 300-point full sweep at each repetition level.
2. **Matched information budget / matched total measurement time.** Belliardo et al. and the
   Guo et al. comparison are the models to imitate: Guo et al. re-implemented a competing
   adaptive baseline *inside the same RL framework*, with the same loss, the same particle
   count, and a fixed number of training iterations (16,384), explicitly "to make a fair
   comparison". Copy this discipline.
3. **Seeded runs.** Learned methods: ≥5 seeds, report mean ± std across seeds; also report
   best-seed and worst-seed so the reader can see variance. Classical deterministic methods
   (LM) are stochastic through init → also seed them.
4. **Paired statistics.** Paired Wilcoxon signed-rank on per-sample errors + bootstrap CI for
   the effect size. Report n; pre-register the target δB\*.
5. **Holdout splits by column/field, not at random.** The audited split must be frozen with
   no leakage between train and eval. The NV-specific warning sign is interpolation-in-B
   being reported as generalization: Rajpal et al. (arXiv:2409.09487) show PCR/CNN uncertainty
   is up to **10× worse** outside the training temperature range. Air-gap your field range.
6. **Real data in the headline.** Synthetic data may train/augment, but the headline
   evaluation must be on real `data_lab` acquisitions. Precedent for the trap: the Wolf et al.
   PRX **5**, 041001 (2015) sensitivity claim required an **Erratum** (PRX **13**, 029903,
   2023) that corrected 0.9 pT/√Hz → **9 pT/√Hz** and 100 fT → ~900 fT for 100 s, i.e. a
   10× error in a headline number that stood for 8 years.
7. **Report n everywhere** — photons per point, samples per level, repetitions, seeds.
8. **Declare t_ovh.** Any η comparison is meaningless unless the dead time per point is
   stated, since η(τ) ∝ √(τ + t_d) e^{(τ/T₂*)^p}/(2πγC τ).
9. **Failure/large-error fraction reported next to every accuracy number.**
10. **CRLB reported as a floor, not as an achievement.** Include the estimator efficiency.

---

## CRLB Notes for This Model

### Model

```
s(τ_i) = C + A · exp(−(τ_i / T₂)^p) · cos(2π f τ_i + φ),      i = 1 … N   (N = 300)
```

with independent per-point noise of variance σ_i² (photon shot noise). Field enters through
the fringe frequency `f = γ_e B_∥ / 2π` (B_∥ = projection on the NV axis). In the project's
convention `γ = 2π × 28e-6 rad/(µs·nT)` ⇒ `f [Hz] = 28.025 · B [nT]` per axis, so
`δB = δf / 28.025 Hz/nT ≈ 0.0357 · δf [Hz] nT`.

### Fisher information matrix

For θ = (C, A, T₂, f, φ) with `E_i ≡ exp(−(τ_i/T₂)^p)`, `ψ_i ≡ 2π f τ_i + φ`:

```
J_jk = Σ_i (1/σ_i²) (∂s_i/∂θ_j)(∂s_i/∂θ_k)

∂s/∂C = 1
∂s/∂A = E_i cos(ψ_i)
∂s/∂φ = −A E_i sin(ψ_i)
∂s/∂f = −2π τ_i A E_i sin(ψ_i)
∂s/∂T₂ = A E_i cos(ψ_i) · p τ_i^p / T₂^{p+1}
```

Then

```
CRLB(f̂) = [J⁻¹]_{ff}          (full 5×5 inversion; includes nuisance-parameter penalization)
```

**Two important caveats:**

1. **Do not use `1/J_ff`.** That is the bound *only if A, C, T₂, φ were known*. With five free
   parameters the frequency variance is strictly larger; the inflation is worst exactly at low
   SNR / short T₂ where A and T₂ trade off against f. Report the **full-inversion** number:
   `CRLB(δB) = √([J⁻¹]_ff) / (γ_e/2π)`.
2. **Fisher information adds over repetitions:** `I_total = r · I_single` for r independent
   repetitions, so `CRLB ∝ 1/√r`. This is what makes the reps-to-δB\* curve a straight line on
   a log-log plot until failure/fatigue effects kick in.

### Known simple special cases

- **Single-parameter frequency, known envelope, square-ish grid:** the standard
  `var(f̂) ≥ σ² / [ (2π)² A² Σ_i τ_i² E_i² sin²ψ_i ]`. This is the form behind the well-known
  `η ∝ 1/(γ C √(N_phot)) · √(τ + t_d) e^{(τ/T₂*)^p}/τ` sensitivity scaffolding.
- **Phase-accumulation limit:** for Ramsey, the optimum free-evolution time satisfies
  `τ^p = T₂*^p/(2p)` ⇒ `τ_opt = T₂*/2` (p = 1, 2) with no dead time, and the minimum
  sensitivity scales as `η_min ∝ 1/√T₂*`. Coherence buys only a square root.
- **Bayesian CRB / van Trees** must be used when the bound depends on the true field B:

  ```
  E[L] ≥ 1 / ( J_π + E_B[ I(B) ] )
  ```

  (Van Trees inequality; the phase-estimation literature — e.g. SciPost Phys. **17**, 004 —
  shows the dephasing-limited CRB is explicitly B-dependent and requires either a fixed-B
  assumption or the Bayesian form.)

### What the literature says about approaching the CRB at low SNR

- **MLE is CRB-tight modulo a simple formula.** Hincks et al. (arXiv:1705.10897,
  NJP **20**, 013022, 2018) numerically show the MLE risk is well approximated by a simple
  CRB expression for the NV three-Poisson-rate readout model, and that the Bayes estimator
  has slightly better risk.
- **Iterative DFT interpolation is 1.0147× the asymptotic CRB** uniformly in frequency
  (Aboutanios & Mulgrew 2005) — the cheapest known way to sit essentially *on* the bound.
- **Rife-style single-shot interpolation is CRB-tight only mid-bin**; the whole
  I-Rife / ASIQ-Rife / PAI-Rife / CQRE / HAQSE family exists to remove the low-SNR and
  bin-edge error floors.
- **Subspace (ESPRIT) methods are near-efficient** on damped-sinusoid problems and are
  recommended as *initializers* for statistically efficient gradient/search methods
  (Gudmundson et al., IEEE SSP 2012).
- **Prony is inefficient** (variance much above CRB, diverging faster as SNR falls).
- **Quantum CRB has been experimentally verified on an NV Ramsey interferometer**: the phase
  estimator saturated the quantum CRB (npj Quantum Information, 2022,
  DOI 10.1038/s41534-022-00547-x). Noise there scales as `Δp = Δ₀/√N + ξ₀`: shot noise plus a
  **non-averaging measurement fluctuation ξ₀ that sets a floor** — the practical reason a real
  experiment stops improving as 1/√N.
- **Readout quality, not the estimator, is often the binding constraint.** The σ_R ≥ 1 factor
  (Barry et al. RMP 2020) leaves conventional optical readout more than an order of magnitude
  above the spin-projection CRB.

### Practical recipe for L5

1. Compute `J` on the actual 300-point τ grid, with the **actual** σ_i (shot-noise law
   σ(r) = 0.207√(5000/r) for this dataset; state it, and check its empirical validity per level).
2. Propagate to field: `CRLB(B) = √([J⁻¹]_ff)/28.025` nT.
3. Plot `achieved δB / CRLB(B)` vs repetition level — this single curve is the honest measure
   of "how close to optimal" every contender is, and it is invariant to unit-system mistakes.
4. Distinguish clearly: beating the *classical baseline's achieved error* is the claim;
   beating the CRLB is impossible and must not be hinted at.
