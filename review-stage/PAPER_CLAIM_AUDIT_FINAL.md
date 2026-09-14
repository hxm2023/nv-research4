# PAPER_CLAIM_AUDIT_FINAL — zero-context numerical / claim audit

Auditor: independent (no prior knowledge of the project, no access to earlier audits).
Date of audit: 2026-09-14.

**VERDICT: FAIL** (see §6). The classical ladder, the two-term law, the crossover, the
identifiability criterion, the add-back test and the fit audit all reproduce exactly. The
manuscript nevertheless contains several claims that the result files contradict, one of
which is a headline claim (the amortized network's ranking), plus two wrong hand-typed
numbers, one untraceable and non-reproducible number, two undefined cross-references and a
figure caption that does not describe the plotted quantity.

---

## 1. Method and inputs

Audited revision: **git `a9b4bea`** ("Add the grid-Bayes baseline across the ladder"),
working tree clean at audit time. `git rev-parse --short HEAD` = `a9b4bea`.

File hashes at audit time (md5):

| file | md5 |
|---|---|
| paper/main.tex | `3fcef61d7c714651727b1c305d940730` |
| paper/numbers.tex | `6a7a7f538926996f28b732619a3bc2a7` |
| results/analysis_v2.json | `30cb26134607c01ad88bc78364b7549e` |
| results/blind_eval.json | `ddcc0f83ec6131c3009d786a4735b8c5` |
| results/pooled_34col.json | `2fde44cfae8eb8bc16a7a17236849e6c` |
| results/blind_res_nets.json | `702d498843c821fd12c4cf2acb66e829` |
| results/robustness_checks.json | `1d33013a38b4eeb87b15acc40d828c7a` |
| results/control_pooling_bias.json | `7992045d90c16c18c7d0147a33bb7381` |
| results/addback_experiment.json | `1220b3e32b4276a56baf3f44e3235ccb` |
| results/identifiability_criterion.json | `eebd0ef00d3869a79c31965f5f6de331` |
| results/session_table.json | `a1bd284dacc272ce6424d33a4a5a1b51` |
| results/audit_fits.json | `73770eadc28b639308398c03ae00966a` |
| results/grid_bayes_ladder.json | `bc276afd37c423ad2de40074e291fcef` |
| results/envelope_sheet8.json | `b87b24019bf9db1dafe6a2e1a1d69f63` |
| results/phase_frame_stats.json | `784b4a75049d6d9d70f79bf876025b35` |

Method. Every ladder number was recomputed from the **raw per-column `B_hat` arrays** in
`blind_eval.json` (lm, 40-col pooled), `pooled_34col.json` (`pool_shared34`, `pool_T2free34`,
34 settings mapped onto 0-based columns 6–39), `blind_res_nets.json` (runs with
`kind=='set'`/`'trace'` at the largest step count having ≥5 seeds, i.e. steps=30000, 5 seeds;
per-seed sheet RMSE over 0-based columns 6–39, median over seeds) and
`grid_bayes_ladder.json`. RMSE = sqrt(mean((B_hat − B_nT)^2)) over indices 6..39, B_nT from
`src/data_pipeline.load_dc()`. The two-term law was refitted with
`src/analysis_v2.fit_floor_law` (identical to the code that produced the paper's macros).
No value was taken from `analysis_v2.json` tables except where explicitly stated.

Note: the working tree changed once during the audit (commit `a9b4bea` was created between
the first read of `main.tex` and the recomputation). All numbers below refer to `a9b4bea`.
`analysis_v2.json` still carries an unused legacy network block (`net_set_ens`, from
`blind_nets.json`) that differs from the paper's network column; see §3 note (n).

---

## 2. Recomputed vs claimed

### 2a. Table I — RMSE (nT), real columns 7–40 (0-based 6..39)

Recomputed (raw arrays; `net` = median over the 5 residual session-nets at 30k steps,
per-seed min/max in brackets). `gb` and `abl` are the grid-Bayes and attention-ablated nets.

| r | lm | pool | part | gb | net (median [min,max]) | abl |
|---|---|---|---|---|---|---|
| 5k | 742.9 | 454.7 | 484.1 | 668.6 | 504.1 [494.9, 564.5] | 559.3 |
| 10k | 629.2 | 318.8 | 323.6 | 603.1 | 386.6 [379.4, 388.1] | 401.9 |
| 20k | 382.7 | 279.4 | 277.8 | 358.0 | 289.2 [275.2, 302.8] | 285.5 |
| 40k | 261.6 | 147.4 | 147.9 | 236.7 | 171.6 [168.2, 186.1] | 188.5 |
| 80k | 194.6 | 114.5 | 116.8 | 243.4 | 138.6 [132.6, 144.2] | 145.4 |
| 160k | 165.0 | 98.2 | 98.5 | 246.9 | 113.4 [109.3, 114.6] | 129.6 |
| 320k | 109.4 | 85.9 | 86.2 | 173.4 | 87.8 [84.0, 94.9] | 96.4 |
| 640k | 59.4 | 73.1 | 73.3 | 174.0 | 66.2 [64.2, 67.3] | 83.4 |

All 7 ladder macro families (`rmseLm`, `rmsePool`, `rmsePart`, `rmseGB`, `rmseNetSet`,
`rmseAbl`, `medNetSet` × 8 budgets = 56 macros) were compared automatically against this
recomputation: **0 mismatches**. Table I's four columns are exactly reproducible from the
raw JSON.

Best measured estimator per budget: pool at 5k, 10k, 40k, 80k, 160k, 320k; part at 20k
(277.8 vs pool 279.4); lm at 640k.

### 2b. Two-term law and crossover (abstract, Sec. IV B)

| quantity | manuscript | recomputed | verdict |
|---|---|---|---|
| A_lm, b_lm, fit rms | 785.3, 27.8, 32.6 | 785.30, 27.84, 32.55 | exact |
| A_pool, b_pool, fit rms | 456.0, 57.6, 18.8 | 456.03, 57.56, 18.82 | exact |
| (A_lm/A_pool)^2 | 2.97 | 2.966 | exact |
| r* (`crossover_reps`) | 6.2×10^5 | 616 904 | exact |
| r* from quoted A and b via 5000(A_lm²−A_pool²)/b_pool² | — | 616 900 | consistent |
| full-sweep law (Table III) | 416.8, 156.2, 9.1×10^4 | in `session_table.json` | matches file (see §4 on provenance) |
| strict-33 law | 459.4, 55.4, 6.6×10^5 | 459.36, 55.38, 661 400 | matches file |
| "changes the fitted law by less than 1%" | <1% | ΔA +0.73%, **Δb −3.8%, Δr* +7.2%** | **unsupported** |
| T2-free law | 474.8, 53.2, 6.9×10^5 | matches `session_table.json` | exact |

Efficiency of per-trace fitting against the (median) free-envelope CRLB:
0.999, 1.196, 1.029, 0.995, 1.047, 1.255, 1.176, **0.904** (5k→640k). The manuscript's
"between 1.0 and 1.3 for r ≤ 320k" is acceptable (0.995/0.999 round to 1.0); "**0.91** at
640k" is a mis-round — the value is 0.90 (and the paper's own printed integers, 59/66,
give 0.89).

Joint-bound efficiency for the pooled estimator: 1.084, 1.075, 1.332, 0.994, 1.092, 1.324,
1.638, 1.972. Free/joint bound ratio: 1.77 at all eight budgets.

### 2c. Synthetic control (Sec. IV C)

`control_pooling_bias.json` (synthetic, exact ground truth, seed 0, 3 realizations × 40
columns; **median** |error|, which is what `make_numbers.py` emits and the paper quotes):

| r | lm (median) | pool_full (median) | pool_partial |
|---|---|---|---|
| 5k | 520.7 | 374.5 | 414.4 |
| 10k | 415.8 | 270.0 | 280.8 |
| 40k | 248.9 | 257.7 | 271.2 |
| 160k | 91.3 | 235.9 | 235.2 |
| 640k | 51.7 | 217.8 | 235.3 |

The four quoted numbers (520.7 / 374.5 and 51.7 / 217.8) are **exact**. Caveat: they are
medians, whereas the rest of the manuscript is RMSE. In RMSE the same control gives
1092.7 vs 589.2 (5k) and **372.8 vs 376.2 (640k)** — i.e. in RMSE the control shows no
crossover in range. See §5.

### 2d. Add-back table (Sec. IV D, Table II)

| session | A (paper / file) | b (paper / file) | r* (paper / file) |
|---|---|---|---|
| 34 | 456 / 456.03 | 58 / 57.56 | 6.2e5 / 616 904 |
| +col 6 | 454 / 453.95 | 59 / 59.26 | 5.8e5 / 584 566 |
| +col 5 | 447 / 447.29 | 62 / 61.94 | 5.4e5 / 542 935 |
| +col 4 | 441 / 441.32 | 63 / 63.08 | 5.3e5 / 530 201 |
| +col 3 | 436 / 435.97 | 67 / 66.99 | 4.8e5 / 475 373 |
| +col 2 | 2339 / 2339.07 | 0 / 0.0 | — / nan |
| +col 1 | 2396 / 2396.46 | 0 / 0.0 | — / nan |

All Table II entries are exact. The claimed degradation ("each of the four … costs a few
per cent") is however only true of A (−0.5 to −1.5% per step): b rises +3.0/+4.5/+1.8/+6.2%
per step (cumulative +16%) and r* falls −5.2/−7.1/−2.3/−10.3% (cumulative −23%).

### 2e. Appendix fit audit

| claim | file | verdict |
|---|---|---|
| 39 allocated = 39 active, 0 dead, at every budget | `audit_fits.pooled_audit` | exact (39 = 34 B + 5 shared; T2 allocated once when shared — confirmed in `robustness_checks.pooled_fit`) |
| L-BFGS-B agrees "to within 0.0 nT at all eight budgets" | `lbfgs_median_diff_nT` = 0.0 at all 8 | supported as a **median**; note the L-BFGS-B start is the TRF solution itself (only the envelope starts at defaults), so this is a local re-convergence check, not an independent re-fit |
| cond(JᵀJ) = 1.2×10^11 at every budget | 1.2339–1.2421×10^11 | exact; smallest singular value 8.22×10^-8 (non-zero), so the ratio is genuine and not a floor artefact |

---

## 3. Specific-claims verdicts

(a) **"best measured precision of any estimator from 80k to 320k repetitions" — UNSUPPORTED
(FALSE).** At 80k the network is 138.6 nT against pooled 114.5 (21.1% worse); at 160k,
113.4 vs 98.2 (15.5% worse); at 320k, 87.8 vs 85.9 (2.2% worse, and the best seed, 84.0,
only ties the pooled value). The network is best at *no* budget. The parenthetical is
self-contradictory and cherry-picked: "139 nT at 80k against 117 nT for the best classical
estimator" (117 is not the best classical estimator — pool is 114.5 — and 139 > 117
anyway), and "88 nT at 320k against 109 nT" compares with per-trace LM rather than with the
best classical value (85.9).

(b) **"within 12% of per-trace fitting at 640k" — SUPPORTED.** 66.2 vs 59.4 = +11.4%.

(c) **"efficiency 1.0–1.3 for r ≤ 320k and 0.91 at 640k" — PARTLY SUPPORTED.** 0.995–1.255
for r ≤ 320k (0.995 and 0.999 round to 1.0). At 640k the value is 0.904 → 0.90, not 0.91.
The manuscript's explanation for the sub-unity point ("the bound is evaluated with a single
reference envelope, the column mean") is **not supported by the code**: in
`analysis_v2.crlb_table` the free-envelope bound is computed **per column** with each
column's own envelope (`*env[c]`); only the *joint* bound uses `env.mean(axis=0)`. With a
valid bound a sub-unity value is impossible, so the 0.904 point remains unexplained (the
efficiency also divides an RMSE over 34 columns by a *median* bound).

(d) **Identifiability criterion — SUPPORTED except one number.** `failing_columns=[1..7]`,
`n_identifiable=33`, bounds of the failing columns 4058.6 → 48 655 nT (manuscript
"4.1×10^3 to 4.9×10^4" ✓), cols 8–40 all below 1071.4 nT ✓, "33 of the 40 settings" ✓.
But "**columns 2 and 1, single-trace bounds of 16 and 20 field steps**" is **WRONG**: the
criterion file gives col 1 = 38.5 steps and col 2 = 45.4 steps (41 271 and 48 655 nT).
No variant bound I computed (free, known-envelope, joint) yields 16 or 20 steps.
Also "less than 1%" (§2b) is unsupported, and Table II's label "34 (identifiable)" includes
col 7, which is 1.02 steps and therefore fails the paper's own criterion (the text notes
the one-column discrepancy but the table label does not).

(e) **Attention-ablation numbers — SUPPORTED.** Ablated/network RMSE ratios:
+10.9, +4.0, −1.3, +9.9, +4.9, +14.3, +9.8, +25.9% for 5k→640k. "Worse at every budget
except 20k, by 4–26%" ✓; per-seed IQRs [25th,75th] overlap only at 20k ✓ (e.g. 5k:
[502.8,510.5] vs [556.4,563.2]).

(f) **Residual autocorrelation — SUPPORTED.** `robustness_checks.residual_autocorrelation`:
−0.00974, −0.01042, +0.00385 → −0.010, −0.010, +0.004 ✓ against 1/√300 = ±0.058 ✓.
(These sections were clobbered out of the file by a partial re-run and restored in
`a9b4bea`; they were missing from the working tree during part of this audit.)

(g) **Grid-Bayes claims — SUPPORTED.** 669/603/358/237 < lm 743/629/383/262 at the four
lowest budgets, 243/247/173/174 > lm 195/165/109/59 from 80k up ✓. Grid spec (161-point B
grid, ±3.2×10^3 nT, 3×3×9 nuisance nodes, A/C profiled) matches
`src/grid_bayes_ladder.py` ✓.

(h) **Envelope, phase, noise law, systematics — SUPPORTED.** A = 0.127±0.005,
C = 0.889±0.006, T2 = 5.404±0.294 µs, p = 2.014±0.423, φ0 = −0.044±0.123 rad, all exact
from `envelope_sheet8.json`; T2 scatter 5.4% ("±5%" ✓). Circular concentrations 0.955,
0.971, …, 0.993, 0.992 ✓. Systematic: median 44 nT, range −107…+139 nT ✓.

(i) **Sensitivity values and overhead independence — SUPPORTED.** η_pool = 1.12×10^6 vs
η_lm = 1.82×10^6 at 5k; 2.03×10^6 vs 1.65×10^6 at 640k; the ranking is identical for
t_ovh ∈ {0.5, 1, 2} µs ✓.

(j) **"essentially tied at 640k (73 against 59 nT)" (Sec. IV B) — OVERSTATED.** 73.1 vs
59.4 is a 23% difference in favour of per-trace fitting (pool/lm = 1.23), not a tie.

(k) **"every pooled estimator is 1.6–2.5× worse" at 640k (Sec. IV F) — UNSUPPORTED.** The
pooled estimators in Table I are 73.1/59.4 = 1.23× and 73.3/59.4 = 1.23× worse; the
full-sweep pooled variant is 2.45×; the grid-Bayes estimator (not pooled) is 2.93×. No
pooled estimator lies in the quoted 1.6–2.5× band.

(l) **"The reversal at high budget is equally significant (p = 1.1×10^-1 at 320k and
3.2×10^-1 at 640k)" — UNSUPPORTED (FALSE).** Those p-values are non-significant by any
convention; the sentence also contradicts the preceding sentence, which correctly calls
p = 9.8×10^-2 at 5k "marginal". The paired tests do confirm the low-budget ordering
(3.7×10^-4 at 10k, 3.2×10^-5 at 40k).

(m) **Fig. 2 caption: "The per-trace estimator lies 1.6–1.8× above the joint bound while
photons are scarce and converges to it at high budget" — UNSUPPORTED.** lm/joint =
1.77, 2.12, 1.82, 1.76, 1.85, 2.22, 2.08, **1.60** (5k→640k). The scarce-photon range is
1.76–2.22 (not 1.6–1.8), and there is no convergence towards the joint bound (the ratio is
still 1.6 at 640k).

(n) **"Reported values are the median over 5 seeds" / "30 000 steps" — SUPPORTED** for the
table's network column. Caveat (not a text error): the Wilcoxon macros `\pNetVsLm*` and the
legacy `\rmseNet*` macros in `analysis_v2.json` come from the *older* `blind_nets.json`
network (640k: 198 nT), not from the residual network in Table I (66 nT). The manuscript's
text does not quote those p-values, but the two networks must not be conflated.

(o) **"Raising the number of starts to 100 changes the fitted fields by less than 0.1 nT for
almost every column" (Sec. III C) — UNSUPPORTED as stated.** The only stored comparison
(`ladder_eval.json`, `lm_free` vs `lm_free_hi`) is 25 → 100 starts in the *non-blind*
(nominal-centred) protocol, and 20% (5k) / 17.5% (10k) of columns move by more than 0.1 nT,
with a maximum shift of 145.8 nT at 5k. No 9 → 100 comparison exists.

---

## 4. Numbers I cannot trace to a result file

Hand-typed numbers that are verified elsewhere in §3 are not repeated here. The following
have **no result file** (or are contradicted by one):

1. **"6.7×10^3 nT"** (Appendix: synthetic FFT median error at 5k). No file contains it. I
   reproduced the pipeline's own synthetic protocol (`blind_session_batch` / `gen_traces` +
   `sample_envelope`, 5k) for 12 seeds: the median FFT error is 0.9–1.4×10^3 nT, never
   6.7×10^3 (max per-session median 1410 nT; per-trace maxima reach 3–4×10^4 nT). The number
   is not reproducible and should be replaced by a computed value or removed.
2. **Noise levels "0.2079, 0.1500, 0.1072, 0.0745, 0.0533, 0.0370, 0.0263, 0.0183"** — no
   result file. My recomputation (3-point second difference / √6) gives 0.2079, 0.1489,
   0.1061, 0.0748, 0.0529, 0.0368, 0.0263, 0.0182; and the quoted spread "to within
   0.2–3.5%" is inconsistent with the paper's own digits (0.0–3.6%: sheet 8 deviates 0.0%,
   sheet 3 deviates 3.6%).
3. **"approximately r/150 detected photons per delay point (roughly 30 to 4×10^3)"** — an
   instrument calibration with no provenance file (it is at least used consistently as the
   secondary axis in Fig. 1).
4. **"16 and 20 field steps"** (Sec. IV D) — contradicted by `identifiability_criterion.json`
   (38.5 and 45.4 steps). See §3(d).
5. **"σ/μ = 0.294"** for T2* (Sec. IV C) — the macro `\envTstarStd` is the absolute standard
   deviation in µs; the relative scatter is 0.2938/5.4036 = **0.054**. The same paragraph of
   Sec. II says "±5%", so the paper contradicts itself.
6. **"1.1×10^3 nT" median FFT initialisation error** — matches the *lowest-budget sheet*
   (1054 nT, 5k); the median pooled over all 8 sheets × 34 columns is 287 nT. Conservative,
   but the wording ("the FFT estimate is accurate to a median 1.1e3 nT") is not the median
   over the data actually used.
7. **"0.91" efficiency at 640k** — 0.904. Minor, but it is inconsistent with the paper's own
   quoted integers.
8. **The full-sweep session law (416.8 / 156.2 / 9.1×10^4)** exists only in
   `session_table.json`; **no committed script computes it** (`session_table.json` is not
   written by any file in `src/`; `git log -S full_sweep` finds only the JSON and
   `make_numbers.py`). The same applies to the paper's mechanism sentence "relaxing T2*
   recovers most of the difference even in the full-sweep session" — **no result file
   contains a full-sweep T2-free variant** (`session_table.json` has `primary_T2_free` only).
9. **"100 nT-class bias"** removed by partial pooling (Discussion) — the measured primary-
   region effect of relaxing T2* is 456.0→474.8 nT in A and 57.6→53.2 nT in b (i.e. a
   ~50 nT-class floor change), not a 100 nT-class bias.

Everything else typed by hand (128×, γ = 2π×28×10^-6, 300/40/8, 1071.4 nT, 6.0 µs,
0.674, 2000 resamples, 9 starts, 512 bins, ±8 µT, 3×3×9, 1.8× bound ratio, 0.207√(5000/r),
±3.2×10^3 window, 0.058 = 1/√300) is confirmed by code or data.

### Undefined cross-references / missing figures

* `\ref{fig:env}` (line 149) and `\ref{fig:control}` (line 388) are **undefined**
  (`main.log`: "Reference `fig:env' … undefined", "Reference `fig:control' … undefined").
  Only `fig:ladder`, `fig:bounds`, `fig:eta` exist. `figures/fig3_control.pdf` and
  `figures/fig4_envelope.pdf` are produced by `make_figures.py` but **never included** in
  the manuscript (`\includegraphics` appears only for figs 1, 2, 5). The synthetic-control
  paragraph therefore points at a figure that is neither present nor referenced, and Sec. II
  cites an envelope figure that does not exist.
* Fig. 1 caption: "for the classical estimators they [the bands] span the column-to-column
  interquartile range … not confidence intervals". The code (`make_figures.fig1`) plots
  `rmse_ci`, i.e. the 2000-resample **bootstrap confidence interval**, for the classical
  estimators (an interval is used only for the network, where it is the 25–75 percentile
  across seeds, labelled "hatched" but drawn as a shaded fill). The caption misdescribes
  both the statistic and the rendering.
* Fig. 1 caption also says "for the four estimators", but the figure now plots **five**
  series (per-trace LM, grid Bayes, pooled, partial pooling, network) — stale after the
  grid-Bayes addition.
* Fig. 5 caption describes only the per-trace/pooled curves and the overhead band; the
  figure also plots the network, which the caption does not mention.

---

## 5. Overstatements

1. **Network ranking** (§3a): "best of all methods from 80k to 320k" (abstract) and "best
   measured estimator of any method from 80k to 320k" (Sec. IV F). The network is worse
   than the pooled fitter at 80k, 160k and 320k, and worse than per-trace fitting at every
   budget below 640k. This is the paper's only learning-side headline and it is false.
2. **"best of all methods"** is also used to support the Discussion claim that the network
   "tracks the better classical strategy at both ends of the ladder" — at 5k the network is
   504 nT against 455 nT (10.9% worse) and at 640k 66 nT against 59 nT (11.4% worse).
   "Tracks" is defensible; "best" is not.
3. **"without being told the instrument model, the budget, or which parameters are shared"**
   (Discussion (iii)) contradicts the paper's own description: the network is *conditioned on
   log σ*, and σ = 0.207√(5000/r) determines r one-to-one, so the photon budget is an input.
   The abstract's "without being told the instrument model" (which omits the budget) is the
   accurate version.
4. **Abstract: "sits a factor 1.63 above the bound that becomes available when … pooled"** —
   1.63 is the ratio of per-trace RMSE to pooled *RMSE*; the ratio of the per-trace bound to
   the joint bound is 1.77, and the ratio of per-trace RMSE to the joint bound is 1.77.
   Sec. IV A states the 1.63 ratio correctly; the abstract misattributes it to the bound.
5. **"converges to it at high budget"** (Fig. 2 caption, §3m) — no convergence is visible in
   the data.
6. **"changes the fitted law by less than 1%"** (Sec. IV D) — true for A only (Δb = −3.8%,
   Δr* = +7.2%).
7. **"degrades the law continuously rather than abruptly"** (Sec. IV D) — the four
   intermediate additions move A by ≤4.4% in total while the last two change A by 5×, which
   is exactly the abrupt failure the same sentence then describes.
8. **Synthetic control "reproduces the crossover of the primary-region configuration"**
   (Sec. IV C) — not supported: (i) the control pools all 40 settings with fields drawn
   uniformly over the instrument range, i.e. the configuration the paper elsewhere calls the
   *full sweep*, not the 34-setting primary region; (ii) fitting the two-term law to the
   control gives r* = 2.3×10^4 (median) / 2.7×10^4 (RMSE), ~25× smaller than the quoted
   6.2×10^5, and a pooled floor of 223 nT (median) / 382 nT (RMSE) against the quote
   57.6 nT; (iii) the quoted control numbers are *medians* while the real-data ladder is
   RMSE — in RMSE the control does not cross over at all in the measured range.
   The control supports the *mechanism direction*, not the primary-region crossover or its
   location.
9. **"converges to the same fields" / "identical fields to within 0.0 nT"** (Appendix) — the
   recorded statistic is `lbfgs_median_diff_nT` (a median absolute difference) computed from
   a re-convergence started at the TRF solution; calling it "identical fields" is stronger
   than the recorded evidence.
10. **"the crossover is predictable rather than merely empirical"** (Discussion (ii)) — not
    demonstrated anywhere in the paper or the result files; the only exact-ground-truth
    control yields a floor 4–7× larger than the quoted b_pool.
11. **No uncertainty is reported for the headline r\* = 6.2×10^5**, while the repository
    contains a bootstrap for r* that is (a) unused in the manuscript and (b) computed for a
    different session (it returns median 8.9×10^4, 95% CI 4.9×10^4–1.3×10^5, i.e. the
    full-sweep value). Given that the abstract quotes a single-valued crossover, the absence
    of any interval — and the existence of a mismatched one — should be fixed or disclosed.

---

## 6. Verdict and required fixes

**Verdict: FAIL.** The manuscript is numerically faithful everywhere it is generated
(ladder, laws, crossover, add-back, audit, envelope, phase, efficiency, grid-Bayes,
ablation), but three statements are contradicted by the result files and several hand-typed
numbers are wrong or unsupported. Because one of them (the network's ranking) is a headline
claim and two are outright false statements of statistical and physical fact, the paper is
not submission-ready as it stands.

Required fixes, in priority order:

1. **Network ranking.** Delete "best of all methods from 80k to 320k" (abstract) and "best
   measured estimator of any method from 80k to 320k" (Sec. IV F). Replace with the verified
   statement, e.g.: "it is within 4% of the best classical estimator at 20k and 2% at 320k,
   is 21% and 16% behind the pooled fitter at 80k and 160k, and at 640k is within 12% of
   per-trace fitting while the primary-region pooled estimators are 23% worse and the
   full-sweep pooled fitter is 2.45× worse." If a ranking claim is wanted, quote the margins
   and the seed spread ([84.0, 94.9] at 320k).
2. **Add-back step counts.** Replace "16 and 20 field steps" with the criterion's values:
   column 2 = 45.4 steps (48 655 nT), column 1 = 38.5 steps (41 271 nT).
3. **σ/μ.** Replace "σ/μ = \envTstarStd" with σ/μ = 0.054 (or state 0.294 µs / 5.404 µs).
4. **Significance wording.** Replace "The reversal at high budget is equally significant
   (p = 1.1×10^-1 at 320k and 3.2×10^-1 at 640k)" with a statement that the high-budget
   reversal is **not** statistically significant on these 34 columns.
5. **"less than 1%"** → "changes A by 0.7%, b by 3.8% and r* by 7.2%".
6. **"essentially tied at 640k (73 against 59 nT)"** → state the 23% deficit explicitly.
7. **"every pooled estimator is 1.6–2.5× worse"** → replace with the measured ratios
   (1.23× for the primary-region pooled estimators at 640k; 2.45× for the full-sweep
   session).
8. **Fig. 2 caption** → "lies 1.8–2.2× above the joint bound while photons are scarce and
   1.6× at 640k, with no convergence to the joint bound".
9. **Synthetic control** → state that the control uses an all-40-setting session and quote
   its own r* (2.3×10^4, median basis) or drop the phrase "reproduces the crossover of the
   primary-region configuration"; state explicitly that the quoted control numbers are
   medians, not RMSE (or quote the RMSE values).
10. **Efficiency 0.91** → 0.90, and replace the explanation of the sub-unity point: the free
    bound is evaluated per column, not with "a single reference envelope (the column mean)";
    disclose that the efficiency divides an RMSE over columns by a median bound and that the
    sub-unity value therefore needs its own explanation.
11. **"6.7×10^3 nT"** → remove or replace with a reproduced number (12 seeds of the
    pipeline's own synthetic protocol give medians of 0.9–1.4×10^3 nT at 5k).
12. **Noise digits** → regenerate from a script (and fix the "0.2–3.5%" range, which is
    0.0–3.6% of the quoted values), or state the level of agreement actually measured.
13. **"100 starts"** → either recompute a 9 → 100 comparison under the blind protocol and
    report the real spread (20% of columns > 0.1 nT at 5k in the existing 25 → 100 run), or
    delete the sentence.
14. **"even in the full-sweep session" (T2-free)** → remove or produce the result; also add a
    script that regenerates `session_table.json` (currently only the JSON exists).
15. **Undefined references** → add `\label{fig:env}` and `\label{fig:control}` and include
    `figures/fig4_envelope.pdf` and `figures/fig3_control.pdf`, or delete the references.
    Fix the Fig. 1 caption to say the classical bands are bootstrap confidence intervals
    (or change the plotted quantity), and "the four estimators" → five.
16. **Discussion (iii)** → drop "or the budget" (the network is given log σ, which encodes
    it).
17. **Optional (provenance hygiene):** report a CI for r* (or state that the available
    bootstrap is for the full-sweep session), and note that `\pNetVsLm*`/`\rmseNet*` in
    `analysis_v2.json` refer to the legacy `blind_nets.json` network rather than the one in
    Table I.

Re-audit after fixes: items 1, 2, 3, 4, 6, 7, 9 are the ones that currently make the paper
FAIL; items 5, 8, 10–17 are quality/provenance fixes that should also be applied before
submission.
