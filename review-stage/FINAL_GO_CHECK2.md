# FINAL zero-context GO/NO-GO check #2 (physics manuscript)

## 1. Audited revision

| | |
|---|---|
| Hash at start of audit (as instructed) | `061584a` ("GO-check repairs: ...") |
| Hash at end of audit | `089a354` ("Number-provenance checker: classify matched/derived/unmatched ...") |
| Repo churn during the audit | `061584a -> c49f434 -> 77d58bd -> ea5032e -> f63dd89 -> 089a354`, caused by a concurrent submission-bundle process, not by this audit |
| Paper delta over that churn | `paper/main.tex` +11 lines (companion-work citations L3/L4 only); `paper/numbers.tex` regenerated (`\lawFullA` 416.8 -> 416.7, see N4). No result JSON changed. |
| Working tree | `paper/` and `results/` clean at the end of the audit; all item checks re-confirmed against the current file |
| Numbers pipeline | `paper/numbers.tex` (19:20) regenerates from the current `results/*.json` with a single one-character difference vs the committed file, now resolved in HEAD (N4) |
| Regeneration run | `python -m src.session_table` and `python -m src.condition_scaled` executed end-to-end on the real data during this audit |

## 2. Item-by-item verdicts on the six claimed fixes

| # | Claimed fix | Verdict | Evidence |
|---|---|---|---|
| 1 | 4.4 nT floor difference cited to Table II, not Table I | **VERIFIED** | `results/session_table.json`: `primary_all_shared.b - primary_T2_free.b = 57.5571 - 53.1900 = 4.367` -> 4.4 nT. The instance that carries a cross-reference (`main.tex:624`) reads `(Table~\ref{tab:session})`; `main.aux` maps `tab:ladder`=I, `tab:session`=II, `tab:addback`=III. The Discussion-(ii) instance (`main.tex:581`) has no `\ref` at all and its neighbouring sentences quote Table II values. No remaining reference to Table I for the floor. |
| 2 | Network margin 2.2-21% over the seven budgets below 640k (not 3.5-21%) | **VERIFIED** | Recomputed from `blind_res_nets.json` (`kind='set'`, `steps=30000`, five seeds `0-4`, RMSE over cols 7-40 of `B_hat` vs the nominal grid, median across seeds) against `analysis_v2.json` pooled RMSE: margins `10.86, 21.29, 3.50, 16.38, 21.06, 15.51, 2.17 %` at 5k/10k/20k/40k/80k/160k/320k -> **2.2-21%**; 640k = -9.45% (per-trace ahead, as stated). "Within 4% at 20k" = 3.50% and "within 2.2% at 320k" = 2.17%, both exact. Abstract "within 2-21% of the best per-budget classical estimator" = best-of-{lm,pool} margins 2.17-21.29%, exact. |
| 3 | Fig. 2 caption: within 10% of the joint bound at four of eight budgets; excursions 1.3x (20k, 160k), 1.6x (320k), 2.0x (640k) | **VERIFIED** | `rmse/joint_crlb_own` from `analysis_v2.json` (pooled): `1.084, 1.075, 1.332, 0.994, 1.092, 1.324, 1.638, 1.972`; within 10% at exactly four budgets (5k, 10k, 40k, 80k) and at the four listed excursions (1.33->1.3 at 20k, 1.32->1.3 at 160k, 1.64->1.6 at 320k, 1.97->2.0 at 640k). Per-trace ratios `1.603-2.225` -> "1.6-2.2x" exact. |
| 4 | Discussion (ii) drops the 5% T2* attribution | **VERIFIED** | The paragraph now says the variation "is **not** by itself what costs", quotes `4.4 nT` for the filtered session (= 4.367, above) and moves the mechanism to the session ("The envelope inhomogeneity matters through the session instead"), with the 156.2 nT full-sweep floor and the 65% recovery. Arithmetic of 65%: `(156.2243 - 92.0151)/(156.2243 - 57.5571) = 64.209/98.667 = 65.08%` -> matches `session_table.json` and the stated rounding. Wording nit: "the floor rises to 156.2 nT, of which freeing T2* recovers 65%" has a loose antecedent (65% is of the 98.7 nT contrast, not of the 156.2 nT floor itself); the unambiguous version is the Sec. IV C sentence. |
| 5 | "about 40% of the difference" -> 65% | **VERIFIED** | `main.tex:390` reads "recovers 65% of the difference"; the immediately preceding sentence contrasts 156.2 nT (full sweep) with 57.6 nT (primary region), so the antecedent difference is 98.67 nT and 64.21/98.67 = 65.1%. The old denominator (64.21/156.2 = 41%) is not the antecedent. |
| 6 | `src/session_table.py` and `src/condition_scaled.py` regenerate their JSONs | **VERIFIED (full rerun)** | Both scripts exist with committed generators (`session_table.py`: `ladder_for` + `pooled_fit` + `fit_law`; `condition_scaled.py`: finite-difference Jacobian of `pooled_objective`, unit column rescaling, SVD). Full `python -m src.session_table` reproduced all four panels to printed precision (456.0/57.6/616,902; 474.8/53.2/691,447; 416.7/156.2/90,763; 457.3/92.0/240,690). Numeric diff of the rewritten files against the stored ones: **0 of 62 scalars differ** (`session_table.json`) and **0 of 16** (`condition_scaled.json`), at double precision. |

## 3. Ten spot-checks against the result files

| # | Claim (location) | Manuscript | Recomputed | Source |
|---|---|---|---|---|
| 1 | Per-trace RMSE at 5k (abstract, Sec. IV A) | 743 | 742.896 | `analysis_v2.json` `tables.cols7_40.r5000.lm_refine.rmse` |
| 2 | Free-envelope bound at 5k (abstract) | 744 | 743.772 | `crlb_medians.r5000.free_median` |
| 3 | Per-trace/pooled factor at 5k (abstract) | 1.63 | 1.6338 | 742.896/454.699 |
| 4 | Both two-term laws (abstract, Sec. IV B) | 785.3 / 27.8 ; 456.0 / 57.6 | 785.303 / 27.836 ; 456.031 / 57.557 | `floor_law.cols7_40` |
| 5 | Network "within 2-21%" of best classical (abstract) | 2-21% | 2.17-21.29% | recomputed, see item 2 |
| 6 | Table I at 640k (lm / pool / part / net) | 59 / 73 / 73 / 66 | 59.42 / 73.11 / 73.29 / 66.20 | `analysis_v2` + `blind_res_nets` (5-seed median; net 66.20) |
| 7 | Table II full 40-setting sweep (A / b / r*) | 416.7 / 156.2 / 9.1e4 | 416.733 / 156.224 / 90,763 | `session_table.json` (and regenerated) |
| 8 | Table III add-back rows (+col 4; +col 2) | 441 / 63 / 5.3e5 ; 2339 / 0 | 441.32 / 63.08 / 530,201 ; 2339.07 / 0.0 | `addback_experiment.json` `n37`, `n39` |
| 9 | Fig. 3 caption: control floor and crossover | ~0.4 uT, ~3e4 reps | b = 381.7 nT (pooled RMSE ladder, `fit_law`), r* = 2.74e4 | `control_pooling_bias.json` + `robustness_checks.fit_law` |
| 10 | Appendix: params, optimiser agreement, conditioning | 39 / 0.0 nT / 1.2e11 / 3.99-4.00 | 39 allocated, 39 active; L-BFGS median diff 1e-5 nT; hess_cond 1.239e11; scaled 3.9875-4.0000 | `audit_fits.json`, `condition_scaled.json` (both regenerated) |

Also verified: eta at 5k/640k = 1.82/1.12 and 1.65/2.03 (`eta_per_budget.t_ovh_1us`); systematic 44.5 nT, -107.4 / +138.6 (`reference_B_sheet8.json`); strict-33 session 459.4 / 55.4 / 6.6e5 vs 34-setting 456.03 / 57.56 / 616,904 -> +0.7% / -3.8% / +7.2% as stated; identifiability criterion selects 33 with columns 1-7 failing and single-trace bounds 4.06e3-4.87e4 nT (4-45 steps); envelope 5% T2* and 21% p scatter, |R| = 0.992; control medians 520.7/374.5 (5k) and 51.7/217.8 (640k); 128x budget range; 2.97 photon-gain factor. No mismatch found in any of them.

## 4. New findings

**N1 (open; was in the previous punch list, not fixed). "Marginalised" is what the code does not do.** Sec. III C (lines 224, 226) describes grid Bayes as "a marginal posterior over B ... (T2*, p, phi0) marginalised on a coarse grid"; Sec. IV A (line 257) calls it "the marginal-posterior estimator" and (line 260) says "marginalising the envelope pays"; the Fig. 1 caption (line 304) repeats the name. `src/grid_bayes_ladder.py` (lines 32-46) loops over the 3x3x9 nuisance grid and keeps the **maximum** likelihood (`if v > ll: ll = v`) before normalising over B: the nuisance parameters are **profiled**, not marginalised (no summation over the 81 nodes). The estimator's numbers are unaffected, but the method description and its name are inaccurate, and the script docstring repeats the error. Fix: "profiled" (and "profile-posterior"/"profile-likelihood estimator" where the name is used).

**N2 (open; was F6 in the previous report, not fixed). Noise-law agreement range.** Line 147: the eight per-sheet noise estimates match `sigma(r)=0.207*sqrt(5000/r)` "to within 0.2-3.5%". Recomputed deviations: `0.43, 2.48, 3.57, 1.80, 3.00, 1.11, 1.64, 0.02 %` -> the true range is **0.02-3.6%**. The lower endpoint is wrong by 10x (conservative direction) and the upper is exceeded by 0.07 pp. The sentence is hand-written (no macro backs it). Fix: "0.02-3.6%", or generate it.

**N3 (new, non-blocking). Scope of the initialisation-error median.** The abstract, the Discussion conditional paragraph and the Appendix quote a "median initialisation error 1.1x10^3 nT" for the real traces. Recomputing FFT+Rife errors on cols 7-40: the 5k sheet median is 1054 nT (matches), but the pooled median over all eight sheets is 287 nT (sheet medians 175-1054 nT), and the maximum is 2742 nT against the 3214 nT window. The quoted value is therefore the worst-sheet median and is conservative (the "inside the window" claim is verified: no column exceeds the window), but the scope is unstated and no JSON/macro stores it. The appendix's synthetic companion figure ("0.9x10^3 nT over twelve sessions, 0.7-1.2x10^3") likewise has no committed generator. Recommend a scope qualifier ("at the lowest budget") or a stored statistic.

**N4 (transient, resolved).** At the pinned start hash `061584a`, `paper/numbers.tex` was stale for exactly one macro: `\lawFullA` = 416.8 while the committed `session_table.json` gives A = 416.7326 (-> 416.7). Re-running `src/make_numbers.py` produced exactly that single-line diff. The concurrent submission commit `77d58bd` regenerated the file; at the current HEAD `\lawFullA` = 416.7 and `paper/numbers.tex` matches the JSONs (re-verified). No remaining defect; noted only because the audit began on a state in which it was real.

Not defects (re-checked and cleared): Table I's network column is the `blind_res_nets.json` 5-seed median (macros `rmseNetSet*`), not the stale `blind_nets.json`; the full-sweep crossover "factor of seven" (616,902/90,763 = 6.80); the 23% (640k) and 63% (5k) margins quoted in Sec. IV F; Fig. 4's 21% p-scatter and |R| = 0.992; the eta overhead statement; the compiled `main.pdf` (19:19) is newer than `main.tex` (19:18) and `main.log` contains no undefined-reference, multiply-defined or missing-file warning.

## 5. Verdict

All six claimed fixes are **VERIFIED**, and the numerical backbone (Tables I-III, both ladder laws, the CRLBs, the eta ladder, the session-definition experiment, the add-back test, the appendix audit) reproduces exactly from the committed result files; the two previously uncommitted JSONs now have working generators whose full rerun reproduces them at double precision. Two items from the previous round's punch list were nevertheless left unedited, and one small scope issue is new.

**NO-GO** - exact remaining list (all text-only, none affects a number, table or figure):

1. Replace "marginalised"/"marginal posterior"/"marginal-posterior estimator"/"marginalising" with "profiled"/"profile-posterior"/"profile-likelihood" at `paper/main.tex` lines 224, 226, 257, 260 and in the Fig. 1 caption (line 304). *(N1; `src/grid_bayes_ladder.py` maximises over the nuisance grid)*
2. Change "to within 0.2-3.5%" to "to within 0.02-3.6%" at `paper/main.tex` line 147. *(N2)*
3. Recommended while editing (non-blocking): qualify the "median initialisation error 1.1x10^3 nT" as the lowest-budget value, or store the statistic. *(N3)*
