# PAPER_CLAIM_AUDIT_FINAL2 — zero-context audit of the repaired revision

Auditor: independent (no prior knowledge of the project, no access to earlier audits).
Date of audit: 2026-09-14.

**VERDICT: PASS-WITH-FIXES.** 11 of the 12 claimed repairs are verified against the raw
result files and the twelfth is partial. The headline results (ladder, both floor laws, the
crossover, the identifiability criterion, the add-back test, the fit audit, the noise and
envelope statistics) all reproduce exactly, and the false network-ranking claim is gone.
However, four statements remain that the result files contradict or do not support, one of
which (`95 nT`, Sec. IV C) is a hand-typed number introduced by the repair commit itself and
present in no result file. Those must be repaired or the supporting experiment run before
submission (see §4).

---

## 1. Audited revision and inputs

`git rev-parse --short HEAD` = **`e612793`** ("Repair every finding of the zero-context audit
(FAIL -> fixes applied)"), working tree clean at audit time. The commit touches only
`paper/main.tex` and `paper/main.pdf`; every `results/*.json` and `paper/numbers.tex` is
byte-identical to the previously audited revision `a9b4bea`.

| file | md5 |
|---|---|
| paper/main.tex | `0e1a973f269c87a55b6df2d598b3d483` |
| paper/numbers.tex | `6a7a7f538926996f28b732619a3bc2a7` |
| paper/main.log | `fb5c68cbf6fcd7b9eb78a4568ddea7ef` |
| results/analysis_v2.json | `30cb26134607c01ad88bc78364b7549e` |
| results/blind_eval.json | `ddcc0f83ec6131c3009d786a4735b8c5` |
| results/pooled_34col.json | `2fde44cfae8eb8bc16a7a17236849e6c` |
| results/blind_res_nets.json | `702d498843c821fd12c4cf2acb66e829` |
| results/grid_bayes_ladder.json | `bc276afd37c423ad2de40074e291fcef` |
| results/control_pooling_bias.json | `7992045d90c16c18c7d0147a33bb7381` |
| results/session_table.json | `a1bd284dacc272ce6424d33a4a5a1b51` |
| results/addback_experiment.json | `1220b3e32b4276a56baf3f44e3235ccb` |
| results/identifiability_criterion.json | `eebd0ef00d3869a79c31965f5f6de331` |
| results/audit_fits.json | `73770eadc28b639308398c03ae00966a` |
| results/robustness_checks.json | `1d33013a38b4eeb87b15acc40d828c7a` |
| results/envelope_sheet8.json | `b87b24019bf9db1dafe6a2e1a1d69f63` |
| results/phase_frame_stats.json | `784b4a75049d6d9d70f79bf876025b35` |

Method. Every ladder number was recomputed from the raw per-column `B_hat` arrays
(`blind_eval.json`, `pooled_34col.json`, `blind_res_nets.json` runs with `kind=='set'` at
steps=30000 / 5 seeds, `grid_bayes_ladder.json`) over 0-based columns 6–39 with
`B_nT` from `src/data_pipeline.load_dc()`; the two-term law was refitted with
`src/analysis_v2.fit_floor_law`; the multi-start claim was re-run from the real traces
through `src/blind_eval.lm_refine`; the synthetic-initialisation claim was re-run through
`src/estimators/blind.blind_session_batch` + `fft_init_batch`; the noise levels were
recomputed as the three-point second difference / √6. No conclusion rests on
`analysis_v2.json`'s derived fields alone.

---

## 2. Verdict table for the 12 claimed fixes

| # | claimed fix | verdict | evidence |
|---|---|---|---|
| 1 | Figs. 3 (control) and 4 (envelope) present, `\ref{fig:control}`/`\ref{fig:env}` defined | **VERIFIED** | `main.tex` lines 407–416 and 418–429 contain both `figure` environments with `\includegraphics{figures/fig3_control.pdf}` / `fig4_envelope.pdf`; `main.aux` has `\newlabel{fig:control}{{3}{5}}` and `\newlabel{fig:env}{{4}{6}}`; `main.log` contains no "undefined" reference warning, and both graphics are placed (pages 5 and 6). The two "float is stuck" warnings are cosmetic deferrals, not losses. |
| 2 | Network within 2–21 % of the best per-budget classical estimator at every budget and never itself the best | **VERIFIED** (rounding caveat) | Recomputed (median over 5 seeds, per-sheet RMSE, cols 7–40) vs best classical = min(lm, pool, part, gb): gaps 10.9, **21.3**, 4.1, 16.4, 21.1, 15.5, 2.2, 11.4 % (5k→640k). Range 2.2–21.3 %: the 10k value exceeds the quoted 21 % by 0.3 pp (rounding). The network is strictly above the best classical value at all eight budgets, including 640k (66.2 vs lm 59.4; it is 9.4 % *better* than the pooled fitter there, but not best). |
| 3 | High-budget reversal no longer called "equally significant" | **VERIFIED** | Text now reads "the two become statistically indistinguishable ($p=0.11$ at 320k and $p=0.32$ at 640k)". `analysis_v2.wilcoxon_cols7_40` gives `joint_refine_vs_lm_refine` p = 1.09×10⁻¹ (320k) and 3.17×10⁻¹ (640k). The "equally significant" clause is gone. |
| 4 | 640k pooled stated as 23 % behind, not "essentially tied" | **VERIFIED** | 73.1119 / 59.4188 − 1 = **23.0 %**; text: "falls behind by 23 % at 640k (73 against 59 nT)". |
| 5 | Fig. 2 caption: per-trace 1.8–2.2× low / 1.6× high; pooled within 10 % to 80k, 2.0× highest | **PARTIAL** | `rmse/joint crlb_own` from `analysis_v2.tables.cols7_40`: per-trace 1.77, 2.12, 1.82, 1.76, 1.86, 2.23, 2.09, **1.60** — "1.8–2.2× at the lowest budgets and 1.6× at the highest" is acceptable. Pooled: 1.08, 1.07, **1.33**, 0.99, 1.09, 1.32, 1.64, **1.97** — "within 10 % of the joint bound up to 80k" is **false at 20k** (33 % above) and would also fail at 160k/320k; only "2.0× at the highest" (1.97) is right. Additionally the left panel is drawn from `crlb_medians`, which are medians over **all 40** columns, not "columns 7–40" as the caption says (the figure's own legend says "40 cols"). |
| 6 | Control paragraph: one shared envelope → full-sharing crossover r\* ≈ 3×10⁴, floor ≈ 0.4 µT, not the primary-region one | **VERIFIED** (with caveats) | Refitting `control_pooling_bias.json` with `fit_floor_law` on the **RMSE** series that Fig. 3 plots: lm A=981.7, b=542.9; pooled A=407.9, **b=381.7 nT = 0.38 µT**, r\* = **27 400 ≈ 3×10⁴**. The paragraph now explicitly says "full-sharing … one shared envelope … reproduces the full-sharing behaviour rather than the primary-region one". Caveats: (i) the synthetic *truth* has per-column envelopes drawn from the real population (`sample_envelope(rng, 40)` in `src/control_pooling_bias.py`); only the fitted model shares one envelope, so the phrase "one shared envelope for a session" describes the fitter, not the data; (ii) the same sentence quotes *medians* (520.7/374.5, 51.7/217.8) while the floor 0.4 µT exists only on the RMSE basis — a median-based fit gives b = 223 nT (0.22 µT), r\* = 22 600; (iii) the raw plotted RMSE points cross between 160k and 640k, so the 3×10⁴ crossover is a property of the fitted law, which Fig. 3 does not draw. |
| 7 | Strict 33-setting law quoted as A +0.7 %, b −3.8 %, r\* +7 % | **VERIFIED** | `addback_experiment.strict33`: A = 459.36 (+0.73 %), b = 55.38 (−3.79 %), r\* = 661 400 (+7.21 %) vs 456.03 / 57.56 / 616 904. |
| 8 | Columns 2 and 1 quoted as 45 and 39 field steps | **VERIFIED** | `identifiability_criterion.crlb_5k_nT`: col 2 = 48 655 nT / 1071.4 = 45.4 steps; col 1 = 41 271 nT / 1071.4 = 38.5 → 39. Text: "columns 2 and 1, single-trace bounds of 45 and 39 field steps". Also correct: failing columns 1–7, identifiable 8–40, 33 of 40, range 4.1×10³–4.9×10⁴ nT = 4–45 steps. |
| 9 | T2\* scatter as σ = 0.29 µs (5 % of mean), not σ/µ = 0.294 | **VERIFIED** | `envelope_sheet8.json`: T2\* mean 5.4036 µs, std 0.2938 µs → 5.44 %. Text: "$\sigma=0.294$ µs, i.e. 5 % of its mean". The σ/µ formulation is gone. |
| 10 | Appendix synthetic initialisation ≈ 0.9×10³ nT median over twelve sessions, range 0.7–1.2×10³, not 6.7×10³ | **VERIFIED** (approximately; no stored artifact) | Re-ran the pipeline's own synthetic protocol at r = 5000 (12 sessions × 40 cols, `blind_session_batch` + `fft_init_batch`): median-of-session-medians 0.89–1.06×10³ nT across seeds, per-session ranges ≈ 0.7–1.7×10³ (seed 0 batch: 943 nT, 689–1349; seed 1: 888, 728–1269). The 6.7×10³ claim is gone and the new value is the right order. The exact seed is not recorded and no result file exists, so the quoted *range* cannot be reproduced bit-for-bit. |
| 11 | Per-trace multi-start: median 0.03 nT, max 39 nT for 9 vs 25 starts | **VERIFIED** | Independently re-run on sheet 1 (5k), cols 7–40, blind FFT window, `lm_refine(n_starts=9)` vs `25`: median 0.0308 nT, max 39.26 nT (col 15). Sheet 8 gives ~0. The stored file (`ladder_eval.json`) is a 25→100 comparison in the *non-blind* protocol and is not the source. Caveat: the parenthetical justification is wrong (see §4 N5). |
| 12 | 640k efficiency (0.90) not explained by an incorrect reference-envelope statement | **VERIFIED** | The old sentence ("the bound is evaluated with a single reference envelope (the column mean of the high-budget fits)") is replaced by "the bound is evaluated with each column's own fitted envelope and the measured noise law; the 10 % sub-unity value … is within the uncertainty of those inputs and is not interpreted as super-efficiency". The replacement is qualitative but not false; the incorrect claim is gone and the value (0.912 → 0.90) matches the JSON. |

---

## 3. Spot-checked numbers (independent recomputation)

| # | manuscript value | provenance | recomputed |
|---|---|---|---|
| 1 | 743 nT (per-trace LM at 5k; abstract, Table I) | `analysis_v2.tables.cols7_40.r5000.lm_refine.rmse` | 742.90 ✓ |
| 2 | 744 nT (free-envelope bound at 5k; abstract) | `analysis_v2.crlb_medians.r5000.free_median` | 743.77 ✓ (median over **all 40** columns; the cols 7–40 median is 736.9 — a 1 % region mismatch in the same sentence) |
| 3 | A = 785.3 / b = 27.8 nT (lm) and A = 456.0 / b = 57.6 nT (pool); abstract, Sec. IV B | `analysis_v2.floor_law.cols7_40` | 785.30 / 27.84 and 456.03 / 57.56 ✓ |
| 4 | r\* = 6.2×10⁵ (primary) and 1×10⁵ (full sweep); abstract, Sec. IV B | `floor_law.crossover_reps`, `session_table.full_sweep_40.rstar` | 616 904 ✓ and 90 764 ≈ 1×10⁵ ✓ |
| 5 | Table I network column 504/387/289/172/139/113/88/66 nT | `blind_res_nets.json`, 5 seeds, 30k steps, cols 7–40 | 504.1/386.6/289.2/171.6/138.6/113.4/87.8/66.2 ✓ |
| 6 | Table I lm 640k = 59, pool 640k = 73, part 20k = 278, gb 5k = 669 nT | `analysis_v2.tables` | 59.4 / 73.1 / 277.8 / 668.6 ✓ |
| 7 | Table II full sweep 416.8 / 156.2 / 9.1×10⁴ | `session_table.full_sweep_40` | 416.78 / 156.22 / 90 764 ✓ |
| 8 | Table II primary T2\*-free 474.8 / 53.2 / 6.9×10⁵ | `session_table.primary_T2_free` | 474.82 / 53.19 / 691 436 ✓ |
| 9 | Table III: 34 → 456/58/6.2×10⁵; 38 → 436/67/4.8×10⁵; 39 → 2339/0/—; 40 → 2396/0/— | `addback_experiment.sessions` | 456.03/57.56/616 904; 435.97/66.99/475 373; 2339.07/0/nan; 2396.46/0/nan ✓ |
| 10 | Appendix: 39 allocated = 39 active; L-BFGS agreement 0.0 nT; cond(JᵀJ) = 1.2×10¹¹ at every budget | `audit_fits.pooled_audit` | 39/39, median diff 0.6–8.8×10⁻⁶ nT, cond 1.2337–1.2421×10¹¹ ✓ |
| 11 | Appendix: real FFT initialisation median 1.1×10³ nT | re-run `fft_rife` on the real traces | sheet 1 (5k): 1054 nT over cols 7–40, 1163 nT over all 40 ✓ (a per-budget/per-subset median; the all-sheet median is 400 nT) |
| 12 | Noise levels 0.2079, 0.1500, 0.1072, 0.0745, 0.0533, 0.0370, 0.0263, 0.0183 (Sec. II) | three-point second difference / √6 on `data_lab` | identical to all four digits ✓; deviations from 0.207√(5000/r) = 0.19–3.54 % → quoted "0.2–3.5 %" ✓ |
| 13 | Systematics: 44 nT median, range −107…+139 nT | `reference_B_sheet8.json` − `B_nT`, cols 7–40 | 44.5 nT, −107.4, +138.6 ✓ |
| 14 | η_pool = 1.12, η_lm = 1.82 (5k) and 2.03 / 1.65 (640k), ×10⁶ nT√µs | `analysis_v2.eta_per_budget.t_ovh_1us` | 1.115/1.822 and 2.029/1.649 ✓ |
| 15 | Fig. 4 caption: p scatter 21 %, |R| = 0.992, one setting at p = 4 | `envelope_sheet8.json` | 21.0 %, |R| = 0.9925, exactly one p = 4.000 ✓ |

All fifteen reproduce. The generated tables (I, II, III) and the abstract's law/crossover
macros are exactly faithful to the JSON.

---

## 4. New findings (still wrong / unsupported)

**N1 (serious, introduced by this commit). Sec. IV C: "freeing $T_2^{*}$ per column in the
full-sweep session moves the floor from 156.2 to 95 nT and the crossover from 9.1×10⁴ to
6.9×10⁵ repetitions."** No result file contains a *full-sweep* T2\*-free fit. A sweep of
every `floor_nT`/`b` field in `results/*.json` returns 27.8, 57.6, 53.2, 156.2, 362.8,
362.5, 362.7, 55.4 and the zero-floor add-back rows — **95 nT appears nowhere**, and
`6.9×10⁵` is exactly `session_table.primary_T2_free.rstar`, i.e. the **34-column primary
region** value (also `crossover_variants.json` "T2 per column"), not a full-sweep one. The
matching primary-region floor is 53.2 nT, not 95 nT. The previous revision carried no number
here; this commit added two. Run and store the full-sweep T2\*-free fit, or delete the
sentence.

**N2 (serious). Discussion: "leave the relaxation time free per field setting … removes a
100 nT-class bias, and it is what the partial-pooling estimator of Table I does."**
Table I contradicts this on the primary region: partial pooling vs full pooling is
484.1 vs 454.7 (5k), 323.6 vs 318.8 (10k), 277.8 vs 279.4 (20k), 147.9 vs 147.4 (40k),
73.3 vs 73.1 nT (640k) — it is worse or equal at seven of eight budgets. The floor change is
57.6 → 53.2 nT (4.4 nT), not 100 nT. The 100 nT-class figure can only be obtained by
conflating the *session-definition* change (full sweep 156.2 → primary 57.6) with the
relaxation-time change.

**N3. Abstract: "sits a factor 1.63 above the bound that becomes available when … pooled."**
1.63 = lm RMSE / pooled RMSE (742.90 / 454.70). The per-trace RMSE divided by the **joint
bound** is 742.90 / 419.47 = **1.77**, and the body of the paper gives the bound ratio
correctly as ≈ 1.8 (Sec. III B). The abstract misattributes an RMSE ratio to a bound and
contradicts the body.

**N4. Sec. IV F: "pooled inference is ahead of it by 11–21 % at the four lowest budgets
(139 against 114 nT at 80k is the worst case)."** Measured network-vs-pooled gaps at the four
lowest budgets are **10.9 %, 21.3 %, 3.5 %, 16.4 %** (5k, 10k, 20k, 40k); 20k is 3.5 %, not
11–21 %. The "worst case" parenthetical cites 80k, which is not among the four lowest
budgets, and the true worst gap is at 10k (21.3 %).

**N5. Methods: "by at most 39 nT (at the lowest budget, where the statistical error is
59 nT at best)".** 59 nT is the per-trace RMSE at **640k**, not at the lowest budget. At 5k
the per-trace RMSE is 742.9 nT (median 551.7 nT; the best-fitting column is 2.0 nT). The
number being justified (39 nT at 5k) is correct; the justification is wrong as written.

**N6. Discussion (iii): "without being told the instrument model, the budget, or which
parameters are shared."** The network is conditioned on log σ, and σ = 0.207√(5000/r)
determines r one-to-one; the paper says so two paragraphs earlier ("it is conditioned on the
noise level"). The abstract was corrected (it now omits "the budget"); the Discussion was
not. This is a residual from the previous audit.

**N7. Fig. 2 caption: "Left: the two Cramér–Rao bounds … median over columns 7–40."** The
`crlb_medians` used by the left panel are medians over **all 40** columns
(`analysis_v2.crlb_table` computes `free` over `range(40)`): the free curve is 743.8 nT at 5k
and 65.7 nT at 640k, whereas the cols 7–40 medians used for the right-panel normalisation are
736.9 and 65.1 nT. The joint bound is almost column-independent, so there the two medians
coincide (419.5 nT at 5k). The caption's "columns 7–40" is therefore inaccurate for the free
curve, and the figure's own legend already says the joint curve is a "40 cols" bound.

**N8. Fig. 5 caption omits the network curve.** `make_figures.fig5` plots the amortized
network (with its seed band) as a third series; the caption describes only per-trace and
pooled inference.

**N9 (provenance).** The crossover has no reported uncertainty, while
`robustness_checks.crossover_bootstrap` holds a 200-draw bootstrap (median 8.9×10⁴, 95 % CI
4.9×10⁴–1.3×10⁵). The macros exist and are unused. The stored bootstrap is for the
full-sweep session, so quoting it next to the primary-region r\* = 6.2×10⁵ would be wrong;
either bootstrap the primary-region r\* or state that no interval is available.

**N10 (provenance).** `session_table.json` (the full-sweep law of Table II, and the strict-33
and add-back variants) still has no committed generating script; only `make_numbers.py`
reads it.

---

## 5. Overall verdict

**PASS-WITH-FIXES.**

* The twelve claimed repairs are real, not cosmetic: 11 are VERIFIED against the raw files
  and 1 (Fig. 2 caption) is PARTIAL because the "pooled within 10 % up to 80k" clause is
  contradicted at 20k. The headline defects of the previous audit — the network ranking, the
  "equally significant" p-values, the "essentially tied" 640k comparison, the wrong field-step
  counts, the σ/µ confusion, the 6.7×10³ nT number, the missing figures 3 and 4 — are fixed.
* The generated numbers (Table I, Table II, Table III, the laws, r\*, the envelope, phase,
  noise, systematic and η values) are exactly reproducible; no mismatch was found in the 15
  spot checks.
* Nevertheless the manuscript is not yet clean. Four statements are contradicted by or
  untraceable in the result files — **N1** (the 95 nT / 6.9×10⁵ full-sweep T2\*-free
  sentence, newly introduced), **N2** (the 100 nT-class bias removal, contradicted by
  Table I), **N3** (the abstract's 1.63 "above the bound"), **N4** (the 11–21 % / four-lowest
  budgets sentence) — plus N5–N8 (mis-stated justification, budget claim, caption
  misdescriptions). N1 and N2 are the substantive ones: both describe a mechanism experiment
  whose result does not exist in the repository.
* Recommendation: produce and commit the full-sweep T2\*-free fit (which would also settle
  N2), or delete both sentences; fix the abstract's 1.63 → 1.77 (or "a factor 1.63 below the
  pooled estimator's error"); fix the 20k clause in the Fig. 2 caption; fix the 11–21 %
  sentence and the 59 nT parenthetical. With those five edits the manuscript is
  submission-ready on numerical grounds. If the unbacked 95 nT sentence is left in place,
  the next audit should return FAIL.
