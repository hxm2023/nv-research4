# PAPER_CLAIM_AUDIT.md — zero-context numerical audit of `paper/main.tex`

Auditor: independent (no prior context on this project). Date: 2026-09-12.
Audited revision: **commit `9185ba8`** ("Phase 3 draft"). SHA256 (first 16 hex) of the files read:

| file | sha256[:16] |
|---|---|
| paper/main.tex | 35e4eaa0ad300c43 |
| paper/numbers.tex | 7a7661d1458ccca9 |
| src/make_numbers.py | 51971df99af3b253 |
| results/analysis_v2.json | 4e0e4ae3ead8b1a3 |
| results/blind_res_nets.json | 3ca49b2ae5053407 |
| results/phase_frame_stats.json | 6bb18c67d0edbf6a |
| results/control_pooling_bias.json | 1a6d63c5ee6bf3ba |
| results/envelope_sheet8.json | 05f7938e2605de6c |

Method: every macro was resolved in `paper/numbers.tex`, traced through `src/make_numbers.py` to a JSON
field, and the underlying quantity was **independently recomputed from the raw per-column arrays**
(`blind_eval.json`, `blind_partial_pool.json`, `blind_res_nets.json`, `control_pooling_bias.json`,
`envelope_sheet8.json`, `phase_frame_stats.json`, `reference_B_sheet8.json`, `data/dc_real.npz`).
Note: the repository was being edited during the audit (`paper/numbers.tex` and `src/make_numbers.py`
changed at 20:41, `results/phase_frame_stats.json` appeared at 20:40). Findings refer to the hash above.

---

## 1. Macro provenance table

Legend: OK = value in `numbers.tex` reproduces from the traced JSON field (within its print precision);
⚠ = traceable but with a stated defect.

| macro group (count) | value(s) | JSON source per make_numbers.py | independent recompute |
|---|---|---|---|
| `\rmseLm*`, `\biasLm*` (16) | 743/629/383/262/195/165/109/59; biases −64…−15 | `analysis_v2.json` → `tables.cols7_40.r*.lm_refine.{rmse,bias}` | OK, exact (e.g. 742.90→743, 59.42→59) |
| `\rmsePool*`, `\biasPool*` (16) | 439/344/272/176/215/175/174/146 | `tables.cols7_40.r*.joint_refine` | OK, exact |
| `\rmsePart*`, `\biasPart*` (16) | 465/343/261/146/151/123/123/95 | `tables.cols7_40.r*.partial_pool` | OK, exact |
| `\ratioLmPool*` (8) | 1.69/1.83/1.41/1.49/0.91/0.94/0.63/0.41 | computed lm/pool RMSE | OK |
| `\crlbFree*`, `\crlbJoint*` (16) | 744/419 … 66/37 | `analysis_v2.json` → `crlb_medians.r*.*_median` (median over **all 40** columns) | OK; ⚠ the efficiency quoted in the text uses the **cols 7–40** median (`crlb_own`, e.g. 736.9 at 5k, 65.1 at 640k), so the bound quoted (744) and the efficiency quoted (1.0–1.3) come from different column sets |
| `\lawALm`, `\lawBLm`, `\lawFitLm`, `\lawAPool`, `\lawBPool`, `\lawFitPool` (6) | 785.3/27.8/32.6; 416.8/156.2/18.9 | `analysis_v2.json` → `floor_law.cols7_40` | OK, exact (re-fit: 785.30/27.84/32.55; 416.78/156.22/18.86) |
| `\crossoverReps`, `\crossoverRepsRounded`, `\photonGainFactor` (3) | 9.1e4, 9, 3.55 | same block | OK, exact (90764.4; 3.5503) |
| `\env*Mean`, `\env*Std` (10) | 0.127±0.005, 0.889±0.006, 5.404±0.294, 2.014±0.423, −0.044±0.123 | `envelope_sheet8.json` → `env_sheet8` (40×5) | OK, exact (numpy ddof=0) |
| `\sysMedianAbs`, `\sysMin`, `\sysMax` (3) | 44, −107, +139 | `reference_B_sheet8.json` − nominal grid, cols 7–40 | OK (44.48, −107.36, +138.56) |
| `\ctrlLm*`, `\ctrlPool*`, `\ctrlPart*` (15) | 520.7/374.5/414.4 … 51.7/217.8/235.3 | `control_pooling_bias.json` → `rows[*].{lm,pool_full,pool_partial}.median` | OK, exact |
| `\etaLm*`, `\etaPool*` (16) | 1.82/1.08 … 1.65/4.04 | computed: RMSE·√(r·(tau_sum+300·1 µs)), tau_sum=903 µs | OK, exact; overhead sensitivity also reproduced from `eta_per_budget` |
| `\rmseNetSet*`, `\nSeedsNetSet` (9) | 542/410/280/178/145/120/86/69, 3 | **`results/blind_res_nets.json`** (median over 3 `kind=="set"` runs of per-seed RMSE over cols 7–40) | OK, exact (542.4, 410.4, 280.2, 178.5, 144.6, 120.1, 86.3, 69.1). ⚠ **not** `analysis_v2.json` — see §3.6/§4 |
| `\phaseConc*` (8) | 0.955/0.971/0.989/0.985/0.989/0.991/0.993/0.992 | `results/phase_frame_stats.json` (new file, 20:40) | OK, exact; I reproduced 0.9546/0.9712/0.9893/0.9853/0.9890/0.9914/0.9931/0.9925 with the same estimator in `src/phase_frame_stats.py` |
| `\nTau`, `\nCols`, `\nSheets`, `\rMinK`, `\rMaxK`, `\tauOffNs`, `\tauStep`, `\bStep`, `\nBins`, `\WResid`, `\tauOffSigmaNs` (11) | 300, 40, 8, 5, 640, 18.6, 20, 1071.4, 512, 8, 2.6 | **hard-coded literals inside make_numbers.py** (not read from any result file) | consistent with `data_pipeline.py`/`blind_res.py`/`model.py`, but not machine-verified: `\nBins`/`\WResid` should be read from `blind_res.N_BINS`/`W_NT`, and neither is used in the text (`\WResid` is dead; line 443 hard-codes "±8µT") |
| `\tauMax`, `\bMax` (2) | 6.0, 42.9 | derived from `load_dc()` (npz) | OK |

Macros **defined but never used** (stale/dead, 85): all `\bias*` except `\biasPoolEightyK`/`\biasPoolSixFortyK`;
all `\rmseNet*`/`\biasNet*` (the *old* absolute-regression nets, `blind_nets.json`);
`\crlb*` for every budget except 5k; `\ratioLmPool{Ten..SixForty}K`; `\ctrl*` except the five quoted;
`\eta*` except the four quoted; `\phaseConcTwentyK/FortyK/EightyK/OneSixtyK`; `\WResid`.
`make_numbers.py` also contains a dead `boundRatio5k` append+pop.

**Numbers typed directly into `main.tex` (no macro, hence no drift guard):** the noise octuplet
(0.2079, 0.1500, 0.1072, 0.0745, 0.0533, 0.0370, 0.0263, 0.0183, line 119); "1–3.5%"; "1.4×"/"4.2×";
"27%"; "23%"; "~25%"; "±5%"; "1.8"; "~1.3 oscillations"; "25 starts"; "0.1 nT"; "0.674"; "2000
resamples"; "~50 nT"; "≥0.99". Some are legitimate prose constants, but the noise values in particular
have **no provenance file** (`per_point_noise()` only prints; no JSON stores it).

---

## 2. Recomputed vs claimed

### 2a. Table I (RMSE, nT, cols 7–40) — recomputed from raw per-column arrays

| r | lm claimed/rec. | pool claimed/rec. | part claimed/rec. | net claimed/rec. |
|---|---|---|---|---|
| 5k | 743 / 742.90 | 439 / 439.06 | 465 / 465.27 | 542 / 542.4 |
| 10k | 629 / 629.21 | 344 / 344.05 | 343 / 343.15 | 410 / 410.4 |
| 20k | 383 / 382.66 | 272 / 271.98 | 261 / 261.26 | 280 / 280.2 |
| 40k | 262 / 261.59 | 176 / 175.63 | 146 / 146.35 | 178 / 178.5 |
| 80k | 195 / 194.64 | 215 / 214.78 | 151 / 151.12 | 145 / 144.6 |
| 160k | 165 / 165.00 | 175 / 174.89 | 123 / 122.77 | 120 / 120.1 |
| 320k | 109 / 109.36 | 174 / 173.81 | 123 / 123.17 | 86 / 86.3 |
| 640k | 59 / 59.42 | 146 / 145.76 | 95 / 95.35 | 69 / 69.1 |

**All 32 cells reproduce exactly.** Net = median over the 3 seeds of the per-seed RMSE (per-seed values
at 5k: 608.3 / 496.8 / 542.4; at 640k: 61.6 / 70.8 / 69.1). The seed-ensemble alternative (median of
`B_hat` across seeds) gives nearly the same numbers (e.g. 529.9 at 5k, 65.6 at 640k), so the choice of
seed statistic is not the source of any discrepancy.

### 2b. Two-term floor law

Re-fit reproduces the paper exactly: lm A=785.30, b=27.84 (fit rms 32.55); pool A=416.78, b=156.22
(fit rms 18.86); r\*=5000·(A_lm²−A_pool²)/b_pool²=90 764; (A_lm/A_pool)²=3.550.

But the fit quality is poor and is **not** as harmless as "fit rms" suggests:
residuals of the pooled law reach +12.6%/−22.3% (at 80k/40k) and of the per-trace law +14.2%/−25.9%
(at 160k/640k). At 640k the lm law predicts 74.8 nT against a measured 59.4 nT. Consequently:
* the **measured** reversal (lm < pool) already happens at 80k (194.6 vs 214.8); log-linear
  interpolation of the measured ladder puts the crossing at **r≈7.0×10⁴**, not 9.1×10⁴;
* no uncertainty is quoted for A, b or r\*, although A and b are strongly correlated in this fit;
* §IV.B says "above ~80k repetitions … per-trace fitting" while the fitted crossover is quoted as
  9.1×10⁴ in the abstract, §IV.B and the Discussion — an internal inconsistency.

### 2c. Synthetic control (`control_pooling_bias.json`)

All quoted macros reproduce exactly (520.7 / 374.5 / 414.4 at 5k; 51.7 / 217.8 / 235.3 at 640k), and
520.7/374.5=1.39 ("1.4×"), 217.8/51.7=4.21 ("4.2×") are correct. Three textual claims are **false**:
1. "with the pooled error flattening at ~156.2 nT, the same floor as in the fit to the real ladder":
   the control's pooled **median** is 235.9 (160k) → 217.8 (640k) nT and still falling; 156.2 nT is the
   RMSE-based floor fitted to the *real* ladder — a median (control) is being compared with an
   RMSE (real) floor, 39% apart at 640k.
2. "Partial pooling … lowers the floor (235.3 nT at 640k)": 235.3 > 217.8, i.e. partial pooling is
   *worse* than full pooling at 640k (and at 40k: 271.2 vs 257.7; only at 160k is it 0.3% better).
3. "shifts the crossover beyond the measured range": in the control, per-trace LM already beats
   partial pooling at 40k (248.8 vs 271.2), so the crossover is *inside* the measured range.
Also note the control gives every classical estimator an **oracle initialisation** at the true field
(`control_pooling_bias.py` passes `B_true[c]` as the centre of a ±3214 nT window, unlike the blind
FFT+Rife protocol used for the headline), uses random fields drawn *with replacement* from 1…40
(not the real fixed grid), and reports medians from only n=3 synthetic sessions with no CI.

### 2d. Envelope population

Reproduces exactly (A 0.127±0.005; C 0.889±0.006; T2\* 5.404±0.294 µs; p 2.014±0.423; φ0 −0.044±0.123).
Two caveats:
* **The quoted spread is not the column-to-column range.** T2\* std/mean = 5.44% (so "±5%" is a std),
  but the actual per-column range is 4.511–6.238 µs = **−16.5%/+15.4%**; A ranges −8.4%/+8.8%.
  The paper's mechanism story ("inhomogeneity of the envelope sets the floor") is *understated* by
  quoting ±5%.
* The stds are dominated by a few columns. Column 1 (B=1071 nT, excluded from the headline region)
  has **p = 4.000 = the upper fit bound** and φ0 = 0.524 rad. Removing that one column changes
  p from 2.014±0.423 to 1.963±0.283 (−33% in std). No generating script exists in the repo for
  `envelope_sheet8.json` (only readers), so the fitting bounds behind these values are undocumented.

### 2e. Other spot checks

* **Noise.** Independent recomputation from `data/dc_real.npz` (3-point second difference /√6) gives
  0.20791, 0.14995, 0.10716, 0.07450, 0.05333, 0.03696, 0.02630, 0.01833 — the paper's digits are
  right, but deviations from σ=0.207√(5000/r) are **+0.19% to +3.54%**, not "1–3.5%" (sheet 8 is
  0.19%, sheet 1 is 0.44%, sheet 3 is 3.54%).
* **Efficiency of per-trace fitting.** From `analysis_v2.json` the eight values are
  1.01, 1.21, 1.04, 1.00, 1.06, 1.27, 1.19, **0.91** — i.e. 0.91–1.27, not "1.0–1.3". The 640k value
  is *below* its own bound (59.4 vs 65.1 nT); the RMS-average per-column free-envelope CRLB over
  cols 7–40 at 640k is 66.4 nT, so the reported RMSE is below even an average bound. That is possible
  only because the "efficiency" reference (a local CRLB evaluated with the same-data envelope fits)
  is not a valid bound for this windowed/initialised estimator, so efficiency ratios (up to 3.9 for
  pooling, 5.3 for the old network) should not be over-interpreted.
* **η.** All sixteen values reproduce; the ranking inversion occurs between 40k and 80k identically
  for t_ovh = 0.5/1/2 µs, so the overhead-independence claim is correct.
* **Systematic.** 44 nT median |deviation|, range −107…+139 nT reproduces; note the quoted "median
  absolute deviation" is the median of |deviation from nominal| (centre 0), not a MAD about the
  median deviation — harmless but imprecise wording.
* **Phase frame.** 0.9546/0.9712/0.9893/0.9853/0.9890/0.9914/0.9931/0.9925 reproduces the paper's
  0.955/0.971/0.992–0.993 and the "≥0.99" of the Fig. 4 caption (640k sheet).

---

## 3. Unverified claims (each with what is missing)

1. **"attains the best measured precision of any estimator at and above 80k repetitions"**
   (abstract, §IV.E). True at 80k (145 vs 151), 160k (120 vs 123) and 320k (86 vs 109); **false at
   640k, where per-trace LM is better (59.4 vs 69.1)** and every one of the 3 network seeds
   (61.6/70.8/69.1) is worse than LM. Margin at 80k is also within seed spread (one seed gives 159.7,
   worse than partial pooling); no CI is computed for the new nets.
2. **"an efficiency of 1.0–1.3 across the whole budget ladder"** (§IV.A; "efficient … at every budget"
   in the abstract). Contradicted by the source of that very number: 0.91 at 640k. Fix to
   "0.9–1.3" (or explain the sub-CRLB point).
3. **"the pooled estimator acquires a positive bias that grows with the budget (185 nT at 80k,
   125 nT at 640k)"** (§IV.B). The two numbers quoted in the same sentence contradict "grows"; the
   pooled bias rises 8→185 nT from 5k to 80k and then stays flat/falls (144, 151, 125).
4. **"the per-trace bias is consistent with zero at every budget"** (§IV.B). No bias uncertainty,
   CI or test exists in any result file (`analysis_v2.json` stores `rmse_ci` only). The point biases
   are within ~1.6×SEM of zero, but the claim as written is untested.
5. **"Partial pooling … lowers the floor"** (§IV.C) — directly contradicted by the cited macro
   (235.3 vs 217.8 at 640k). See §2c.
6. **Table I caption "Values are generated from results/analysis_v2.json"** — the network column is
   generated from `results/blind_res_nets.json`, and the phase macros from
   `results/phase_frame_stats.json`.
7. **Fig. 1 vs Table I: the network plotted is not the network tabulated.** `make_figures.fig1`
   reads `analysis_v2.json → net_set_ens`, i.e. the **old, absolute-regression, 5-seed** `blind_nets.json`
   estimator: 455.1/427.0/309.2/222.3/239.7/219.0/187.7/197.6, labelled "amortized, session-conditioned".
   Table I and §IV.E report the **new residual** network: 542/410/280/178/145/120/86/69. The figure
   and table therefore disagree at *every* budget (at 640k: 198 vs 69 nT) and the figure implies the
   network beats partial pooling at 5k (455 vs 465), contradicting the table (542 vs 465).
   `paper/figures/*.pdf` are timestamped 20:09, before the new nets (20:26).
8. **"without being told … the budget"** (Discussion iii). The network explicitly receives
   `log10(σ)` as context at both training and evaluation (`train_res_jindun.py` line 99,
   `blind_res._ctx`), and under the declared shot-noise law σ⇔r. The budget is an input.
9. **"the crossover is predictable rather than merely empirical"** (Discussion ii). No result file
   derives b from the envelope scatter; b=156.2 nT is fitted to the same ladder it is used to
   interpret (circular), and no uncertainty or out-of-sample prediction is reported.
10. **"$25$ starts inside the blind window. Doubling the number of starts changes the result by less
    than $0.1$ nT"** (Methods). The pipeline that produced the headline numbers
    (`blind_eval.py → lm_multistart`) uses **9** starts; 25/100 starts belong to the *voided* v1
    `ladder_eval.py` (oracle windows), and the 0.1 nT figure appears only in
    `review-stage/ADVERSARIAL_RESPONSE.md`. No result file tests start-count sensitivity for the
    blind protocol.
11. **"Wilcoxon signed-rank tests between paired estimators on the same traces, reported per budget"**
    (Methods). `analysis_v2.json` contains no p-values; the only Wilcoxon computation is in the
    voided v1 `ladder_eval.json`. Nothing in the paper reports it.
12. **"A frozen split reserves the two lowest-budget sheets and the columns that are multiples of
    seven for evaluation"** (Methods). `results/frozen_split.json` does not exist, `frozen_split()`
    is never called by any analysis script, and the reported metric (cols 7–40, all 8 sheets) mixes
    dev columns and the "holdout" columns 7/14/21/28/35. Unverifiable as written.
13. **"$T_2^*$ … varies by ±5%"** (abstract, §II, §V, Fig. 4 caption): 5.44% is the std; the column
    range is −16.5%/+15.4%. Either say "std of 5%" or quote the range.
14. **"stays within ~25% of the pooled bound at the lowest budget"** (abstract): the network is 29.3%
    above the joint CRLB (542.4/419.5) and 23.5% above the pooled *estimator* (542.4/439.1). Pick one
    and quote the matching reference. Similarly the abstract's "sits a factor 1.69 above the bound
    that becomes available when pooled" conflates the bound ratio (744/419 = **1.77**) with the
    RMSE ratio (1.69). "within 23% of pooled inference" is 23.5% (and is seed-fragile: 13%–39%
    across the three seeds).
15. **No grid-Bayes baseline.** CLAUDE.md requires the classical comparators (LM multistart / FFT+Rife /
    grid Bayes) to be given a generous tuning budget; the manuscript reports only LM variants with a
    shared FFT+Rife init. `baselines.grid_bayes` exists but no result file evaluates it, so the
    "classical baseline" claim is narrower than the project's own protocol.

---

## 4. Verdict

**FAIL** — not because the numbers are wrong (the generated layer is unusually clean), but because
several headline, abstract-level claims are contradicted by the manuscript's own result files and one
figure plots a different estimator than the table it is said to support.

What is solid: every macro in Table I, the floor-law coefficients and crossover formula, the envelope
population, the control values, η, the systematic, and the phase-frame concentrations trace to result
files and reproduce to print precision under independent recomputation.

Required fixes, in priority order:

1. Delete or qualify "best measured precision of any estimator at and above 80k repetitions"
   (false at 640k: 69.1 vs 59.4 nT) — e.g. "at 80k–320k".
2. Correct "efficiency of 1.0–1.3" to 0.91–1.27 and state that at 640k the per-trace RMSE lies
   *below* the nominal free-envelope CRLB, which invalidates that bound as an efficiency reference.
3. Rewrite §IV.C: the control does **not** show partial pooling lowering the floor (235.3 > 217.8 nT at
   640k) nor a crossover beyond the measured range, and the pooled control error is not "flattening at
   ~156.2 nT" (it is 217.8 nT at 640k and still falling). Compare medians with medians, RMSE with RMSE.
4. Replace the "bias grows with the budget" sentence (bias peaks at 80k, then falls).
5. Regenerate Fig. 1 from the same network as Table I (`blind_res_nets.json`), or state explicitly that
   the figure shows the earlier 5-seed absolute-regression network.
6. Fix the Table I caption provenance (net ← `blind_res_nets.json`; phase ← `phase_frame_stats.json`).
7. Fix Methods: real start count (9, not 25) and either drop the 0.1 nT claim or add a result file;
   drop the Wilcoxon sentence or add the test to `analysis_v2.py`; drop the frozen-split sentence or
   commit `results/frozen_split.json` and report the holdout-only metric.
8. Remove or reword "without being told … the budget" (log σ is an input); similarly "the crossover is
   predictable" (b is fitted on the same ladder — no independent prediction is demonstrated).
9. Quote the noise-law agreement as 0.2–3.5%, and the T2\* inhomogeneity as a std (5%) or range
   (−16%/+15%), not "±5%".
10. Report the crossover with uncertainty and reconcile it with the measured reversal (interpolated
    ≈7×10⁴, already visible at 80k), or present 9.1×10⁴ explicitly as a fit parameter of an
    approximate law (law residuals up to 26%).
11. Add macro coverage for the noise octuplet (currently hand-typed with no result file), and read
    `nBins`/`WResid` from `src/estimators/blind_res.py` instead of hard-coding them.
12. Note that the envelope population (p=2.014±0.423) is driven by one boundary-saturated col-1 fit
    (p=4.000); excluding it gives p=1.963±0.283. Document the fitting bounds for
    `envelope_sheet8.json` (no generating script is committed).
