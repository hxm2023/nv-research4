# Field Conventions — NV-Center Ramsey Magnetometry (writing, plotting, units, review)

Knowledge-base note for NV×AI Line #5. Compiled 2026-09-12 from web/literature search.
Citations below were seen in search results; items I could not source are explicitly
flagged **[UNSOURCED]**.

---

## Plot Types

### 1. Ramsey fringe (`signal` vs `τ`)

- The canonical figure. Fluorescence (normalized 0–1, or raw kcounts) vs free-evolution
  time τ, with the fit overlay `C + A e^{−(τ/T₂*)^p} cos(2πfτ + φ)`.
- Conventions: τ in **ns** for single NV / nanodiamond, **µs** for bulk ensemble; error bars
  = 1σ from photon statistics; an inset or lower panel often shows **residuals**.
- Fitting practice seen in the literature: contrast `C` and phase shift `φ` are extracted
  from the fringe fit; **asymmetric error bars** on contrast are frequently reported as a
  68.27 % (1σ-equivalent) confidence interval; decay envelopes are then fit separately by
  **least-squares weighted by symmetrized error bars** (Univ. Innsbruck master thesis,
  uibk.ac.at, "Ramsey fringes are fitted with the function … returning the fringe contrast C
  and a phase shift φ").
- Typical NV scale anchors from search: T₂*-limited Ramsey with T₂* of a few µs for
  as-grown diamond (thesis chapter / AI-Terakoya NV chapter); T₂* ≈ 0.27(4) ms quoted for a
  dense-NV cavity device (arXiv:2511.19831).

### 2. Decay envelope fits

- Contrast vs τ with exponential (p = 1) or Gaussian (p = 2) model. The exponent must be
  stated; `p = 2` is the Gaussian-dephasing convention used for inhomogeneous T₂*.
- Watch: `T₂*` from a Gaussian fit is **not** comparable to `T₂*` from an exponential fit.
  Innsbruck thesis example: 3.9(3) ms (Gaussian) vs 54(8) ms (exponential) on the same
  qubit — a factor 14 difference from the model choice alone.

### 3. Error- vs-repetitions curves (log-log)

- x = repetitions `r` or total measurement time `t_total`; y = δB (or σ_B).
- Expected slope **−1/2** (white/shot noise). Deviations are the signal:
  - Flat/flattening at long τ ⇒ **drift-limited**. Example: compact integrated NV sensor,
    B_min ∝ 1/√τ for τ ≤ 1 ms then **flattening for τ > 1 ms** (arXiv listing family for
    compact integrated NV magnetometers).
  - Slope steeper than −1/2 ⇒ averaging is doing something unusual (or you are averaging
    away a coherent systematic — a red flag).
- Report the fitted slope; a slope that is not −1/2 must be explained physically.

### 4. Sensitivity curves `η(reps)` or `η(T_total)`

- L5's headline plot. y = η = δB·√t_total in nT/√Hz; x = repetition level (5k → 640k) or
  t_total. Since η is designed to be flat for a shot-noise-limited estimator, **the
  interesting content is: (i) the plateau level, (ii) the low-rep regime where estimators
  diverge from each other, (iii) the onset of flattening/drift.**
- Companion plot: **reps-to-target-precision δB\*** (bar chart or step curve) — this is the
  operational low-photon-budget statement audiences actually understand.
- Device-paper analogue: sensitivity spectrum from `noise_PSD(f)/slope`, median quoted
  (protocol in arXiv:2305.06269).

### 5. Allan deviation plots

- Standard for every NV device paper claiming a noise floor. `σ_A(τ)` vs averaging time τ on
  log-log; read off the **minimum detectable field** and its averaging time, plus the τ^{-1/2}
  (white) → flat/rising (flicker/random-walk/drift) transition.
- Real anchors found in search:
  - Wolf et al., *Phys. Rev. X* **5**, 041001 (2015): 0.9 pT/√Hz, ~100 fT in 100 s — **but
    Erratum PRX 13, 029903 (2023)**: the shot-noise level estimate (Eq. 3) and the Allan
    deviation calculation were wrong; corrected to **9 pT/√Hz** and ~900 fT in 100 s.
  - Compact & stable diamond sensor ((111) ¹²C-enriched CVD): 44 pT/Hz^0.5 noise floor,
    28 pT/Hz^0.5 shot-noise-limited, **Allan minimum 1.2 pT at ~1000 s**
    (DOI 10.1002/qute.202300456).
  - Compact integrated NV sensor: shot-noise limit ≈ 3 nT/√Hz, but Allan gives
    B_min(τ ≈ 1 ms) ≈ 1 µT ⇒ **31 nT/√Hz** — an order of magnitude above the shot-noise
    limit. This gap is the whole reason the Allan plot exists.
  - Chip-scale Ramsey sensor: 150 nT/√Hz, white-noise τ^{−1/2} up to ~0.1 s, best resolution
    near 0.2 s.
  - Tabletop NV current sensor: ~2.3 nT/√Hz floor vs 585 pT/√Hz shot-noise estimate; Allan
    shows flicker at low current, random walk at high current.
  - NV current comparator: Allan minimum 5e-7 A·turns at 67 Hz; DC ratio Allan 50 nA
    (*Sci. Rep.* s41598-026-58868-2).
- **Journal association (observed):** Allan deviation is near-mandatory in *PRApplied*,
  *PRX*, *Adv. Quantum Technol.*, *Sci. Rep.* device papers; rare in *PRL* theory letters.

### 6. Posterior / uncertainty plots

- Bayesian NV papers show the posterior (histogram / particle cloud / credible band) rather
  than a single error bar; error propagation is then a first-class claim.
- Precedent: Hincks et al., arXiv:1705.10897, *N. J. Phys.* **20**, 013022 (2018) — fully
  Bayesian quantum Hamiltonian learning cross-validated on real NV data vs weighted least
  squares.
- Particle-filter posteriors appear in adaptive protocols (arXiv:2312.16985; arXiv:2506.13469).
- For amortized/NN posteriors, the accompanying diagnostic plot should be **expected coverage
  / SBC rank histogram / TARP** (Talts et al. arXiv:1804.06788; Deistler et al.
  arXiv:2210.04815; Lemos et al. 2023; `sbi.diagnostics`).

### 7. CRLB vs achieved error

- Plot either `achieved σ_B / CRLB(B)` vs repetition level, or both curves on one log-log axis.
- Experimental precedent: npj Quantum Information (2022), DOI 10.1038/s41534-022-00547-x,
  "Quantum Fisher information measurement and verification of the quantum Cramér–Rao bound in
  a solid-state qubit" — the estimator is shown to saturate the quantum CRB.
- Theory precedent: SciPost Phys. **17**, 004 — full Fisher-information treatment with
  sensitivity `η = e^{x(T)}/|φ(T,b)/b| · √T`.
- Baseline-comparison precedent: Belliardo et al. (arXiv:2312.16985 / *Quantum* **8**, 1555,
  2024) report sensor precision alongside the CRB via Fisher information.

### 8. Heatmaps over (B, τ) or (B, rep)

- **[UNSOURCED as a literature convention.]** Heatmaps in the NV literature are overwhelmingly
  **spatial** (widefield magnetic images — e.g. the vortex imaging in arXiv:2603.14728; NV
  vector magnetic images in arXiv:2407.14553) or **(B, MW frequency)** ODMR maps.
- Recommendation for L5: a (B, τ) or (B, rep) heatmap of `σ_B̂` or of the failure indicator
  is a *legitimate and probably under-used* way to expose where an estimator breaks — but treat
  it as your own contribution to the plotting vocabulary, not an inherited convention.

### Journal ↔ figure culture (observed, use as a guide not a rule)

| Journal class | Typical figure set | Length/shape |
|---|---|---|
| *Rev. Mod. Phys.* (review) | 30+ figures; 36 figures for Barry et al. 2020 (arXiv:1903.08176) | 73 pages, encyclopedic |
| *PRX* | Sensitivity + Allan + device schematic; ~6–10 figures | full article |
| *PRApplied* | Device schematic, Ramsey/echo fringes, noise spectrum, Allan deviation, comparison table | full article; **100-word justification of fit to PRApplied required**; Data Availability Statement mandatory |
| *PRA* / *PRL* | Fringes + theory curves; PRL letters 3–5 figures | PRL ≤ 3,750 words OR ~4 pages; PRA Letters up to 5 pages |
| *Optics Letters* | 2–4 compact multi-panel figures | **4 printed pages**; abbreviated reference style (no article titles, first 3 authors + *et al.*); Data Availability Statement required |
| *npj Quantum Information* / *Sci. Rep.* | Flexible; heavier on diagnostics | open access |

---

## Notation Conventions

### Symbol table

| Symbol | Meaning | Typical unit |
|---|---|---|
| `γ` (or `γ_e/2π`) | Electron gyromagnetic ratio. **γ_e/2π = 28.0249 GHz/T = 2.8025 MHz/G = 28.025 Hz/nT = 28.025 MHz/mT** | Hz/nT, MHz/G, or rad/(s·T) |
| `τ` (also `t`, `T`) | Free-evolution time of the Ramsey sequence | ns (single NV), µs (ensemble) |
| `T₂*` | Inhomogeneous dephasing time (Ramsey envelope) | ns–ms |
| `T₂` (or `T₂^echo`) | Homogeneous coherence time (Hahn echo / DD) | µs–ms |
| `p` / `m` | Decay exponent: p = 1 exponential, **p = 2 Gaussian** (field convention) | — |
| `C` (contrast) | Fringe contrast = (S_max − S_min)/(S_max + S_min); readout contrast | dimensionless (often reported in %) |
| `A` | Fringe amplitude | counts or normalized |
| `C₀`/`C̄` | Baseline/offset constant in the fit | counts |
| `φ` | Accumulated phase | rad |
| `B` | Magnetic field; `B_∥` = component along the NV axis | nT, µT, T |
| `σ` | Per-point noise std (photon shot noise) | normalized units or counts |
| `σ_R` | Readout factor above the spin-projection limit, `√(1 + 2(α₀+α₁)/(α₀−α₁)²) ≥ 1` | dimensionless |
| `η` | Sensitivity = δB·√t_total | nT/√Hz (or pT/√Hz, fT/√Hz) |
| `δB` | Field estimation uncertainty (posterior std / RMSE) | nT |
| `N` / `r` / `N_reps` | Number of repetitions (measurement cycles) | integer |
| `R̄`, `R₀` | Photon detection rate | counts/s |
| `𝒩` / `n_avg` | Average photons collected per measurement | counts |
| `t_ovh`, `t_d`, `t_m` | Per-point overhead / dead time (init + readout) | ns–µs |
| `Δν`, `Γ` | ODMR linewidth (FWHM), linewidth | Hz |
| `Δf` | Measurement bandwidth | Hz |
| `T_total` / `t_total` | Total accumulation time of the data used for one estimate | s |

### The two unit systems

**System A — SI / rad-based (`rad s⁻¹ T⁻¹`).** `ω = γ_e B` with
`γ_e = 1.7608597e11 rad s⁻¹ T⁻¹ = 2π × 28.0249 GHz/T`.
Preferred by quantum-metrology theory papers (RMP, PRX, SciPost).

**System B — "laboratory" / cycle-based (`Hz nT⁻¹`, `MHz G⁻¹`).**
`f = (γ_e/2π) B` with `γ_e/2π = 28.0249 GHz/T = 28.025 MHz/mT = 28.025 Hz/nT
= 2.8025 MHz/G` (1 T = 10⁴ G).
Preferred by experimental NV magnetometry.

**This project's convention (locked in CLAUDE.md):**
`γ = 2π × 28e-6 rad/(µs·nT)` ⇒ `f [Hz] = 28.025 · B [nT]` for the aligned NV axis, and
`δB [nT] = δf [Hz] / 28.025`. Units: `B` in nT, `τ` in ns (written `20n ns`), Gaussian decay,
`τ_off ≈ 18.6 ± 2.6 ns` correction (cite L1's `confirm_tau_off`, do not re-derive).

### Unit-trap checklist (has bitten this family of projects before)

1. `γ` vs `γ/2π` — a factor 6.28 in the field. Always state which.
2. **Hz vs rad/s** in the fitted frequency — and therefore in δB.
3. **µs vs ns** in τ, and therefore in `t_total` (a 1000× error in η).
4. **T vs mT vs G vs nT**; `MHz/G` vs `Hz/nT` are numerically ≈ 2.8 vs 28 — trivially confused.
5. **FWHM vs σ vs Γ** for linewidth. `Δν` (FWHM) appears in pulsed-ODMR sensitivity formulas
   with a lineshape factor `𝒫 = √(ε/(8 ln 2))`; mixing these costs tens of percent.
6. **Axis projection**: `B_∥ = B·cos θ`; a misalignment of 5° costs 0.4 %, but the
   "which one of the four NV axes" question is structural (the uncorrelated-noise penalty for
   measuring a single axis was quoted as a 5.3× increase in a patent example).
7. `Γ = 1/T₂*` (exponential convention) vs `T₂* = √2/(2πσ)` for Gaussian noise — the search
   material gives `T₂* = √2/(2π σ)` for Gaussian frequency noise.

---

## Reporting Conventions

### Uncertainties

- Default is **1σ** (= 68.27 % confidence). If you report a 95 % interval, say so.
- Contrast / fidelity values in NV qubit papers are frequently quoted with **asymmetric**
  68.27 % intervals (Innsbruck thesis convention).
- Always state **how** the uncertainty was obtained: fit covariance, bootstrap, Monte Carlo,
  Bayesian posterior, or across-seed std. "± x" without a method is not reportable.
- Charge/spin state-prep infidelity, dark counts, and finite visibility must be in the noise
  model; the NV readout is properly a **biased coin through three Poisson rates** (Hincks
  et al., arXiv:1705.10897), not a Gaussian.

### n reporting

- Report photons per point, measurement cycles per repetition level, number of τ points
  (300 here), number of seeds, number of test samples.
- Effective `n` for the photon budget is `r × N_points`, but the *cost* is
  `r · Σ_i (τ_i + t_ovh)` — always quote the cost, not just the count.

### p-values

- Physics journals: report exact p-values for non-standard tests, and state the test name.
- For L5: **paired Wilcoxon signed-rank** + **bootstrap CI** for the effect size, plus the
  seed count and the failure fraction. Do not report a p-value computed by treating paired
  samples as independent (the standard error is inflated).

### How NV papers state "sensitivity" — and the pitfalls

**Correct statement forms:**

- `η = X nT/√Hz` where η is the minimum detectable field per root **averaging time**, i.e.
  `δB_min(t) = η/√t`.
- Equivalently `η = σ_B √T_m`, or `η = σ_B/√(2Δf)` for a bandwidth Δf (arXiv:2009.02371);
  `δB_min = η/√t` (arXiv:2604.20901).
- Device papers: `η(f) = noise_PSD(f) / slope`, with slope = dSignal/dB in nT⁻¹ at the
  maximum-slope working point (arXiv:2305.06269).
- Volume-normalized variant: `T µm^{3/2} Hz^{-1/2}` (used when comparing sensing volumes,
  *Principles and techniques of the quantum diamond microscope*, Nanophotonics 2019,
  DOI 10.1515/nanoph-2019-0209).

**Pitfalls (each of these has produced a wrong published number):**

1. **Dividing by √bandwidth incorrectly.** η = σ/√(2Δf) holds only when the noise is **white**
   over the band and the quoted σ is a spectral density. If σ is already an rms over the band,
   dividing again by √Δf double-counts the bandwidth. Non-white (flicker, drift, laser
   technical noise) noise **breaks √t averaging entirely** — the Diamond-magnetometer patent
   (US20170146615A1) states this explicitly as the reason the √Hz normalization requires
   technical-noise mitigation.
2. **The Wolf et al. Erratum.** *Phys. Rev. X* **5**, 041001 (2015) claimed 0.9 pT/√Hz and
   ~100 fT in 100 s. **Erratum: PRX 13, 029903 (2023)** found an error in the shot-noise level
   estimation (Eq. 3, p. 7) and in the Allan deviation calculation; corrected values are
   **9 pT/√Hz** and ~900 fT in 100 s. A 10× headline error that survived 8 years of citation.
   Lesson: the σ in the numerator is the softest number in the whole formula — verify it
   against an independent photon-count calibration.
3. **Using the baseline noise instead of the working-point noise**, or ignoring the readout
   factor. The standard formula neglects a factor ≈ √(1 − 3C/4) ≈ 0.92 correction relative to
   a Monte-Carlo treatment (from the pulsed-ODMR sensitivity derivation in the Jülich/PhysRevA
   line of work).
4. **Forgetting dead time.** `η(τ) ∝ √(τ + t_d) e^{(τ/T₂*)^p}/(2πγC₀τ)`. Quoting a Ramsey
   sensitivity with `t_d` omitted overstates it; with T₂* = 1 µs, t_d = 3 µs, η_min is worse
   by ≈ 2.3× than the t_d = 0 case (13.2 → 30.7 nT/√Hz **approx**).
5. **Confusing protocol bandwidth with sampling rate.** An NV T₁ measurement can span MHz
   frequency bandwidth while repeating at <1 kHz; the temporal resolution ceiling is ~5 MHz
   from the optical pumping rate (200 ns metastable lifetime). DD bandwidth is Fourier-limited:
   center f₀ = 1/(2τ), width Δf = 1/(kτ) for k pulses.
6. **Reporting the noise floor as the sensitivity** (or vice versa). They differ by the
   slope conversion; see pitfall 2.
7. **Extrapolating a sensitivity claim from a simulation or from an out-of-range fit.**
   Rajpal et al. (arXiv:2409.09487) show data-driven models' uncertainty blowing up (up to 10×)
   outside the training range — a simulation-derived η claim inherits the same risk.

---

## Paper Structure for Physics Journals (PRA / PRApplied / Optics Letters class)

### PRApplied (the most likely target for an NV×AI methods paper)

- **Research Article**, REVTeX; IMRaD order (Introduction / Methods / Results / Discussion).
- **Unstructured abstract**, within the journal's stated limit (an out-of-limit abstract is a
  common desk-return reason; exact numeric limit not confirmed by the sources consulted).
- **Mandatory Data Availability Statement**; declarations block covering ethics, conflict of
  interest, funding.
- **Authors of Research Articles and Letters must supply a 100-word justification** of why the
  paper suits PRApplied — write this early, it doubles as the significance paragraph.
- Length: enforced as a **total word-equivalent count** = text + displayed math + figures +
  tables, with figures converted via `(150/aspect_ratio) + 20` words single-column and
  `300/(0.5·aspect_ratio) + 40` double-column; PRX/PRApplied reviews use a flat
  **170 words per single-column figure, 340 per two-column figure** (APS length guide).
  A **30,000-word** figure applies to PRApplied **Review Articles** only.
- References in **APS numbered style**. Figures/tables captioned and cited in order.
- **AI tools may assist but cannot be authors; substantive AI use must be disclosed.**

### PRA

- Regular Articles are full-length; Letters in PRA up to **5 pages**.
- Same APS reference/caption conventions; APS length guide gives word-equivalents
  (displayed math = 16 words per row, single-column).

### PRL (if the result is a short, sharp claim)

- **3,750 words OR ~4 journal pages**, whichever comes first (word count includes body text,
  figure captions, footnotes; excludes title, abstract, authors, acknowledgments, references).
- **Abstract ≤ 600 characters** (approximately 75–100 words), single paragraph, **no
  references, equations, or footnotes**. One of the shortest abstract limits in physics.
- PRL expects a broad-interest hook; the "low photon budget + full sweep" framing may or may
  not clear that bar — PRApplied is the safer home for a methods + dataset paper.

### Optics Letters

- **Limited to four printed pages** (confirmed by multiple sources; also applies to letters
  papers in *Optica*).
- **Abbreviated reference style**: journal citations omit article title and final page number;
  list up to three author names, then *et al.* A full bibliography page is added automatically
  and **does not count** against the page limit.
- Figures must be placed and sized at their in-text position (not grouped at the end);
  accessibility requires not relying on color alone (use shapes / line styles / labels).
- Back matter order: Funding / Acknowledgment / Disclosures / **Data Availability Statement
  (required)** / Supplemental Document.
- **[UNSOURCED]** A specific 35-word abstract limit for Optics Letters was not confirmed by the
  sources consulted — check the official Optica author guidelines before relying on it.

### Typical NV magnetometry paper skeleton (regardless of journal)

1. Introduction — application + why sensitivity/photon budget matters, prior art.
2. Sensing principle — Zeeman Hamiltonian, Ramsey sequence, the sensitivity model
   `η(τ)`, T₂*/contrast/readout definitions.
3. Experimental — diamond, setup, sequence timings including **t_ovh**, τ grid, repetition
   ladder.
4. Estimation method — estimator, training data provenance (synthetic vs real), baselines.
5. Results — fringes, error vs reps (log-log), η(reps), reps-to-δB\*, CRLB overlay,
   failure fraction, coverage.
6. Discussion — where the gain comes from, limits, generalization range.
7. Methods / Supplemental — CRLB derivation, noise model, hyperparameter tuning budget,
   seeds, compute.

---

## Reviewer Expectations in This Field

What a referee for *PRApplied* / *PRA* / *PRL* / *Optics Letters* will demand from a
"low-photon-budget, better estimator" paper:

1. **CRLB comparison.** Show the achieved error against the CRB — including the **full
   nuisance-parameter inversion**, not `1/J_ff`. Referees in this field know the difference.
   Experimental precedent that the estimator can saturate the quantum CRB exists (npj QI 2022),
   so "we are near the CRB" is a verifiable, and expected, claim.
2. **Matched photon budget / matched total measurement time.** Any claimed gain must be at
   equal `t_total` (or equal `r`). **The field has a working precedent for this**: Guo et al.
   (arXiv:2506.13469) re-implemented a competing baseline inside their own framework with the
   same loss, particle count and training iterations "to make a fair comparison". A referee will
   ask whether the baselines got a comparable tuning budget.
3. **Honest error bars and reported n.** 1σ, method stated, n stated. Failure / large-error
   fraction reported for every low-SNR estimator. Overconfident Bayesian/NN uncertainties are a
   standard reviewer catch — be ready to show expected coverage.
4. **Real data.** Training on synthetic/anchored-simulation data is accepted; **headline
   evaluation on synthetic only is not.** The Wolf et al. erratum is the field's living memory
   of what happens when a headline sensitivity claim is not independently validated.
5. **Baselines at their best.** LM multi-start NLS, FFT+Rife, grid Bayes with declared priors,
   each with a stated hyperparameter search. A baseline that was hand-tuned to lose is the
   classic rejection reason.
6. **No bandwidth/√Hz sleight of hand.** Reviewers will reconstruct η from your numbers and
   check that white-noise assumptions were tested (Allan deviation or equivalent).
7. **Statistical hygiene:** ≥5 seeds for learned methods, paired tests, pre-registered target
   δB\*, no cherry-picked seed, no test-set tuning.
8. **Anti-overlap with companion work.** For L5 specifically: do not re-argue the τ_off/φ0
   calibration discovery (L1) or the sparse-sampling design story (L3/L4); cite them as known
   conventions / companion instrument work. Expect at least one referee to have read them.
9. **Reproducibility artifacts:** Data Availability Statement is mandatory at APS and Optica;
   a reviewer may ask for the held-out split definition, the exact τ grid, and the seeds.
10. **AI-use disclosure** and human accountability statement per journal policy.

### Things a referee will likely *not* accept as contributions

- Inference speed as a headline claim (only as supporting evidence in a real-time niche).
- Beating the CRB (impossible — instant credibility loss).
- A "sensitivity improvement" that comes from a different τ grid, a different number of τ
  points, or a different total accumulation time.
- Reconstruction loss on a degradation model, reconstruction quality as a proxy for field
  accuracy, or training-set performance presented as generalization.
