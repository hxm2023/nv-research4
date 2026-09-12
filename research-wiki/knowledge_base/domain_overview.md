# Domain Overview: NV-center Ramsey magnetometry at low photon budget

Scope of this document: estimating a **DC magnetic field B** from **Ramsey interferometry data
with a fixed, full τ-sweep**, under a **low photon budget** (few experimental repetitions), with the
figure of merit being **sensitivity η = δB·√t_total**. Compiled 2026-09-12 from web/arXiv search hits;
every listed reference was seen on a live listing page (arXiv/journal/index).

## What is this field?

A negatively charged nitrogen-vacancy (NV) center in diamond is an atomic-scale electron spin (S=1)
whose ground-state spin sublevels shift linearly with magnetic field via the Zeeman effect,
Δω = γ_e·B_∥ with γ_e = 2π × 28.0 GHz/T (i.e. 2π × 28.0 MHz/mT; equivalently 28.0 Hz/nT... in the
Lab's own unit convention 2π × 28e-6 rad/(µs·nT)). Because the spin can be optically initialized and
read out, and because its coherence time can reach microseconds (T₂*) to milliseconds (T₂) at room
temperature, the NV is the leading solid-state quantum magnetometer for nanoscale and microscale
field sensing.

**Ramsey interferometry** is the workhorse DC protocol. A π/2 microwave pulse rotates the spin into
a superposition; the spin accumulates a field-dependent phase φ = γ_e·B·τ during a free precession
time τ; a second π/2 pulse converts phase into a population difference; the population is read out
by spin-dependent photoluminescence. Repeating over a grid of τ values yields a **Ramsey fringe**
S(τ) = A + B·cos(γ_e B τ + φ₀)·exp(−(τ/T₂*)^p) — a damped sinusoid whose frequency is the quantity of
interest. Fitting the fringe gives B (equivalently the Larmor frequency ω = γ_e B).

**Low photon budget** arises because readout is inefficient. Room-temperature NV readout has no
spin-selective optical transition: photon counts differ by only ~20–40% between m_s = 0 and m_s = ±1
(contrast C), and only a small fraction of emitted photons is collected (collection efficiency of a
few percent for a single NV in a confocal setup; better with solid immersion lenses or waveguides for
ensembles). Consequently each τ point is typically measured with N_rep = 10³–10⁶ laser+microwave
repetitions to build up photon statistics. The photon budget per point is therefore the dominant
experimental cost, and it sets the measurement time t_total, which enters the sensitivity directly.

The field is intrinsically interdisciplinary: spin physics and quantum metrology (what is the best
estimator? what is the CRLB?), instrumentation (diamond growth, microwave control, photonics), and
signal processing / machine learning (how do you extract B from a noisy damped sinusoid?). This last
intersection is where the ML-for-NV literature sits, and it is the intersection this project targets.

## Key Concepts

**NV center.** Point defect (substitutional N + adjacent vacancy) in diamond; the negatively charged
state (NV⁻) is the useful one. Spin-triplet ground state ³A₂ with zero-field splitting D ≈ 2.87 GHz
between m_s = 0 and m_s = ±1, and a magnetically sensitive 2.87 GHz ODMR/Ramsey resonance. Ensembles
of NVs (10¹¹–10¹⁷ cm⁻³) give larger signals and better sensitivity but introduce inhomogeneous
broadening and misalignment of the four crystallographic NV axes.

**Ramsey sequence.** π/2 – τ – π/2 – readout. Pulsed, unlike CW-ODMR which sweeps microwave
frequency. Ramsey gives the longest effective coherence (no continuous drive), so it is the protocol
of choice for DC fields and the one whose sensitivity is limited by T₂* rather than by drive
inhomogeneity. Ramsey fringes are the canonical "damped sinusoid in noise" estimation problem, with
a phase offset φ₀, an amplitude/contrast C, a decay time T₂*, and a possibly non-exponential stretch
factor p (typically 1 ≤ p ≤ 3).

**T₂* (inhomogeneous dephasing).** For a single NV in a ¹²C-enriched sample, T₂* can reach hundreds
of µs; in natural-abundance diamond the ¹³C nuclear spin bath limits T₂* to ~1–10 µs for single NVs
and ~1–100 µs for ensembles (it scales with the isotopically purified ¹²C fraction). T₂* sets the
number of usable fringe oscillations, i.e. the information available in the sweep, and it directly
sets the optimal interrogation time τ ≈ T₂*.

**Fringe.** The measured curve S(τ). Key structural parameters: contrast C (visibility, attenuated by
readout infidelity and decoherence), number of oscillatory periods visible ≈ γ_e B T₂*/2π, and the
sweep range 0 < τ < τ_max. A **crucial nuisance** for low-field operation: the fringe is periodic, so
the frequency is only identifiable modulo 2π/Δτ where Δτ is the sampling step — this is the
**aliasing / phase-wrapping** problem (the estimator can lock onto a wrong alias, ω → ω + 2π/Δτ).

**Aliasing / phase wrapping.** Because cos(ωτ) is even and periodic in ωτ, a coarse τ grid admits
multiple field values consistent with the data; only the Bayesian posterior or an explicitly
unwrapped fit resolves the ambiguity. This is the same physics that makes FFT-based estimators
ambiguous between ω and (sampling frequency − ω), and it is the reason grid/FFT methods fail at low
field or with sparse grids.

**Photon shot noise.** The dominant noise at low budget. Counts are Poisson: for N_ph detected
photons per measurement, the fractional count noise is 1/√N_ph. The resulting field uncertainty is
approximately

    δB ≈ 1 / (γ_e · C · √N_ph)          (photon-shot-noise limit, optimal τ ≈ T₂*)

which is why "fewer repetitions" ⇒ fewer photons per point ⇒ larger δB for *any* estimator; the
question is only **how close a given estimator comes to this bound** at low N_ph. Barry et al. (2020)
decompose the full expression into spin-projection-limited, spin-dephasing, readout and overhead
terms, with the readout term scaling as 1/(C²·n_avg) where n_avg is the mean photon number collected
per measurement.

**Sensitivity η.** η = δB · √t_total, units T/√Hz (= T·s^(1/2)). The √t_total accounts for the fact
that averaging M independent measurements reduces δB by √M; thus η is the fundamental
time-normalized precision. Values quoted in the literature (see below) span roughly
0.4 nT/√Hz to 60 nT/√Hz for realistic room-temperature devices, with best ensemble demonstrations in
the pT/√Hz range under heavy averaging.

**t_total bookkeeping.** Two conventions coexist and must not be mixed:
(i) *per-measurement* convention: t_total = a single shot's cost (e.g. τ + t_ovh per point × 300 points),
giving an η that describes the hardware's instantaneous precision rate;
(ii) *accumulation* convention: t_total = the wall-clock time of all repetitions used to reach δB.
In this project L5 uses the accumulation convention explicitly: for a full 300-point sweep at
repetition level r, t_total ≈ r · Σᵢ(τᵢ + t_ovh), and t_ovh (readout + pulse overhead per point) must
be declared and sensitivity-analyzed (0.5×/1×/2× brackets).

**Cramér–Rao lower bound (CRLB).** For an unbiased estimator, Cov(B̂) ≥ I(B)⁻¹, where I(B) is the
Fisher information of the model S(τ|B) at the true parameter. For a photon-counting Ramsey sweep,
I(B) is a sum over τ points of (∂S/∂B)²/(S + background shot noise), so the CRLB depends on where the
τ points sit relative to the fringe extrema and how many photons each point carries. The CRLB is the
right benchmark for "is this estimator optimal?", and it is the benchmark against which learned
estimators must be judged. The quantum Fisher information / quantum CRLB generalizes this to
optimization over probe states and controls; for single-parameter DC field estimation the QCRB is
attainable, and multi-parameter cases (e.g. B together with T₂*) can have a singular QFIM, so joint
estimation is not always simultaneously optimal.

**Readout fidelity and contrast.** Room-temperature NV readout: ~20–40% contrast for a single NV,
lower for ensembles (often 1–10% without hyperfine-resolved control); ¹⁴N hyperfine structure
(splitting ~2.2 MHz) further reduces fringe contrast by ~3× unless triple/multi-tone microwave
control is used. Readout fidelity can be improved with spin-to-charge conversion, single-shot
cryogenic readout, or cavity/light-trapping geometries — all of which change the *hardware* η and are
orthogonal to the *estimator* question.

## Standard Methods

### 1. Classical frequency/phase estimation

- **FFT peak + interpolation.** Take the DFT of the (background-subtracted) fringe, find the peak
  bin, then interpolate for sub-bin accuracy. Canonical theory: Rife & Boorstyn (1974) derived the
  ML estimator for a single complex tone and the exact CRB, and showed FFT-peak estimation is ML over
  a coarse grid; the interpolation schemes (Quinn 1994; Aboutanios & Mulgrew 2005) close most of the
  gap to the CRB at high SNR. Known failure mode: a **threshold effect** below a certain SNR, where
  the estimator "loses lock" and the variance collapses to (bin spacing)²/12 — exactly the regime a
  low photon budget puts you in.
- **Least-squares Levenberg–Marquardt with multi-start.** Fit S(τ) = A + C·cos(ωτ + φ₀)·e^{−(τ/T₂*)^p}
  directly. This is the most common NV practice. It is asymptotically efficient (approaches the CRB)
  when initialized near the true frequency, but it is a non-convex fit: at low photon counts the
  optimizer can converge to a wrong alias or to a local minimum with unphysical T₂*, and the reported
  covariance from the Jacobian can badly understate the true spread. Multi-start over ω (grid of
  candidate frequencies) mitigates but does not eliminate this. Optional refinements: fixing p, using
  variable projection (Golub–Pereyra) to eliminate the linear parameters, or re-parameterizing to
  avoid φ₀/T₂* coupling.
- **Grid Bayes / maximum-likelihood on a grid.** Discretize B (or ω) on a grid, evaluate the Poisson
  or Gaussian likelihood of the full sweep for each grid point, and return the posterior mean /
  MAP. Robust and alias-aware because the full sweep is used, and it naturally yields a posterior
  width rather than a Jacobian approximation; cost is O(grid × τ points).
- **Hilbert / analytic-signal phase estimation.** Convert the real fringe to a complex analytic
  signal (Hilbert transform, or quadrature detection by a second measurement at φ+π/2), then
  unwrap the phase φ(τ) = ωτ + φ₀ and fit a straight line. Fast and accurate when the SNR is
  adequate to unwrap reliably; breaks down with phase slips at low photon counts. Directly related
  to the "phase-based, time-domain" estimators in the signal-processing literature.
- **Subspace / parametric methods** (Prony, ESPRIT, matrix pencil, MUSIC). Fit sums of damped
  exponentials from a covariance/Hankel matrix. High resolution at moderate SNR but statistically
  inefficient and noise-sensitive for a single damped sinusoid; rarely used in NV practice.

### 2. Bayesian / MCMC estimation and posterior-based uncertainty

Bayesian inference treats B, C, T₂*, φ₀, background as random variables, propagates a prior through
the likelihood of the full sweep, and returns a posterior. Advantages relevant here: (a) the
posterior is the correct uncertainty statement at *any* SNR, whereas the LM covariance is only valid
asymptotically; (b) priors encode physical knowledge (T₂* range, expected field range, known τ_off
readout offset) which is exactly the kind of side information a low-photon-budget experiment needs;
(c) the same machinery supports **adaptive** τ selection (choose next τ to minimize expected
posterior entropy or variance). Implementations range from grid/Laplace approximations through
sequential Monte Carlo ("particle filter") to MCMC. Real examples: Santagati et al. (2019) used
sequential Monte Carlo Bayesian phase estimation with one photon per step, achieving 60 nT·s^{1/2}
from a single room-temperature NV; McMichael et al. (2021) formulated sequential Bayesian *experiment
design* for τ selection and reported 2×/4× speed-ups over adaptive-heuristic and random protocols in
the low-fidelity averaged-readout regime; Wu et al. (2021, PRA 103, 042607) used Bayesian estimators
on single-photon events in a coherent-population-trapping protocol and approached the classical CRLB.

### 3. Neural / learned estimators for NV

Two distinct roles, often conflated in the literature:

*Estimator (inference side).*
- **Simulation-trained regression networks.** Train on synthetic Ramsey/ODMR data with known labels;
  deploy on real data. Reported for ODMR mostly: Homrighausen et al. (2023) trained an ANN on CW-ODMR
  spectra of randomly oriented NV ensembles and ran inference on an ESP32 microcontroller (edge ML).
  More recent 2025 work compares 18 regressors on all-optical NV data (LightGBM/XGBoost reportedly
  R² ≈ 0.999) and uses fully connected networks to beat nonlinear least squares for low-field
  ambiguity resolution up to 8 mT.
- **CNN estimators on spectra/fringes.** Yao et al. (arXiv:2603.14728) use a 1D-CNN for direct
  parameter inference from ODMR spectra without initialization or iterative fitting, reporting the
  largest gains at low SNR — the closest analogue of "fit-free" estimation.
- **Physics-informed / sim-to-real.** NVRNet (Shang & Fuchs, arXiv:2603.14144, 2026) pretrains
  U-Net denoisers on Hamiltonian-based Ramsey simulations with experimentally calibrated noise, then
  fine-tunes lightweight uncertainty-aware adapter layers on real single-NV traces; reports
  reconstruction error 0.44–0.67× the raw noise and ~40× faster characterization. It estimates
  *hyperfine parameters*, not B, and is a characterization (not sensitivity) result.
  Daniel et al. (arXiv:2608.19582, 2026) embed the Zeeman splitting into the learning pipeline for
  ensemble NV sim-to-real calibration and report a 372× tracking-error improvement over a purely
  statistical baseline on uncalibrated raw ODMR data.
- **Graybox models.** Youssry, ..., Bonato (arXiv:2601.17465, 2026) blend a physics model with a
  learned correction of experimental imperfections, then do Bayesian inference of a static field
  with a single spin; with ~10⁴ training points the graybox beats both the whitebox physics model
  (by orders of magnitude in MSE) and a comparable blackbox network.

*Controller (experiment-design side).*
- **Reinforcement learning / model-aware RL.** Belliardo, Zoratti & Giovannetti
  (arXiv:2403.05706 = PRA 109, 062609 (2024); software qsensoropt) train NN agents to choose τ and φ
  adaptively for repeated Ramsey measurements of electronic spins in diamond, estimating B, hyperfine
  couplings and decoherence times; they report beating the particle-guess heuristic and σ⁻¹ strategies.
- **Bayesian-NN + federated RL, two-stage.** Guo et al. (arXiv:2506.13469) narrow the field range
  with a Bayesian NN, then fine-tune sensing parameters with federated RL under a total sensing-time
  budget, for single-shot-readout NV DC estimation.
- **Entropy-based adaptive scheduling.** Greentree et al. (arXiv:2510.21108) minimize entropy
  step-by-step to design Ramsey measurement sequences, evaluated on NV magnetometry in simulation.
- **Surrogate-model control optimization.** Jauch et al. (QST 11, 015055 (2026)) use Gaussian
  processes and ANNs as fast-retrainable surrogates for microwave pulse-shape optimization in a
  Ramsey sequence, reporting >6× faster convergence, up to 59.6% Ramsey contrast (vs rectangular
  pulses) and a 41.9% SNR gain on a synthetic magnetocardiographic signal.

*Caveats documented in the literature itself.* NN estimators are biased; one broadband-microwave
study reported that NN models struggled to learn from the data; several high-profile gains are
simulation-only; and no paper found here reports a learned estimator that beats a well-tuned
classical fit *in η = δB√t_total on real NV data at low repetition counts*.

### 4. Amortized inference / conditional density estimation

Outside NV physics, the dominant modern paradigm for "estimate parameters from noisy physical
observations" is **simulation-based inference (SBI)**: train a conditional density estimator
(normalizing flow, or a classifier/ratio estimator as in TMNRE) to approximate p(θ|x) directly from
simulated (θ, x) pairs. Once trained, the posterior for a new observation costs a single forward
pass — no per-observation MCMC or multi-start optimization. Documented in astrophysics and
condensed-matter contexts (galaxy SED fitting, eclipsing binaries, kilonova spectra, RIXS Hamiltonian
inference), with speed-ups of ~10³× over nested sampling and calibration validated by SBC/TARP
tests. Key transferable ideas for NV: (a) *amortization* — the expensive part (training) is done
once, so per-measurement inference cost drops out of t_total, which matters when the estimator runs
inside an experiment loop; (b) *posterior calibration* — SBI provides goodness-of-calibration
diagnostics that classical LM fits do not; (c) *marginalization over nuisance parameters*
(background, T₂*, φ₀, readout offset) is native rather than a nuisance to be profiled. There is a
tension to be honest about: amortized posteriors can be miscalibrated if the simulation does not match
the real noise (sim-to-real gap), which is exactly the failure mode NVRNet and Daniel et al. try to
patch with physics-informed fine-tuning. For NV specifically, amortization appears only as an
*adaptive controller* (Belliardo et al.; Guo et al.) or as a hyperfine-characterization denoiser
(NVRNet) — never as a *density estimator over a full fixed Ramsey sweep, benchmarked in η*.

## Sensitivity and the SNR budget

**Definitions in use.** The NV literature quotes η with several different normalizations and it is a
classic source of invalid comparisons. Barry et al. (2020, RMP 92, 015004) is the definitive
treatment; Rondin et al. (2014) and Degen et al. (2017) give the standard derivations.

- **CW-ODMR sensitivity** (continuous microwave drive, sweep frequency):
  η_CW ≈ (4/(3√3)) · Δν / (γ_e · C · √R), with Δν the FWHM linewidth (Hz), C the contrast, R the
  detected photon rate (s⁻¹). Equivalent angular-frequency form η ≈ (8π/(3√3))·(1/γ)·δν/(C√R).
  The 4/(3√3) factor is the optimum of the Lorentzian slope, i.e. a statement about the best
  operating point, not about the estimator.
- **Pulsed Ramsey (DC) sensitivity**: for interrogation time τ and per-shot overhead t_ovh,
  η ≈ (1/(γ_e C)) · √((τ + t_ovh)/(τ · n_ph)) with n_ph the photons collected per shot at τ; the optimum
  is τ ≈ T₂*, giving η ∝ (1/(γ_e C √n_ph)) · √(1 + t_ovh/T₂*) / √(T₂*)-type scaling. Barry's full form
  multiplies a spin-projection term (∝ N⁻¹ᐟ²τ⁻¹ᐟ²), a dephasing factor e^{−(τ/T₂*)^p}, a readout term
  ∝ 1/(C²n_avg) and an overhead factor (t_I + τ + t_R)/τ.
- **Two meanings of "DC sensitivity".** (a) The *per-shot* η above (an extrapolation assuming white
  noise, answering "what δB do I get in 1 s of accumulated data?"); (b) the *achieved* δB after a
  stated total time T_total (what Mazes's "3 nT at kHz after 100 s" and Wolf's "900 fT in 100 s"
  mean). Only (b) is estimator-sensitive at low photon counts, and only (b) is directly comparable
  across estimators when the photon budget is fixed. This distinction is the crux of the L5 program.

**Real reported values (with provenance caution).**

| System | Reported η | Note |
|---|---|---|
| Single NV in 30-nm nanocrystal (Maze 2008) | 0.5 µT/√Hz | 3 nT detected at kHz after 100 s averaging |
| Single NV, one-photon-readout Bayesian (Santagati 2019) | **60 nT·s^(1/2)** | includes init/readout/computational overhead; ~1 photon per step |
| Ensemble, light-trapping waveguide (Clevenson 2015) | ~1 nT/√Hz (0.1–10 Hz) | corrigendum issued; 0.93 nT std in 10 s |
| Ensemble N~10¹¹ (Wolf 2015) | 9 pT/√Hz **after erratum** | originally claimed 0.9 pT/√Hz; PRX erratum 13, 029903 (2023); 900 fT in 100 s |
| Ensemble, ODMR, multi-diamond comparison (Jani 2025) | 380 pT/√Hz | photon-shot-noise-limited, ODMR not Ramsey |
| Cavity nanophotonic Ramsey (Sørensen 2025, arXiv:2511.19831) | 58 nT/√Hz DC | Ramsey + lock-in, best claimed for a nanofabricated cavity device |
| Theory: DC CW vs pulsed at optical-power limit (arXiv:2311.06055) | pulsed ~2–3× better | much less than single-NV power-unlimited advantage |
| Error-budget study (Leclerc 2026, arXiv:2608.28519) | bias 8–1500 nT at equal η | equal sensitivity does NOT imply equal accuracy |

**Interpretation for a low-photon-budget project.** (i) The hardware η values above are mostly
*per-shot extrapolations* at high photon flux, not the achieved precision from a bounded photon
budget; (ii) at low N_rep the estimator's efficiency relative to the CRLB is the entire story, and
that has essentially not been characterized on real NV Ramsey sweeps; (iii) overhead t_ovh is not
negligible — if t_ovh ≫ τ, the achievable η saturates and the choice of sweep length (300 points)
itself becomes a design parameter; (iv) the sensitivity comparison must hold the τ grid, the data
and the photon budget fixed, which is precisely the "full sweep + low reps" cell.

## Active Research Directions (2024–2026)

1. **Learned estimators for NV spectra/fringes**, moving from ODMR spectra (easier: static lineshapes)
   to Ramsey time series (harder: damped oscillation + alias + nuisance parameters). Dominant
   architecture choices: 1D-CNN and U-Net denoisers, MLPs on subsampled spectra, ensembles of
   gradient-boosted trees for deployment. Reported win conditions are consistently *speed*, *robustness
   at low SNR*, and *removal of initialization/fitting failures* — NOT improved η on real data.
2. **Sim-to-real transfer and physics-informed models.** The recognized bottleneck is that
   simulation-trained networks fail on real instruments (laser drift, sample drift, unmodeled noise).
   Solutions in 2026 preprints: parameter-efficient adapters fine-tuned on a few real traces (NVRNet);
   embedding the Zeeman term directly in the pipeline (Daniel et al.); graybox hybrid models
   (Youssry et al.). This is currently the hottest sub-area and it is *directly relevant* to any plan
   that trains on synthetic-augmented real data.
3. **Adaptive / RL experiment design.** qsensoropt-style model-aware RL and entropy/Bayesian
   scheduling for τ and φ choices. Mostly simulation; the reported gains over heuristics are modest
   (2–4×) and the field has been converging on Bayesian sequential design as the practical winner.
   Notably, adaptive τ shortening is *incompatible* with a fixed full-sweep protocol.
4. **Photon-efficient protocols and readout.** Repetitive readout, spin-to-charge conversion,
   cavity/light-trapping, hyperfine-resolved multi-tone drive (claimed up to 3–4× sensitivity gains
   from double-quantum Ramsey + spin-bath driving, and up to 3× from triple-tone control in the
   low-dephasing regime). These attack the photon budget at the *hardware* level; they are the
   natural companion/competitor framing for any estimator-level claim.
5. **Subsampling and compressed sensing.** CS applied to ensemble ESR peak location (arXiv:2502.06070:
   ~100 points matched a full raster at high field, no advantage at low field); physics-constrained
   CS enforcing PSD/Toeplitz structure in the data-starved regime (QST, Kalev); sparse-sampling
   wide-field reconstruction with a training-free mean-adjusted Bayesian estimator
   (arXiv:2602.00679, simulation, 25 points for a 10 000-pixel image). Note: these reduce the number
   of *τ/frequency points*, which is a different axis from reducing the *repetitions per point*.
6. **Quantum metrology meets deep learning.** Quantum-circuit learning to extend dynamic range
   (arXiv:2505.04958), QML under measurement-induced information loss (arXiv:2608.23934, which finds
   that classical ML on measurement statistics does about as well as quantum kernels unless coherent
   pre-measurement information is available), variational Bayesian frameworks for joint estimation
   and model learning (arXiv:2507.23130). Mostly methodology, not NV hardware.
7. **Multi-parameter and vector magnetometry** with correct treatment of Fisher-information
   singularities, dead zones, and joint estimation of B and T₂*. Relevant because estimating T₂*
   jointly with B is a natural part of any Bayesian treatment of a Ramsey sweep and can change the
   achievable CRLB.

## Key Venues

| Venue | What it expects | Fit for this project |
|---|---|---|
| **Physical Review A** (PRA) | Estimation theory, quantum metrology protocols, Fisher information, adaptive schemes. Tolerates simulation-only if the theory is clean. | Good for the CRLB/estimator-theory core |
| **Physical Review Applied** (PRApplied) | Device-level demonstrations, sensitivity improvements, instrumentation. Wants real hardware and honest η numbers. | Primary target if claims are hardware-grounded |
| **Physical Review B / PRX Quantum** | Condensed-matter spin physics / higher-impact quantum information and metrology. | Stretch; needs a strong conceptual novelty beyond estimator performance |
| **Reviews of Modern Physics** (RMP) | Invited-scale reviews (Barry 2020, Degen 2017 are here). | Only as citation source, not a target |
| **npj Quantum Information** | Quantum sensing + information-theoretic framing; friendly to ML-adjacent method papers. | Strong target for "learning + metrology" framing |
| **Quantum Science and Technology** (IOP, QST) | Applied quantum technology, protocols, ML-enhanced sensing (Jauch 2026 published here). | Good target; open access, explicit ML appetite |
| **Optics Letters / Optica / Optics Express** | Optical instrumentation, radiometry, fast hardware demonstrations. | Only if the story is an optical-hardware improvement |
| **Applied Physics Letters / Rev. Sci. Instrum.** | Compact device and technique papers; less theory depth. | Secondary |
| **IEEE Sensors Journal / IEEE Trans. Instrum. Meas.** | Sensor engineering, ML deployment, edge inference, benchmarking of regressors. | Where the ODMR-ML papers land; low physics prestige |
| **Machine Learning: Science and Technology** (IOP) | ML methodology applied to physical sciences; wants ML rigor (baselines, calibration, ablations). | Good fit for the learned-estimator framing; physics audience is secondary |
| **npj/Nature-family (Nature Communications, Sci. Adv.)** | Needs a headline result with broad appeal, or a real-data win beating the state of the art on multiple fronts. | Only if the pilot produces a large, robust, real-data effect |
| **ML conferences (NeurIPS/ICML/ICLR)** | Methodological novelty in learning; NV-specific results are usually not enough on their own. | Unlikely primary venue; consider a physics-ML workshop |

Practical note: NV/quantum-sensing papers are conventionally judged on real data with declared
parameter provenance, explicit uncertainty, and CRLB comparison — a simulation-only learned estimator
is normally a desk reject at the physics venues unless the method itself is the contribution.

## Reference Papers

32 numbered entries (25 primary + 7 supporting/methodological), every one verified by a live arXiv
listing, journal page, or index hit during compilation on 2026-09-12. IDs are arXiv unless a DOI is
given. Entries marked "(Supporting)" are secondary-but-useful; the primary 25 are the ones a related-
work section should engage.

*Foundational NV magnetometry*
1. J. M. Taylor, P. Cappellaro, L. Childress, L. Jiang, D. Budker, P. R. Hemmer, A. Yacoby, R. Walsworth, M. D. Lukin, "High-sensitivity diamond magnetometer with nanoscale resolution," *Nature Physics* **4**, 810 (2008). arXiv:0805.1367. — Foundational theory of the NV magnetometer; AC/DC sensitivity formalism, ensemble vs single-spin.
2. J. R. Maze et al., "Nanoscale magnetic sensing with an individual electronic spin in diamond," *Nature* **455**, 644 (2008). DOI 10.1038/nature07279. — First experimental nanoscale NV magnetic sensing; 0.5 µT/√Hz for a 30-nm crystal, 3 nT detected after 100 s. The canonical low-photon-count baseline.
3. G. Balasubramanian et al., "Nanoscale imaging magnetometry with diamond spins under ambient conditions," *Nature* **455**, 648 (2008). DOI 10.1038/nature07278. — Companion experimental demonstration; scanning-probe imaging.
4. L. Rondin, J.-P. Tetienne, T. Hingant, J.-F. Roch, P. Maletinsky, V. Jacques, "Magnetometry with nitrogen-vacancy defects in diamond," *Rep. Prog. Phys.* **77**, 056503 (2014). DOI 10.1088/0034-4885/77/5/056503. — Standard review; sensitivity limits, measurement schemes, single vs ensemble.
5. C. L. Degen, F. Reinhard, P. Cappellaro, "Quantum sensing," *Rev. Mod. Phys.* **89**, 035002 (2017). arXiv:1611.02427. — The standard metrology framework: Ramsey/DD protocols, filter functions, sensitivity, SQL/Heisenberg limits.
6. J. F. Barry, J. M. Schloss, E. Bauch, M. J. Turner, C. A. Hart, L. M. Pham, R. L. Walsworth, "Sensitivity optimization for NV-diamond magnetometry," *Rev. Mod. Phys.* **92**, 015004 (2020). arXiv:1903.08176. — **The** sensitivity reference: full η decomposition (spin projection, dephasing, readout, overhead), readout-fidelity and material routes, tabulated photon collection numbers. Defines the η conventions any L5 claim must use.

*Sensitivity benchmarks and photon-budget hardware*
7. T. Wolf et al., "Subpicotesla diamond magnetometry," *Phys. Rev. X* **5**, 041001 (2015). arXiv:1411.6553. **Erratum: Phys. Rev. X 13, 029903 (2023)** — sensitivity corrected from 0.9 pT/√Hz to 9 pT/√Hz. — Cautionary tale on η bookkeeping; still the ensemble-AC reference point.
8. H. Clevenson et al., "Broadband magnetometry and temperature sensing with a light-trapping diamond waveguide," *Nature Physics* **11**, 393 (2015). DOI 10.1038/nphys3291 (corrigendum issued). — ~1 nT/√Hz broadband DC; photon-collection engineering.
9. "Nanophotonic magnetometry in a spin-dense diamond cavity," arXiv:2511.19831 (2025). — 58 nT/√Hz DC Ramsey sensitivity, lock-in amplified, best claimed for a nanofabricated cavity device; a current hardware η datapoint.
10. "Triple-Tone Microwave Control for Sensitivity Optimization in Compact Ensemble NV Magnetometers," arXiv:2510.00913 (2025, accepted *Optica*). — Hyperfine-resolved multi-tone drive; up to 3× ODMR sensitivity gain, Ramsey gain only under limited microwave power. Defines the hardware-side competition for contrast.
11. "Comparing continuous and pulsed NV DC magnetometry in the optical-power-limited regime," arXiv:2311.06055, *J. Opt. Soc. Am. B* **41**, 62 (2024). — Pulsed Ramsey only ~2–3× better than CW when optical power is limited; sets realistic expectations for protocol-level gains.
12. N. Leclerc et al., "Beyond sensitivity: mechanism-resolved error budgets for designing quantum sensors," arXiv:2608.28519 (2026). — Same η, bias 8–1500 nT depending on limiting mechanism; argues sensitivity-only optimization is insufficient. Directly relevant to how L5 should report.

*Classical estimation theory (the baseline toolbox)*
13. D. C. Rife, R. R. Boorstyn, "Single-tone parameter estimation from discrete-time observations," *IEEE Trans. Inf. Theory* **20**, 591 (1974). DOI 10.1109/TIT.1974.1055282. — Exact CRB and ML for a single tone; the threshold effect that low photon budgets expose.
14. E. Aboutanios, B. Mulgrew, "Iterative frequency estimation by interpolation on Fourier coefficients," *IEEE Trans. Signal Process.* **53**, 1237 (2005). DOI 10.1109/TSP.2005.843704. — Standard FFT-interpolation estimator; the "FFT+Rife-like" classical baseline. (Related standard tools, cited inline in §1: Quinn's Fourier-coefficient interpolation; Kay's phase-based single-frequency estimator; Golub–Pereyra variable projection for separable NLLS.)

*Bayesian / adaptive Ramsey estimation with few photons*
15. R. Santagati et al., "Magnetic-field learning using a single electronic spin in diamond with one-photon readout at room temperature," *Phys. Rev. X* **9**, 021019 (2019). arXiv:1807.09753. — **The key precursor**: Bayesian phase estimation + Hamiltonian learning, ~1 photon per step, 60 nT·s^(1/2) including all overheads, tracks time-varying fields. Any L5 novelty claim must be positioned against this.
16. S. McMichael, S. Dushenko, K. Blakley, "Sequential Bayesian experiment design for adaptive Ramsey sequence measurements," *J. Appl. Phys.* **130** (2021). arXiv:2105.02327. — Bayesian τ selection in the low-fidelity averaged-readout NV regime; 2×/4× speed-up over heuristic/random. The practical adaptive-design reference.
17. S.-H. Wu, E. Turner, H. Wang, "Continuous real-time sensing with a nitrogen-vacancy center via coherent population trapping," *Phys. Rev. A* **103**, 042607 (2021). arXiv:2102.07212. — Single-photon-event Bayesian estimator approaching the classical CRLB at a few percent collection efficiency.
18. J. Greentree, W. Moran, R. Evans, A. Melatos, N. K. Kundu, P. M. Farrell, "Myopic Entropy Scheduling for Ramsey Magnetometry," arXiv:2510.21108 (2025). — Entropy-minimizing adaptive sequence design evaluated on NV Ramsey; recent competitor in the adaptive-design lane (simulation).

*Learned estimators and ML controllers for NV*
19. F. Belliardo, F. Zoratti, V. Giovannetti, "Applications of model-aware reinforcement learning in Bayesian quantum metrology," *Phys. Rev. A* **109**, 062609 (2024). arXiv:2403.05706. Companion: arXiv:2403.10317 (*Int. J. Quantum Inf.*, 2024). — RL agents choose τ/φ for repeated Ramsey measurements on electron spins in diamond; qsensoropt. The strongest existing learned-estimator/controller work in this exact physical setting.
20. S. Guo, J. Liu, T. Le, H. Dai, "A Two-stage Optimization Method for Wide-range Single-electron Quantum Magnetic Sensing," arXiv:2506.13469 (2025). — Bayesian NN + federated RL under a total sensing-time budget; single-shot readout NV DC field. Closest to an "amortized coarse-to-fine" estimator under a time budget.
21. G. Haim, S. Martina, J. Howell, N. Bar-Gill, F. Caruso, "Machine-learning based high-bandwidth magnetic sensing," *Mach. Learn.: Sci. Technol.* **6**, 025074 (2025). arXiv:2409.12820. — MLP on heavily subsampled ensemble ESR spectra; up to 5× improvement in the sensitivity/bandwidth figure of merit, ~3× fewer data points, tested on real scans. The best real-data ML-NV-sensitivity datapoint found.
22. C. Shang, G. D. Fuchs, "Fast Single Nitrogen-Vacancy Center Ramsey Characterization using a Physics-Informed Neural Network (NVRNet)," arXiv:2603.14144 (2026). — Simulation-pretrained U-Net + uncertainty-aware adapters fine-tuned on real Ramsey traces; ~40× faster characterization. The template for sim-to-real Ramsey pipelines (but estimates hyperfine parameters, not B).
23. J. Daniel, M. Y. Kim et al., "Physics-guided machine learning for sim-to-real calibration of NV diamond magnetometers," arXiv:2608.19582 (2026). — Zeeman term embedded in the learning pipeline; 372× tracking-error improvement over a statistical baseline on raw uncalibrated ODMR. Evidence for physics-informed priors being the deciding factor.
24. A. Youssry, S. Todd, P. Murton, M. J. Arshad, N. Werren, A. Peruzzo, C. Bonato, "Bayesian quantum sensing using graybox machine learning," arXiv:2601.17465 (2026). — First experimental graybox (physics + learned imperfection) model for a solid-state spin; Bayesian static-field estimation beating both whitebox and blackbox with ~10⁴ training points.
25. J. Homrighausen, L. Horsthemke, J. Pogorzelski, S. Trinschek, P. Glösekötter, M. Gregor, "Edge-machine-learning-assisted robust magnetometer based on randomly oriented NV ensembles in diamond," *Sensors* **23**, 1119 (2023). — ANN on ODMR spectra, inference on an ESP32; exemplar of the deployment-oriented ML-NV lane.
26. (Supporting) B. Varona-Uriarte et al., "Automatic detection of nuclear spins at arbitrary magnetic fields via signal-to-image AI model," *Phys. Rev. Lett.* **132**, 150801 (2024). arXiv:2311.15037; and "A Deep-Learning-Boosted Framework for Quantum Sensing with NV Centers in Diamond," arXiv:2603.14728 (2026). — CNNs on noisy NV spectra for hyperfine inference and for initialization-free parameter extraction, with the largest gains reported at low SNR. Evidence that learned estimators help exactly where analytic fits break.
27. (Supporting, method citation) I. Jauch, T. Strohm, T. Fuchs, F. Jelezko, "Quantum magnetometry enhanced by machine learning," *Quantum Sci. Technol.* **11**, 015055 (2026). DOI 10.1088/2058-9565/ae3acf. — GP/ANN surrogates for microwave pulse-shape optimization in Ramsey; 59.6% contrast, 41.9% SNR gain. ML attacking the *contrast*, not the estimator. (Discussed in §3.)

*Subsampling / information-limited estimation*
28. "Compressed sensing enabled high-bandwidth and large dynamic range magnetic sensing," arXiv:2502.06070 (2025). — CS for ESR peak location; ~100 points matched a full raster at SNR≈3, **no advantage at lower field/SNR**. Honest negative result relevant to any "fewer points" claim.
29. "High-resolution wide-field magnetic imaging with sparse sampling using NV centers," arXiv:2602.00679 (2026). — Training-free Bayesian (MABE) reconstruction from 25 points; simulation only; notes CS/GP adaptive sampling as future routes.
30. "QML for Quantum Sensing under Measurement-Induced Information Loss," arXiv:2608.23934 (2026). — NV Ramsey framed as a regression benchmark; classical ML on measurement statistics is competitive unless coherent pre-measurement information is available. Useful for scoping what ML can and cannot buy.
31. H. Yamauchi, S. C. Stearn, S. Tovey, "Sequential Spatiotemporal Magnetic-Field Reconstruction via Quantum Hamiltonian Learning with NV-Center Spin-1 Hamiltonians," arXiv:2605.23455 (2026). — Sequential Bayesian updates with Fisher-information/leakage diagnostics; identifies coupling identifiability as the bottleneck.
32. (Methodological pointer, not NV-specific) Amortized neural posterior estimation / TMNRE as implemented in `swyft` and related SBI toolboxes; recent applications include RIXS Hamiltonian posterior inference (arXiv:2608.13848) and galaxy SED fitting (arXiv:2511.10640). — Blueprint for training once and evaluating posteriors at near-zero per-measurement cost, with SBC/TARP calibration diagnostics.

## Open gaps / what appears NOT to have been done

Honest read as of 2026-09-12, after the searches above.

**Is "full 300-point sweep + low repetitions + sensitivity-metric-optimized estimation" occupied?**
Not that I can find. The cell appears **unoccupied as a whole**, though every one of its walls has
neighbors:

1. **The photon-budget axis and the full-sweep axis are being attacked separately, never together.**
   Santagati (2019) is the strongest low-photon result (one photon per step, 60 nT·s^(1/2)) but its
   protocol is *adaptive single-τ*, not a fixed full sweep — it deliberately avoids spending photons
   on τ points it judges uninformative. Conversely, the ML-on-subsampled-data works (Haim 2025; CS,
   arXiv:2502.06070) keep the per-point repetition high and drop τ points instead. NVRNet uses
   *minimal-sweep* Ramsey traces but targets hyperfine characterization, not B, and does not report η.
   Nobody found here benchmarks an estimator on a **fixed, complete 300-point Ramsey sweep at very low
   repetitions per point** and reports **η = δB·√t_total against the CRLB**, with the classical
   baselines (LM multi-start, FFT+interpolation, grid Bayes) given a full tuning budget. That
   specific comparison — the "estimator efficiency gap at fixed photon budget" — is the white space.

2. **The metric is almost never the headline.** Real NV papers report *hardware* η (photon shot-noise
   limited extrapolation at a single optimal τ) or *speed/throughput*, not the estimator-limited
   η from a bounded dataset. Only a handful report absolute sensitivities with all overheads included
   (Santagati 60 nT·s^(1/2); Leclerc 2026's error-budget argument that equal η ≠ equal accuracy). The
   framing "given a fixed photon budget, which estimator reaches δB* with the fewest repetitions?" —
   the operationally useful form — is essentially absent, which makes it available and also means the
   community has not settled the baselines, so a careful L5 must define them itself.

3. **Real-data learned estimators for B are thin, and sim-to-real is the recognized blocker.**
   Almost every learned-NV work is either ODMR (static lineshapes, easier) or simulation-only, and
   the 2026 preprints (NVRNet, Daniel et al., Youssry et al.) all explicitly diagnose the
   simulation-to-reality gap as the hard part. A learned estimator trained on real low-repetition
   Ramsey sweeps (with synthetic augmentation anchored in real fitted parameters), evaluated on
   held-out real data with paired statistics, would land in a genuinely under-served region — and
   the L1 bloodline (τ_off calibration conventions, APCE-style amortized estimation) is exactly the
   kind of physics prior that the sim-to-real literature says is needed.

Cross-check against the anti-overlap gates: L1 owns the calibration-anchoring story (τ_off/φ₀ as a
discovery), L3/L4 own sampling-design/aliasing-as-the-story. L5 must therefore *not* sell calibration
or sampling design as the novelty, and must not use an adaptive/short-τ protocol. The defensible
claim shape is narrow and specific: **at a fixed full sweep and a fixed, small repetition count,
a well-regularized learned/amortized estimator attains a target δB with fewer repetitions than
fully-tuned classical baselines, measured in η, on real data, ≥3 seeds, paired tests, with the CRLB
as the ceiling.** Two risks to pre-register: (a) if the classical LM/Bayes baseline is already at the
CRLB at the tested repetition levels, there is no headroom and the pilot must be reported as negative
(this is a realistic outcome, given that Bayesian estimators were shown to approach the CRLB in
Wu 2021 and the FFT threshold effect only bites at quite low SNR); (b) prior-conditioned estimators
can win at low photon budget merely by exploiting the prior, which must be disclosed and controlled
(prior-only baselines, priors matched to what the classical methods are also allowed to use).
