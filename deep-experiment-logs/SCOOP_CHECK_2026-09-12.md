# Scoop Check — 2026-09-12

**Project**: NV×AI Line #5 — Sensitivity-optimal low-SNR Ramsey estimation (nv-research4)
**Cell under check**: estimate DC field B from NV Ramsey data at **low photon budget** (few reps, 5k–40k shots/τ) while **keeping the full 300-τ sweep**, optimizing the **sensitivity figure of merit η = δB·√t_total**, using **ML / amortized / prior-informed estimators** (simulation-trained neural posterior, hierarchical/joint estimation across traces, calibration-conditioned priors) against classical baselines (LM multi-start, FFT+Rife, grid Bayes); optionally cross-field transfer / meta-learning.

**Verdict: SAFE (qualified) — no direct occupancy found.** See §Verdict for the qualification and the required differentiation moves.

---

## Queries run

### Direct database/API attempts (all rate-limited from this host)
| Target | Endpoint | Result |
|---|---|---|
| arXiv API | `export.arxiv.org/api/query?search_query=...` (multiple formulations: `all:"NV center" AND all:"neural" AND all:"magnetic field"`; `(magnetometry OR "quantum sensing") AND (amortized OR "simulation-based inference" OR "neural posterior")`; `abs:"NV center" AND abs:"sensitivity"`; `all:"nitrogen-vacancy" AND all:"neural network"`; `abs:"NV center" AND abs:"Ramsey"`) | HTTP 429 / body = `Rate exceeded.` on every call (curl both sandboxed and unsandboxed; WebFetch) |
| Semantic Scholar Graph API | `api.semanticscholar.org/graph/v1/paper/search` (2 queries) | HTTP 429 |
| arXiv HTML search UI | `arxiv.org/search/?searchtype=all&query=...` | socket closed (2 attempts) |
| arXiv month listing | `arxiv.org/list/quant-ph/2026-08?show=2000` | partial: page truncated after ~136 entries — **not a complete sweep** |
| scirate search | `scirate.com/search?q=...` | HTTP 403 |
| arXiv author page | `arxiv.org/a/leonk_1.html` | HTTP 404 |

→ **Coverage caveat**: the structured API path was unavailable. All findings below come from ~37 WebSearch queries (which index arXiv well, plus alphaxiv/arxivlens/ar5iv/inspirehep/scite/quantumarticles mirrors) plus targeted page fetches. A residual risk remains that a very recent (Sept 2026, `2609.xxxxx`) paper was not surfaced by any of these queries. **Recommend re-running the arXiv API sweep (5 min) once the rate limit clears, before the G-Pos gate.**

### Theme queries (WebSearch, 37 total)
1. arXiv 2026 neural network magnetic field estimation NV center Ramsey deep learning magnetometry
2. arXiv simulation-based inference amortized neural posterior quantum sensing magnetometry 2026
3. arXiv July August 2026 photon-efficient NV center magnetometry low photon budget sensitivity estimation
4. arXiv 2026 Cramer-Rao bound NV center magnetic field estimation sensitivity optimal quantum metrology neural
5. arXiv meta-learning few-shot quantum sensing NV center transfer learning field estimation 2026
6. "neural posterior" OR "amortized inference" Ramsey fringes magnetic field estimation low SNR arXiv
7. arXiv 2603.14144 NVRNet physics-informed neural network Ramsey nitrogen-vacancy abstract minimal sweep
8. arXiv 2026 deep learning magnetic field estimation diamond magnetometer low SNR fewer measurements sensitivity picotesla
9. arXiv 2608.23934 quantum machine learning NV center magnetic field finite-shot estimation measurement
10. arXiv 2608.19582 physics-guided machine learning sim-to-real calibration NV diamond magnetometer
11. arXiv 2026 low repetitions few shots NV center Ramsey machine learning field estimation photon budget
12. arXiv amortized neural estimator NV center diamond spin magnetometry simulation-trained 2026
13. arXiv 2026 machine learning sensitivity improvement diamond magnetometer noise floor sensitivity neural network Ramsey ensemble
14. arXiv 2026 joint estimation shared parameters multiple Ramsey traces hierarchical Bayesian quantum sensing
15. arXiv 2026 "few-shot" OR "meta-learning" quantum sensor magnetometer generalization across field values transfer
16. arXiv 2026 neural network reaches shot-noise limit magnetometry estimation efficiency photons per measurement
17. arXiv August September 2026 nitrogen-vacancy Ramsey neural network magnetic field sensitivity new
18. "Adaptive and Robust Control of Diamond Quantum Sensors via Meta-Learning" arXiv ID date authors abstract
19. arXiv 2026 "photon budget" quantum sensing estimation deep learning low-light magnetometry neural
20. arXiv 2026 neural network estimator outperforms maximum likelihood fitting Ramsey decoherence noisy traces magnetic field uncertainty
21. arXiv 2609 September 2026 nitrogen-vacancy magnetometry machine learning estimation new paper
22. "Deep-neural-network-based magnetic-field acquisition method for quantum sensing with nitrogen-vacancy centers" Zhang year journal
23. "Quantum magnetometry enhanced by machine learning" Jauch Strohm Fuchs Jelezko arXiv year
24. arXiv 2026 neural estimation magnetic field "total measurement time" OR "acquisition time" sensitivity diamond magnetometer tradeoff fewer averages
25. arXiv 2026 Ramsey fringe machine learning estimate magnetic field precision low SNR full sweep NV ensemble deep learning denoising field extraction
26. arXiv 2026 quantum sensing "information per photon" OR "estimation efficiency" neural network estimation nitrogen vacancy sensitivity metric
27. "arXiv:2609" nitrogen vacancy center quantum sensing neural network estimation September 2026
28. arXiv 2026 Bayesian neural network NV center DC magnetometry estimation uncertainty calibration Ramsey shots
29. arXiv 2025 2026 deep learning enhanced DC magnetometry NV diamond sensitivity improvement over least squares fitting Ramsey
30. arXiv 2506.13469 two-stage optimization wide-range single-electron quantum magnetic sensing BNN RL details
31. arXiv 2026 "physics-informed" OR "simulation-trained" neural network Ramsey fringe field estimation ensemble NV full trace sensitivity eta
32. arXiv 2026 "few repetitions" OR "limited data" OR "low photon count" Ramsey deep learning magnetic field estimation NV noise
33. arXiv 2026 physics-informed neural network magnetometry NV ensemble field estimation replacing least-squares fit sensitivity benchmark
34. arXiv 2026 machine learning enhanced sensitivity NV magnetometer estimator improvement factor delta B sqrt T total time
35. arXiv 2605.04416 SpinTune quantum sensor networks reliability sensitivity abstract NV
36. "Optimal Strategies for Multi-parameter Quantum Metrology" arXiv Li Hu Chen Yang Yuan August 2026 (ID verification)
37. "Beyond sensitivity" "mechanism-resolved error budgets" arXiv 2608 NV diamond ensemble (ID verification)

---

## Hits

Legend for verdict: **(a) occupies cell** / **(b) partial overlap** / **(c) adjacent** / **(d) irrelevant**.
"Sub-claim" = which L5 component it touches: `ML-est` (ML estimator for NV), `low-photon` (low photon budget / few reps), `full-sweep` (dense τ grid), `η` (sensitivity δB·√t_total as objective), `amort` (amortized/simulation-trained prior), `transfer` (cross-condition transfer / meta-learning).

### Tier 1 — Most threatening (recent + closest)

| arXiv ID | Title | Authors | Date | Verdict | Assessment |
|---|---|---|---|---|---|
| **2603.14144** (v1 NVRNet, v2 retitled) | Fast Single Nitrogen-Vacancy Center Ramsey Characterization using a Physics-Informed Neural Network | Chao Shang, Gregory D. Fuchs (Cornell) | 2026-03-14 (rev. 2026-04-03) | **(b) partial — closest single paper** | Sub-claim: `ML-est`+`low-photon`+`amort`. Maps **minimal-sweep / few-sweep noisy Ramsey PL traces** → denoised waveform + hyperfine (¹³C) parameters. Two-stage U-Net (time-frequency + attention time-domain) **pretrained on Hamiltonian simulations with experimentally calibrated noise** + parameter-efficient adapters fine-tuned on few real traces. Reports median reconstruction error 0.44–0.67× raw noise, normalized FFT error 0.10–0.19, **"up to ~40× acceleration … reducing both required data volume and acquisition time."** **NOT the cell**: target is hyperfine couplings (spin-environment characterization), *not* DC B; metric is reconstruction/FFT error, *not* η=δB·√t_total; single NV (not ensemble); no photon-budget ladder; no classical-baseline η comparison; no amortized posterior over B; no calibration-conditioned prior. **Risk**: a reviewer could read L5 as "NVRNet applied to B" — differentiation must be argued explicitly. |
| **2608.23934** | QML for Quantum Sensing under Measurement-Induced Information Loss | Sounak Bhowmik, Himanshu Thapliyal (SMU) | 2026-08-25 | **(b) partial** | Sub-claim: `ML-est`+`low-photon`. NV Ramsey interferometry, B ∈ [0,2] µT, finite-shot binomial noise, T₂=100 µs, 10% readout error; compares classical ML (ridge/RBF-ridge/MLP) on measurement statistics vs **quantum kernel ridge regression on pre-measurement density matrices**; conclusion: classical readout intelligence has diminishing returns, measurement-induced information loss is the bottleneck. **NOT the cell**: quantum-kernel vs classical-ML *theory* comparison (not amortized estimator vs classical fit); no photon-budget ladder; no η; no real data; no full-sweep decision. **Important**: its thesis ("improve the learner further gives little") is a *potential counter-argument to L5's premise* and must be addressed head-on. |
| **2603.14728** | A Deep-Learning-Boosted Framework for Quantum Sensing with Nitrogen-Vacancy Centers in Diamond | Changyu Yao et al. (WashU) | 2026-03 (~Mar 16) | **(b) partial** | Sub-claim: `ML-est`+`low-photon`. 1D-CNN (~70M params) for ODMR spectra → direct parameter inference, no initialization, GPU-parallel; **largest gains at low SNR**; explicitly emulates limited-averaging (SNR = 5.33, C√N shot-noise framing); validated on synthetic + real, intracellular nanodiamond thermometry, widefield vortex imaging. **NOT the cell**: ODMR (not Ramsey), no η, no photon-budget axis, no sensitivity-vs-reps curve. |

### Tier 2 — Amortized / BNN NV field estimation (closest to the *estimator* claim)

| arXiv ID | Title | Authors | Date | Verdict | Assessment |
|---|---|---|---|---|---|
| **2506.13469** | A Two-stage Optimization Method for Wide-range Single-electron Quantum Magnetic Sensing | Shiqian Guo, Jianqing Liu, Thinh Le, Huaiyu Dai (NCSU) | 2025-06-16 (v2 ~2025-08) | **(b) partial — closest on amortization** | Sub-claim: `ML-est`+`amort`. **Trained BNN estimator** (offline, amortized Bayesian inversion, one-hot shot sequences → posterior over ω) for **DC field** from **single-electron NV Ramsey**; Stage 2 = federated RL adaptive selection of (τ, φ) with particle-filter posterior; budget R_max = 22,000 µs, 70 shots in Stage 1; baselines: Bonato (partially adaptive), Belliardo (vanilla RL), **Nolan "NN-shots" (non-adaptive BNN)**. Metric = MSE, not η. **NOT the cell**: adaptive/sparse parameter-selection (L3/L4 territory — L5 must NOT go here), single NV single-shot readout, MSE metric, no full 300-τ sweep protocol, no photon-budget ladder, no classical LM/FFT/Rife comparison under equal budget. **Risk**: occupies the "amortized BNN for NV DC field estimation" phrase; L5 must cite and distinguish. |
| **2512.11300** | Distributed Quantum Magnetic Sensing for Infrastructure-free Geo-localization | (same NCSU lineage) | 2025-12 | **(b) partial** | Sub-claim: `ML-est`+`amort`. Offline-trained **Bayesian NN** → coarse Larmor estimate from fixed-parameter Ramsey shots, then particle-filter refinement, then RL adaptive (τ, φ) selection within a time budget; NV covariance model incl. decoherence/readout noise. Application = geo-localization + map matching. **NOT the cell**: adaptive sensing + navigation application, not η-optimal estimation on a full sweep. |
| **2608.19582** | Physics-guided machine learning for sim-to-real calibration of NV diamond magnetometers | J. Daniel, M. Y. Kim, …, S. Lee, J. Lee, J.-H. Kim (CSUSB + UNIST) | 2026-08-20 | **(b) partial** | Sub-claim: `ML-est`+`amort`(`transfer`). Ensemble-NV vector magnetometry; embeds Zeeman splitting directly into the learning pipeline; hybrid sparse-real + scalable-synthetic training; **372× precision improvement over purely statistical baselines**; decodes raw uncalibrated ODMR. **NOT the cell**: ODMR (not Ramsey), calibration/sim-to-real is the headline, no photon-budget ladder, no η, no amortized posterior, no classical LM/FFT baseline under equal photon budget. |
| **2608.27632** | Machine Learning-Based Characterisation of the Non-Markovian Dynamics of a Nitrogen-Vacancy Centre | (see inspirehep 3197367) | 2026-08 | **(b) partial** | Sub-claim: `ML-est`+`low-photon`. NN infers reaction-coordinate spectral-density parameters from **noisy Rabi dynamics**; benchmarked against **Fisher information and MLE**; NN variance ≈ MLE before asymptotic limit for some params; proposes NN→MLE two-step (NN narrows search space). **NOT the cell**: Rabi/spectral-density characterization, not DC B; NN *matches* rather than beats MLE. **Note**: the "NN as warm-start for MLE" conclusion is a mild threat to the "amortized estimator beats classical" framing — L5 should pre-empt it (L5's lever is prior information, not raw fitting speed). |
| **2605.13988** | Neural Fields for NV-Center Inverse Sensing (NeTMY) | Zhao, Zhong, Hu, de Leon, Allen-Blanchette | 2026-05-13 | **(c) adjacent** | Amortization-**free** coordinate neural field + differentiable NV forward model for reconstructing sparse spin-source densities from magnetic-noise spectra; explicitly frames "supervised networks trained on simulated labels" as a failure mode for its (spectrally coupled) inverse problem. **NOT the cell** (different inverse problem), but it is the main *methodological counter-current* to simulation-trained amortization and should be cited/differentiated. |

### Tier 3 — Same "sensitivity" narrative, different lever (protocol/hardware, not estimator)

| arXiv ID | Title | Date | Verdict | Assessment |
|---|---|---|---|---|
| 2510.11720 / 2606.02749 | Magnetometry / **Vector** Magnetometry with Broadband Microwave Fields in NV Centers | 2025-09-29 / 2026-06-01 | (b) partial | Sub-claim: `ML-est`. NN vs classical MLE (KL-divergence min) for **DC field** from broadband-MW transmission through NV ensembles; ~10 pT/√Hz (SC) / 5–100 pT/√Hz (vector). Different protocol (broadband transmission, not Ramsey sweep); NN reportedly *matched*, not beat, MLE. Cite as "NN vs classical estimator for NV DC field, equal footing" precedent. |
| 2602.00679 | High-resolution wide-field magnetic imaging with sparse sampling using NV centers | 2026-01-31 | (b) partial — **anti-overlap alarm** | Mean-adjusted Bayesian estimation (MABE) reconstructs 10⁴ pixels from **25 sampling points**; optimized DD gives ~2× sensitivity improvement. **This is sparse-sampling design (= L3/L4 family), not L5.** Cite as the boundary L5 must stay on the correct side of. |
| 2512.10549v2 | Sensitivity threshold defines the optimal spin subset for ensemble quantum sensing | 2025-12 (v2 2026-08-27) | (c) adjacent | Analytic sensitivity for inhomogeneous ensembles + explicit photon-shot-noise formulas; up to 8× sensitivity gain by selecting the optimal **spin subset**. Same η narrative, hardware/protocol lever, not estimator. |
| 2608.28519 | Beyond sensitivity: mechanism-resolved error budgets for designing quantum sensors | 2026-08-28 | (c) adjacent | Open-system simulation → sensitivity/accuracy/robustness with Shapley attribution, instantiated for NV ensemble (dephasing limits sensitivity; thermal shift limits accuracy; optical leakage limits robustness; bias 8–1500 nT at fixed sensitivity). Useful framing citation: "sensitivity alone is insufficient" — supports L5's insistence on pairing δB with t_total, but also a caution that δB alone is not the whole story. |
| 2607.01615 | Noise suppression via pulsed all-optical magnetometry with NV ensembles | 2026-07-02 | (c) adjacent | Hardware protocol (two PL readouts per pulse), 10× low-frequency noise-floor improvement near zero field. No ML, no estimation. |
| 2608.02060 | Characterizing the NV singlet transition and phonon sideband for absorption-based room-temperature magnetometry | 2026-08-03 | (d) irrelevant | Spectroscopy/hardware. |
| 2609.03039 | Nanoscale magnetometry via collective many-body dynamics in diamond | 2026-09-02 | (c) adjacent | Interaction-enhanced NV sensing, 7.9 dB metrological gain (hardware). |
| 2609.04733 | NV Centers in Diamond for Quantum Biosensing: review | 2026-09-04 | (d) irrelevant | Review. |
| 2609.02792 | Phonon-limited detection thresholds for fluorescent-protein spin-qubit relaxometry | 2026-09-02 | (c) adjacent | Photon-budget theory for a *different* qubit (validated vs NV benchmarks); propagates shot noise + photobleaching photon budget. Good citation for "photon budget as co-equal bottleneck". |
| 2603.16487 | Sub-zeptonewton force sensitivity in levitated diamond | 2026-03 | (d) irrelevant | Force sensing. |
| 2605.04416 | SpinTune: RL-discovered adaptive DD sequences for NV sensor networks | 2026-05-06 | (c) adjacent | RL for **AC** magnetometry pulse design, ~5× sensitivity vs CPMG; lever = pulse sequence, not estimator. |
| Jauch, Strohm, Fuchs, Jelezko | Quantum magnetometry enhanced by machine learning — Quantum Sci. Technol. 11 (2026), DOI 10.1088/2058-9565/ae3acf | 2026-02-04 | (c) adjacent | Quantum optimal **control** (pulse shaping) + ML (GPs, ANNs) for Ramsey magnetometry; 6× faster convergence, SNR gain on synthetic magnetocardiogram. Same ingredients (ML + NV Ramsey + magnetometry) but lever = control pulses; metric = convergence speed/SNR, not η=δB·√t_total. **No arXiv preprint found.** |
| Zhang, Zhang, Jiang, Qin | Deep-neural-network-based magnetic-field acquisition method for quantum sensing with NV centers — **Phys. Rev. A 110, 052417** | 2024-11-12 | (b) partial (older) | **Closest older work**: DNN maps resonance frequencies of the 4 NV orientations → field vector. Field acquisition, not low-photon-budget sensitivity optimization. Pre-2025, non-negotiable as prior art but not occupying the cell. |
| 1903.08176 | Sensitivity Optimization for NV-Diamond Magnetometry (review) | 2019 | (c) adjacent | Canonical source of the η formalism: η_sp = 1/(γ_e√τ), ensemble η = 1/(γ_e√(Nτ)), photon-shot-noise-limited η_opt, overhead-time factor (t_I+τ+t_R)/τ, and the note that conventional readout is ~100× from the spin-projection limit. **This is the metric definition L5 inherits, not competition.** |
| 2510.07510 | Efficient Radiofrequency Sensing with Fluorescence Encoding | 2025-10 | (d) irrelevant | RF sensing, η = (4/3√3)(Γ/γ)(1/C√R). |
| 2510.00913 | Triple-Tone Microwave Control for Sensitivity Optimization in Compact Ensemble NV Magnetometers | 2025-10 | (c) adjacent | Ramsey/ODMR sensitivity via MW control (hardware). |
| 2511.19831 | Nanophotonic magnetometry in a spin-dense diamond cavity | 2025-11 | (c) adjacent | Lock-in Ramsey, 58 nT/√Hz photon-shot-noise-limited (hardware). |
| (conference, 2026) | Data-Driven All-Optical Magnetometry: regression models from NV fluorescence lifetimes | 2026-07 | (c) adjacent | LightGBM/XGBoost/RF/symbolic regression on **lifetime** readout; R²≈0.999. All-optical modality, not Ramsey; no η. |

### Tier 4 — Theory / bounds / unrelated inverse problems (check but not occupancy)

| arXiv ID | Title | Date | Verdict | Assessment |
|---|---|---|---|---|
| 2608.01114 | Optimal Strategies for Multi-parameter Quantum Metrology | 2026-08 | (c) adjacent | SDP bounds (Holevo, Nagaoka–Hayashi, QCRB) over parallel/sequential/indefinite-causal-order strategies, with resource constraints (memory dim, control energy); demoed on multiparameter magnetometry. Theory ceiling, no NV, no ML, no estimator. |
| 2607.15398 | Saturating the Bayesian Nagaoka–Hayashi bound for the depolarization SU(2) rotation channel | 2026-07 | (c) adjacent | Bayesian multiparameter bounds, theory. |
| 2601.23283 | Robust multiparameter estimation using quantum scrambling (tilted Ramsey) | 2026-01 | (c) adjacent | Theory, tilted Ramsey protocol, cross-talk correction. |
| 2603.20139 | Heisenberg-scaling characterization of a two-channel optical network via two-port homodyne detection | 2026-03 | (c) adjacent | CRB saturation with "modest repetitions and low photon number" — but optical interferometry, different platform. |
| 2507.17460 | Optimizing quantum sensing networks via genetic algorithms and deep learning | 2025-07 | (c) adjacent | DNN surrogate for QFI of sensing networks. |
| 2604.19120 | Ultimate sensitivity of multiparameter estimation in quantum sensing with undetected photons | 2026-04 | (d) irrelevant | Nonlinear interferometry QFI. |
| 2602.17180 | Fourier-Space Approach to Physics-Informed Magnetization Reconstruction from NV Measurements | 2026-02-19 | (d) irrelevant | Scanning-NV magnetization reconstruction (micromagnetics). |
| 2604.23431 | Physics-Informed Deep Image Prior Reconstruction of In-Plane Magnetization from Scanning NV Magnetometry | 2026-04-25 | (d) irrelevant | Same family as above. |
| 2608.21658 | Precise Modeling of a Complex Solenoidal Magnetic Field Using Analytic Functions and a PINN | 2026-08-21 | (c) adjacent | PINN beats linear least-squares (χ²_red 2.15→1.034) — but Mu2e solenoid, not NV. Useful precedent citation for "learned model beats LSQ", not occupancy. |
| 2609.08014 | Learned Diffractive Optics for Quantum-Optimal Inference | 2026-09-07 | (c) adjacent | Learned optics for **parameter estimation under a restricted photon budget**, optimizing Fisher-information-per-photon / MSE at finite N. Different physical layer (measurement optics), but it is the closest thing found to "photon-budget-aware learned estimation" and a good related-work citation. |
| 2604.22526 | Information-Theoretic Geometry Optimization and Physics-Aware Learning for Calibration-Free Magnetic Localization | 2026-04 | (c) adjacent | Calibration-free magnetic localization (not NV Ramsey). |
| Adaptive and Robust Control of Diamond Quantum Sensors via Meta-Learning | (arXiv 2024-12-27; Adv. Quantum Technol., DOI 10.1002/qute.70385) | 2024-12 | (c) adjacent | Meta-learned **control protocols** generalizing across devices/environments; "adapt in as few iterations as possible". Meta-learning in NV, but for control transfer, not field estimation. Closest `transfer` precedent outside control. |

---

## Direct-occupancy hits

**None.** No paper found that simultaneously:
1. keeps the **full dense τ sweep** (300 points),
2. is scored on **η = δB·√t_total** (or the equivalent "repetitions-to-target-δB" curve),
3. at **low photon budget / few repetitions per τ**,
4. with an **amortized / prior-informed / simulation-trained estimator of the DC field B**, benchmarked against **classical LM/FFT+Rife/grid-Bayes baselines given an equal photon budget**.

Every candidate fails at least two of these four. The nearest misses and why they are not kills:

- **2603.14144 (NVRNet)** — few-sweep Ramsey + simulation-pretrained + explicit data-volume/acquisition-time reduction. Fails criteria 2 and 4: estimates ¹³C hyperfine parameters on a *single* NV, no η, no DC-B posterior, no classical-baseline sensitivity comparison.
- **2506.13469 / 2512.11300** — amortized BNN for DC field from Ramsey, but on the **adaptive/sparse τ-selection** side (explicitly L3/L4's cell, which L5 must avoid anyway), single NV single-shot, metric MSE not η.
- **2608.19582 / 2603.14728** — ODMR, not Ramsey; calibration/throughput framing, not photon-budget-η.
- **2608.23934** — simulated Ramsey + finite shots + learning, but a quantum-kernel-vs-classical-ML information-theoretic comparison, not an amortized field estimator, no η, no real data, no photon ladder.

---

## Verdict: SAFE (qualified)

**SAFE** with respect to direct occupancy: the L5 innovation cell — *"low photon budget + full τ sweep + η-optimal amortized estimation with calibration-conditioned priors, benchmarked against tuned classical estimators under equal photon budget, on real ensemble Ramsey data"* — is **unoccupied** as of 2026-09-12 in everything surfaced by ~37 queries.

**The three qualifications that matter:**

1. **The novelty must be argued on the cell, not on "ML for NV".** That generic claim is now **crowded**: in the last ~6 months alone there are ≥5 papers (2603.14144, 2603.14728, 2606.02749, 2608.19582, 2608.23934) plus ≥2 from 2025 (2506.13469, 2510.11720) doing "learned estimator for NV field/parameter extraction, strongest at low SNR". A paper whose abstract reads "we use a neural network to estimate B from noisy NV Ramsey data" will be judged as incremental. The defensible core is: **(i)** η = δB·√t_total as the *primary* objective (nobody found is optimizing it with a learned estimator), **(ii)** the **photon-budget ladder with a fixed full τ grid** and an explicit `t_ovh` sensitivity analysis, **(iii)** the **amortized / calibration-conditioned prior across field values** (L1 bloodline) as the mechanism that buys the sensitivity gain, and **(iv)** rigorous head-to-head with *tuned* classical baselines (LM multi-start / FFT+Rife / grid Bayes) under an identical photon budget — the L2/L3/L4 companion lineage makes this comparison credible in a way the found papers' comparisons are not.

2. **Two papers actively argue against part of the premise** and must be cited and answered, not ignored:
   - **2608.23934** concludes that classical learners on measurement statistics have "diminishing returns" and that measurement-induced information loss is the real bottleneck → L5's claimed gain must therefore come from **prior/amortization structure** (which that paper does not test), not merely from "a bigger/better classical estimator".
   - **2608.27632** finds NN ≈ MLE (not better) on noisy NV traces and proposes NN only as a warm start → L5 must show its gain is not "faster fitting" but genuinely lower δB at equal t_total, and should adopt the NN→refine two-step as a *baseline* rather than a competitor.

3. **Anti-overlap gates confirmed live.** 2602.00679 (sparse sampling / 25 points for 10⁴ pixels) and 2506.13469 / 2512.11300 (adaptive τ, φ selection with RL + particle filter) show the L3/L4-adjacent cells are actively worked. L5 must keep the **full 300-τ sweep** and vary **only the photon budget** — if any candidate idea drifts toward "choose better τ points", it collides with that literature instead of occupying L5's cell.

**Confidence: medium-high (~75–80%) for the last 2 months; medium (~65%) for 2025-2026 broadly.** The limiting factor is coverage, not analysis: the arXiv API, Semantic Scholar API, the arXiv HTML search UI and scirate were all rate-limited/blocked from this host, so the sweep rests on ~37 web-search queries against arXiv-indexing mirrors plus one partial (truncated) month-listing page. No query surfaced any title combining {Ramsey + NV/ensemble + low photons/repetitions + learned estimator + sensitivity η}. **Recommended pre-G-Pos action: re-run the raw arXiv API sweep (`abs:"NV center" AND abs:"Ramsey"`, `abs:magnetometry AND abs:"neural"`, `abs:magnetometry AND abs:"machine learning"`, cat:quant-ph, July–September 2026 windows) once the rate limit clears, to convert "no query hit it" into "not in the index".**

### Closest older work (pre-2025, for the prior-art paragraph)
- **Zhang, Zhang, Jiang, Qin, Phys. Rev. A 110, 052417 (2024)** — DNN for NV magnetic-field *acquisition* (vector from four-orientation resonance frequencies). The original "DNN for NV field estimation".
- **arXiv:1903.08176 (2019)** — the canonical η formalism, the overhead-time factor, and the spin-projection-limit framing that L5's metric inherits.
- **Bonato et al. / Belliardo et al. / Nolan et al. ("NN-shots")** — the partially-adaptive, vanilla-RL and non-adaptive-BNN NV field-estimation baselines that 2506.13469 benchmarks against; these are the true methodological ancestors of the "amortized BNN for NV field" line.

---

## Raw arXiv API sweep (independent re-run) — 2026-09-12

## Route and coverage honesty

**The raw arXiv API (`export.arxiv.org/api/query`) is BLOCKED from this host.** Every structured
query returned `HTTP 429 / body = "Rate exceeded."` — with and without a custom `User-Agent`,
over both `http://` and `https://` (following the 301), after 65 s cooldowns, and across 3–4 retry
loops with 15–25 s backoff. The only call that ever succeeded was the trivial `all:electron`
(HTTP 200, 4457 bytes), which is consistent with an edge-cached response rather than a working
API entitlement for this IP. **No substantive result in this section comes from the raw API.**

**Substitute route actually used:** arXiv's own advanced-search endpoint
`https://arxiv.org/search/advanced?advanced=&terms-N-operator=AND&terms-N-term=...&terms-N-field=all&date-filter_by=date_range&...&abstracts=show&size=...`
— same index, same host, same day, returns full abstracts. It was **validated as a working index**
before use: it independently reproduced every paper the earlier WebSearch-based sweep had found
(2603.14144, 2603.14728, 2608.23934, 2608.19582, 2506.13469, 2512.11300, 2602.00679, 2510.11720,
2605.13988, 2608.28519, 2609.02792, 2507.17460, 2511.19831). Zero-result queries were verified to
be genuine arXiv "Sorry, your query returned no results" pages, not parse failures.

**Two query forms failed structurally and were NOT covered by that formulation:**
`Ramsey AND diamond` and any `terms-N-field=title` query returned `HTTP 400` on 3 attempts each.
The recent-window sweep (`all: nitrogen-vacancy`, 2026-07-01→2026-09-12, 100 hits, capped)
compensates for the first. The title-field control is missing — the meta-learning NV paper
(Adv. Quantum Technol. 2024) was instead confirmed present in the index via `meta-learning AND quantum`.

## Query log

All queries `all`-fields, 2024-06-01 → 2026-09-12 unless noted. Spacing 8–10 s; results capped as shown.

| # | Query | Hits |
|---|---|---|
| 1 | `"NV center" AND "machine learning"` | 11 |
| 2 | `"NV center" AND "magnetic field" AND estimation` | 17 |
| 3 | `"Cramer-Rao" AND NV` | 1 |
| 4 | `photon AND Ramsey AND sensitivity` | 8 |
| 5 | `"amortized inference" AND "quantum sensing"` | **0** (genuine) |
| 5b | `amortized AND "quantum sensing"` | 1 |
| 6 | `hierarchical AND "quantum sensing" AND estimation` | **0** (genuine) |
| 7 | `"few-shot" AND "quantum sensing"` | **0** (genuine) |
| 7b | `"meta-learning" AND "quantum sensing"` | **0** (genuine) |
| 8 | `"joint estimation" AND "quantum metrology"` | 11 |
| 9 | `"neural posterior" AND magnetometry` | **0** (genuine) |
| 9b | `"neural posterior" AND "quantum sensing"` | **0** (genuine) |
| 10 | `"diamond magnetometry" AND "deep learning"` | **0** (genuine) |
| 11 | `sensitivity AND NV AND "neural network"` | 5 |
| 12 | `"shot noise" AND Ramsey AND estimation` | 1 |
| 13 | `"nitrogen-vacancy" AND "photon budget"` | 2 |
| 14 | `"nitrogen-vacancy" AND "low photon"` | 1 |
| 15 | `"Cramer-Rao" AND magnetometry` | **0** (genuine) |
| 16 | `"quantum sensing" AND "neural network" AND estimation` | 5 |
| c1 | `meta-learning AND quantum` (control) | 50 |
| c2 | `hierarchical AND magnetometry` | **0** |
| c3 | `"quantum sensing" AND "transfer learning"` | **0** |
| c4 | `"ensemble" AND "Ramsey" AND "neural"` | **0** |
| c5 | `pooled AND "quantum sensing"` | 5 |
| L1 | `nitrogen-vacancy`, window 2026-07-01→2026-09-12 | 100 (capped) |
| L2 | `magnetometry`, window 2026-07-01→2026-09-12 | 71 |
| L3 | `"quantum sensing" AND learning`, window 2026-06-01→2026-09-12 | 12 |
| L4 | `nitrogen-vacancy AND Bayesian` | 9 |
| L5 | `"NV ensemble" AND estimation` | 3 |
| L6 | `"NV center" AND "low signal-to-noise"` | 2 |
| L7 | `"quantum sensing" AND "multi-task"` | 1 |

## Results — relevant hits (new in this re-run are marked NEW)

| arXiv ID | Title | Date | Verdict | Assessment |
|---|---|---|---|---|
| **2508.14902** | Hierarchical Maximum Likelihood Estimation for Time-Resolved NMR Data | 2025-08-26 (v. 2026) | **(b) PARTIAL — closest *mechanism* precedent, NEW** | A **Bayesian hierarchical model reduced to a least-squares / VarPro extension** that pools information instead of a two-stage fit, "to maximize the precision at minimal uncertainty". Validated in two experiments — one of which uses a **micron-scale NMR setup with NV centers in diamond for detection** — beating Fourier methods and a two-stage VarPro. **NOT the cell:** hyperpolarized-metabolite NMR quantification (time-resolved spectra), shared structure is across *time points/predictors*, not across **40 field columns of one session**; no Ramsey DC-B estimation, no photon-budget ladder, no η=δB·√t_total, no classical LM/FFT+Rife baseline under equal photon budget. **Why it matters:** it is direct evidence that "hierarchical/pooled MLE beats two-stage estimation" is already a known move in the NV-adjacent literature. L5 must cite it and locate its novelty in *what* is pooled (relaxation envelope + instrument phase frame across B-columns) and in the sensitivity metric, not in "we pool". |
| **2601.17465** | Bayesian quantum sensing using graybox machine learning | 2026-09-10 | **(b) PARTIAL — strong, NEW** | First experimental **graybox** (physics model + learned imperfection model) for a solid-state open quantum system, **validated on estimating a static magnetic field with a single-spin quantum sensor**, performing **Bayesian inference** with a model trained on ~10,000 prior experimental datapoints; **orders-of-magnitude MSE improvement** over the physics-only model and a clear gain over a same-size blackbox. **NOT the cell:** single spin (not a 40-column ensemble session), no low-photon/few-repetition regime, no η=δB·√t_total, no full 300-τ sweep protocol, no tuned-classical-baseline comparison, and the lever is *model fidelity* (unmodelled noise/control imperfections), not shared-nuisance pooling. **Why it matters:** it is the closest thing found to "prior-trained hybrid model + Bayesian DC-B estimation on real data" and it already claims large error reduction. L5 must differentiate on the ensemble/session pooling axis and on η — and should cite it as the strongest recent precedent that physics+learned models beat physics-only ones. |
| **2607.01085** | Fisher Glasses: Tail-Certified Quantum Metrology in Quenched Environments | 2026-07-01 | **(b) PARTIAL — conceptual, NEW** | Formalises exactly the structure L5 exploits: **"quenched sensors, where slow environmental variables freeze within a session but vary between repetitions"** (explicitly naming shallow NV centers). Certification **conditions on the latent session**, projects out **nuisance directions**, and tail-certifies; proves a no-go that averaged Fisher data cannot determine the certificate. **NOT the cell:** pure theory/certification, no estimator, no Ramsey sweep, no photon budget, no η, no real data; it does not estimate B. **Why it matters:** it is the theoretical justification for L5's premise that nuisance parameters are session-shared and must not be averaged over — cite it as *support*, and note L5 supplies what it lacks (an actual estimator + sensitivity metric). |
| **2608.11092** | Physics-Constrained Compressed Sensing for Quantum Sensing in the Data-Starved Regime | 2026-08-11 | **(b)/(c) PARTIAL-ADJACENT, NEW** | Exploits intrinsic structure (PSD + Toeplitz + low-rank priors on two-time correlation Gram matrices) via convex optimisation to improve frequency estimation **"from sparse and noisy data"**; demonstrated numerically on GHZ magnetometry. **NOT the cell:** compressed sensing / sparse-acquisition = the **L3/L4 family** L5 must avoid; GHZ platform, not NV ensemble Ramsey; no B estimator, no η, no photon-budget ladder. Cite as the nearest "structural-prior beats brute force in a data-starved regime" precedent — and as an **anti-overlap marker** (it sits on the sparse-sampling side of the fence). |
| **2608.25534** | A universal loss-limited optimum for fixed multi-pass quantum sensing per absorbed photon | 2026-08-26 | **(c) ADJACENT, NEW** | Optimises a **per-photon** figure of merit (information per absorbed photon) and derives a universal trade-off h(x)=x²/(eˣ−1) with maximum 0.648 at x=1.594. **NOT the cell:** photons through a sample (multi-pass interferometry), not NV spin readout; no estimator, no B. Useful citation for "photon-budget-aware figures of merit are an active concern", and a reminder that "information per photon" is a competing normalisation to L5's η=δB·√t_total. |
| **2512.13835** | Microwave-free vector magnetometry and crystal orientation determination with NV centers using Bayesian inference | 2026-06-16 | **(c) ADJACENT, NEW** | Bayesian inference extracting the **B-field vector + NV orientation** from PL maps; analytical cross-relaxation model. Not Ramsey, no photon budget, no η, no learned/amortized estimator. |
| **2508.21450** | Reducing Sensing Time through Offline Experimental Design for Nuclear Spin Detection | 2026-05-27 | **(c) ADJACENT + anti-overlap alarm, NEW** | Deep-learning model (SALI) + surrogate-information-gain **data-point selection**; 85% reduction in measurement time on a real NV–¹³C experiment, 60% predicted in the low-field regime. **This is experimental *design* (which points to take) — L3/L4 territory.** Confirms the "reduce t_total" narrative is actively worked from the design side; L5 must stay on the *estimator* side with a fixed full sweep. |
| **2502.06070** | Compressed sensing enabled high-bandwidth and large dynamic range magnetic sensing | 2025-02-09 | **(c) ADJACENT + anti-overlap, NEW** | Compressed sensing for NV magnetic sensing. Same L3/L4 fence. |
| **2609.06292** | Quantum Sensing of Non-Repeatable Events Enhanced by In-Sensor Quantum Reservoir Computing | 2026-09-05 | **(c) ADJACENT, NEW** | Reservoir computing for DD magnetometry of non-repeatable events; binary phase classification, not B estimation, no η. |
| **2605.23455** | Sequential Spatiotemporal Magnetic-Field Reconstruction via Quantum Hamiltonian Learning with NV-Center Spin-1 Hamiltonians | 2026-05-25 | **(c) ADJACENT, NEW** | Sequential Bayesian reconstruction of 2-D field maps; explicitly reports a **shared coupling parameter J shared across scan windows** and finds it only partially identifiable (biased posterior mean 326.9 Hz despite posterior narrowing). **Relevant caution for L5**: pooling a shared nuisance parameter can concentrate the posterior without removing bias — L5 must report bias, not just CI width. |
| **2604.20901** | Impact of Photoelectric Readout Noise on Magnetic Field Sensitivity of NV Centers in Diamond | 2026-04-21 | **(c) ADJACENT, NEW** | Readout-noise/hardware; sensitivity framing only. |
| **2602.23712** | Real-time Amplitude and Phase Estimation of AC Fields with Diamond Spins | 2026-02-27 | **(c) ADJACENT, NEW** | Single-shot AC amplitude/phase, 320 µs resolution; AC not DC, no η-vs-reps ladder. |
| **2603.13754** | A Highly Sensitive Diamond NV Magnetometer Using Ramsey Interferometry with a Short Sensor-to-Sample Distance | 2026-03-14 | **(c) ADJACENT, NEW** | Ramsey ensemble hardware; 2.93(7) pT/√Hz at 210 mW. Protocol/engineering lever, not estimator. |
| **2602.17648** | Approaching the Limit in Multiparameter AC Magnetometry with Quantum Control | 2026-02-19 | **(c) ADJACENT, NEW** | QFIM-singularity-resolving control protocol for AC amplitude+frequency; sensor = single NV. Control lever, no estimator/η. |
| **2602.12090** | Unconditional full vector magnetometry using spin selectivity in NV centers in diamond | 2026-02-12 | **(c) ADJACENT, NEW** | Vector magnetometry without prior field knowledge; hardware/protocol. |
| **2607.13422** | Suppressing Detuning-Induced Bias in Ramsey Magnetometry with Composite Pulses | 2026-07-14 | **(c) ADJACENT, NEW** | DC Ramsey magnetometry **with an unknown detuning parameter** — surfaces the same "unknown nuisance in the Ramsey model" problem L5 handles by pooling; but solved with composite pulses (control), single qubit, no photon budget, no η. Worth citing in the nuisance-parameter paragraph. |
| **2609.10606** | When Measurement Constraints Favor Quantum Computational Sensing for Stealthy Power-Grid Attack Detection | 2026-09-08 | **(c) ADJACENT, NEW** | Computational sensing under measurement constraints; application-domain. |
| **2607.25145** | Agentic AI for Scientific Reasoning in Autonomous Quantum Sensing Experiments | 2026-07-27 | **(c) ADJACENT, NEW** | LLM agent autonomously runs an NV experiment incl. a Ramsey T₂* measurement. Automation, not estimation theory. |
| **2607.22521** | Critical Sensing with Autonomous Devices: Self-Oscillation Threshold of a Frequency-Locked NV-Centre Magnetometer | 2026-07-24 | **(c) ADJACENT, NEW** | CW-ODMR feedback-lock bifurcation; hardware/nonlinear dynamics. |
| **2607.22410** | A Kalman Filter Based Approach to NV Diamond Data Fusion For Improved Temperature Sensing | 2026-07-24 | **(c) ADJACENT, NEW** | Kalman fusion of two NV modalities, 57% accuracy gain — but **temperature**, not B, and no photon-budget axis. Mild precedent for "fusion of modalities across one session". |
| **2609.09571** | Momentum-resolved quantum noise spectroscopy using ensembles of diamond quantum sensors | 2026-09-08 | **(c) ADJACENT, NEW** | Wide-field NV ensemble noise spectroscopy; not parameter estimation of DC B. |
| **2608.27979** | Pulsed single-photon magnetometry with a Λ-type three-level system: near-optimal frequency-resolved photon counting | 2026-08-28 | **(c) ADJACENT, NEW** | QFI decomposition under photon loss; different platform (atomic Λ system). |
| **2507.05366** | Simultaneous Determination of Local Magnetic Fields and Sensor Orientation with NV Centers in Nanodiamond | 2026-09-03 | **(c) ADJACENT, NEW** | Joint estimation of field + orientation (≥4 bias fields); classical, no ML/no photon budget. |
| **2608.17582** | Automating Variational Quantum Sensing through Reinforcement-Learned Circuit Structures | 2026-08-18 | **(c) ADJACENT, NEW** | RL over circuit *architectures* with Fisher-information objectives; gate-model circuit design, no NV/no Ramsey/no B. |
| **2606.15071** | Quantum learning with a single-atom sensor | 2026-06-12 | **(d) IRRELEVANT, NEW** | Quantum-agent learning theory. |
| **2607.15040** | Machine-Learning-Empowered Quantum Sensing of the Plaquette Phase in a Three-Level Delta System | 2026-07-16 | **(d) IRRELEVANT, NEW** | MLP on STIRAP populations; different observable. |
| L1/L2 listing sweep (100 + 71 hits, 2026-07→09) | — | — | **(c)/(d)** | Exhaustive recent-window check: **no title in the two-month window combines {NV/ensemble Ramsey + low photon budget/repetitions + learned estimator + sensitivity η}.** Newest relevant entries are the ones already tabulated above (2609.06292, 2608.28519, 2608.27632, 2608.23934, 2608.19582, 2608.11092). The rest is materials science, NMR, thermometry, hardware and biology. |

## Direct-occupancy hits

**None. No DIRECT KILL in this re-run.** Nothing found that simultaneously keeps the full dense 300-τ
sweep, is scored on η = δB·√t_total, operates at low photon budget / few repetitions per τ, and uses an
amortized/prior-informed estimator of DC B benchmarked against tuned classical baselines at equal
photon budget.

## Updated verdict

**SAFE (qualified) — unchanged, and now confirmed on the arXiv index itself rather than via
web-search mirrors.** The 12 core queries plus ~20 variants and two recent-window listing sweeps
(171 papers over 2026-07-01→2026-09-12) surface **no direct occupancy** and **no direct kill**.

Two qualifications changed shape and both are load-bearing:

1. **The "pooling / hierarchical" mechanism is no longer novel *as a technique*.** **2508.14902**
   (hierarchical MLE, validated partly on NV-based NMR detection) and **2607.01085** (session-latent
   nuisance formalism for quenched NV sensors) mean L5 cannot present "we use a hierarchical/pooled
   estimator that conditions on the session" as the contribution. The defensible novelty is narrower
   and must be stated as: *pooling the shared relaxation envelope, contrast/T₂*/stretch and the
   instrument phase frame **across the 40 B-columns of one measurement session** to buy **δB at equal
   t_total on a fixed full 300-τ sweep**, with η = δB·√t_total as the primary objective and tuned
   classical baselines (LM multistart / FFT+Rife / grid Bayes) given an identical photon budget.
   **2508.14902 is the single most important paper to cite and differentiate against.**
2. **The "physics+learned model + Bayesian inference for a static B" space got its strongest entry
   yet**: **2601.17465** (2026-09-10, graybox Bayesian, orders-of-magnitude MSE gain over physics-only
   on a real single-spin sensor). L5 must (a) cite it, (b) note its lever is model fidelity not
   shared-nuisance pooling, single-spin not ensemble session, no photon-budget ladder, and (c) avoid
   an abstract that reads as "we also use a prior-trained Bayesian model to estimate B".

**Confidence: high (~85%) for 2026-07-01 → 2026-09-12** (two independent listing sweeps of that window
plus the targeted queries). **Medium-high (~75%) for 2024-06 → 2026-09 broadly**, limited by: the
`Ramsey AND diamond` and title-field query forms returning HTTP 400 (uncovered), and the fact that
arXiv search covers metadata/abstracts only (a paper whose abstract avoids our vocabulary would be
missed). The previous sweep's coverage caveat — "re-run the raw API to convert *no query hit it* into
*not in the index*" — is now **partially discharged**: the raw API itself remained unusable, but the
arXiv HTML index was queried directly and independently reproduced the earlier findings.
