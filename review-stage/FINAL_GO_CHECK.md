# FINAL zero-context GO/NO-GO check (physics manuscript)

## 1. Audited revision

| | |
|---|---|
| Hash at start of audit | `271e5fb` ("Close the remaining findings of the second audit (N1-N8)") |
| Hash at end of audit (current) | `c61b33c` ("Appendix: dimensionless conditioning diagnostic") |
| Delta between the two | one paragraph in the Appendix (raw cond `1.2e11` reinterpreted via a column-normalised Jacobian). No other file changed. |
| Working tree | clean; `paper/main.pdf` (19:02) is newer than `paper/main.tex` (19:02) and its extracted text contains the new appendix wording, so the PDF matches the source |
| Numbers pipeline | `paper/numbers.tex` (10:30) is older than `main.tex` (19:02) but no number-bearing JSON changed after 10:30, so no macro is stale |

The repository advanced by one commit *during* the audit (19:02:39). All checks below were executed against the current state `c61b33c`; the switch is immaterial because the delta is an appendix addition which was itself verified (§4, new finding F5).

## 2. Item-by-item verdict table

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Sec. IV C full-sweep numbers: floor 156 -> 92 nT, crossover 9.1e4 -> 2.4e5 | **VERIFIED** | Re-ran `robustness_checks.pooled_fit` (free=() and free=('T2',)) on all 40 columns x 8 real sheets, scored on cols 7-40, law by `fit_law`. Got A=416.73, b=156.22, r*=90 763 (stored 416.78 / 156.22 / 90 764) and A=457.30, b=92.02, r*=240 690 (stored 457.30 / 92.02 / 240 690). The T2*-free ladder reproduces to 2 decimals at every budget. |
| 2 | "differ by 4.4 nT of floor"; "removes 64 nT of floor" | **VERIFIED (numbers) / PARTIAL (cross-ref)** | 57.557-53.191 = 4.37 -> 4.4 nT (session_table `primary_all_shared` vs `primary_T2_free`); 156.216-92.015 = 64.2 -> 64 nT. Both exact. **But** the discussion cites `Table I` for the 4.4 nT; Table I is the RMSE ladder and contains no floor (nearest value is 4.8 nT = pool-part at 10k). The floors are in **Table II**. Wrong `\ref`. |
| 3 | Abstract factor per-trace-vs-pooled must not be "above a bound" | **VERIFIED** | 742.896/454.699 = 1.6338 -> `1.63`; abstract now reads "is a factor 1.63 **worse than the pooled estimator**", no bound claim. |
| 4 | Network paragraph: "ahead ... at every budget below 640k, by 3.5-21% ... within 4% at 20k" | **PARTIAL — range lower bound is wrong** | Recomputed (5 set-runs, 30000 steps, median of per-seed RMSE): margins are 10.9, 21.3, 3.5, 16.4, 21.1, 15.5, **2.2**, -9.5 % of pool. Range over those seven budgets is **2.2-21 %**, not 3.5-21 %. The 3.5-21 % quoted is the range over the four *lowest* budgets only. "Ahead at every budget below 640k" is true; "within 4 % at 20k" is true (3.50 %). |
| 5 | Fig. 2 caption ratios | **PARTIAL** | rmse/joint-bound: lm = 1.77, 2.12, 1.83, 1.76, 1.86, 2.23, 2.09, 1.60 (caption "1.6-2.2x, no trend" OK); pool = 1.08, 1.08, **1.33**, 0.99, 1.09, **1.32**, **1.64**, **1.97**. Caption's 1.3x at 20k/160k and 2.0x at 640k are right, **but** "within 10 % of the joint bound at most budgets" holds at only **4 of 8** budgets (5k, 10k, 40k, 80k), and the 1.64x excursion at 320k is not listed. |
| 6 | "median 0.03 nT, at most 39 nT at the lowest budget, an order of magnitude below the 743 nT error there" | **VERIFIED** | Re-ran `lm_refine(n_starts=9)` vs `25` on sheet 1, cols 7-40: median 0.0308 nT, max 39.26 nT (col 15); sheet 2 gives 0.006 nT. Per-trace RMSE at 5k reproduces as 742.9 -> 743 nT. |
| 7 | Fig. 5 must actually plot the network | **VERIFIED** | `make_figures.fig5` plots `res_net_ladder()` (3rd series, seed band); visually confirmed in `paper/figures/fig5_eta.png` (three labelled curves: per-trace LM, pooled, amortized network). Caption matches. |
| 8 | 5 figures + 3 tables present and included; no undefined refs | **VERIFIED** | LaTeX log reads all five PDFs (`fig1..fig5`); `main.aux` defines `tab:ladder` (I), `tab:session` (II), `tab:addback` (III) and `fig:ladder/bounds/control/env/eta` (1-5); log has **no** undefined-reference, multiply-defined or missing-file warning. Only two benign "float is stuck" warnings (placement, not content). |

## 3. Ten independently recomputed numbers

| # | Claim (where) | Manuscript | Recomputed | Source |
|---|---|---|---|---|
| 1 | per-trace RMSE at 5k (abstract, Sec. IV A) | 743 | 742.896 | `analysis_v2.json` `tables.cols7_40.r5000.lm_refine.rmse` |
| 2 | free-envelope bound at 5k (abstract) | 744 | 743.772 | `crlb_medians.r5000.free_median` |
| 3 | per-trace/pooled factor at 5k (abstract) | 1.63 | 1.6338 | 742.896/454.699 |
| 4 | law coefficients (abstract) | 785.3 / 27.8 ; 456.0 / 57.6 | 785.303 / 27.836 ; 456.031 / 57.557 | `floor_law.cols7_40` |
| 5 | photon-gain factor (Sec. IV B) | 2.97 | 2.966 | (A_lm/A_pool)^2 |
| 6 | Table I @640k (lm / pool / part / net) | 59 / 73 / 73 / 66 | 59.42 / 73.11 / 73.29 / 66.20 | `analysis_v2` + `blind_res_nets` (net = median of 5 seeds) |
| 7 | Table II full sweep (A / b / r*) | 416.8 / 156.2 / 9.1e4 | 416.73 / 156.22 / 90 763 (my refit) | `session_table.json`, reproduced |
| 8 | Table II full-sweep T2*-free (A / b / r*) | 457.3 / 92.0 / 2.4e5 | 457.30 / 92.02 / 240 690 (my refit) | `session_table.json`, reproduced |
| 9 | Table III row "+col 4" (A / b / r*) | 441 / 63 / 5.3e5 | 441.32 / 63.08 / 530 201 | `addback_experiment.json` |
| 10 | Appendix: 39 params, 0.0 nT L-BFGS, cond 1.2e11, scaled 3.99-4.00 | as stated | 39/39 active, 1e-6 nT, 1.239e11, 4.0000 (5k) and 3.9902 (640k) | `audit_fits.json`, `condition_scaled.json`, re-derived with the audit's own finite-difference Jacobian |
| 11 | eta at 5k / 640k (Sec. IV E) | 1.82/1.12, 1.65/2.03 | identical | `analysis_v2` + tau_sum = 903 us, t_ovh = 1 us |
| 12 | systematic 44 nT, -107..+139 nT (Sec. II) | as stated | 44.5, -107.4, +138.6 | `reference_B_sheet8.json` - nominal grid |

No mismatch in any of the twelve. Noise ladder (0.2079 ... 0.0183), envelope population (0.127/0.889/5.404/2.014/-0.044), phase concentration (0.955 ... 0.992), |R|=0.992, p-scatter 21 %, Wilcoxon p-values, CRLB ratio 1.757-1.784, and the synthetic control's floor (~0.38 uT from its RMSE ladder) and crossover (~2.7e4) also reproduce.

## 4. New findings

**F1 (substantive, not previously flagged).** Sec. IV F: the measured margin is **2.2-21 %** across the budgets below 640k; the text says 3.5-21 %, which is the range of the four *lowest* budgets only. At 320k the pooled estimator leads by 2.17 % (85.91 vs 87.78 nT), outside the quoted range. Fix: "by 2-21 %" or restrict the sentence to the four lowest budgets.

**F2 (previously flagged as N7, fix incomplete).** Fig. 2 caption "within 10 % of the joint bound at most budgets": true at 4 of 8 budgets. The 320k ratio (1.64x) is also omitted from the enumeration while smaller excursions are listed. Fix: "within 10 % at half the budgets ... and to 1.6x at 320k before reaching 2.0x at 640k".

**F3 (attribution).** Discussion (ii) states the +-5 % envelope variation "sets a bias floor b_pool ~ 57.6 nT". The manuscript's own Table II shows that freeing the inhomogeneous T2* in that same session moves the floor by only **4.4 nT** (57.6 -> 53.2); the full-sweep experiment that does show a 64 nT T2* effect is a different session. Meanwhile the nominal-vs-fitted field deviation over cols 7-40 has median 44 nT and rms 59.4 nT, i.e. the same size as the floor. The attribution of the primary-region floor to the envelope is therefore not established by any quoted number. Fix: either soften to "the floor is instrument physics, of which the envelope scatter and the magnet calibration are both of this order", or quote the full-sweep attribution explicitly as the mechanism evidence.

**F4 (wording).** Sec. IV C: "recovers about 40 % of the difference". Against the immediately preceding 156.2 vs 57.6 nT contrast, freeing T2* recovers 64.2/98.6 = **65 %**; 40 % is only obtained with the full-sweep floor itself as denominator (64.2/156.2 = 41 %). Fix the wording or the number.

**F5 (provenance; prior audit N10, still open).** `results/session_table.json` (including the newly added `full_sweep_40_T2free` block that backs item 1) and the new `results/condition_scaled.json` still have **no committed generating script**; `make_numbers.py` only reads them. I verified both reproduce exactly by re-running `pooled_fit`/`fit_law` and the audit's own Jacobian, so the values are trustworthy, but the regeneration path is not in the repo.

**F6 (trivial).** Sec. II: the noise law is said to be matched "to within 0.2-3.5 %"; the eight deviations are 0.02, 2.5, 3.6, 1.8, 3.0, 1.1, 1.6, 0.02 % (max 3.57 %).

Not defects (checked and cleared): the `\pNetVsLm*`, `\rmseNet*` (old net), `\medNetSet*`, `\crossoverCI*` and `\attrib*` macros are generated but unused, so the stale `blind_nets.json` network never enters the text; Table I's caption correctly names `blind_res_nets.json`; the Methods' "512-bin posterior spanning +-8 uT" matches `estimators/blind_res.py` (W_NT=8000, N_BINS=512), which is the net that produced `blind_res_nets.json`; the grid-Bayes description (161-point B grid, 3x3x9 nuisance grid, A and C by linear least squares, posterior mean) matches `grid_bayes_ladder.py`, except that the nuisance grid is **profiled (max), not marginalised** - the word "marginalised" in Sec. III C and "marginalising the envelope pays" in Sec. IV A overstates what the code does (no sum over the 81 nuisance nodes), which is a wording fix, not a numbers fix.

## 5. Verdict

**NO-GO** - four text/caption statements must change, all others verified:

1. Sec. IV F: "by 3.5-21 %" -> "by 2-21 %" (or restrict to the four lowest budgets). *(item 4)*
2. Fig. 2 caption: "within 10 % ... at most budgets" -> 4 of 8 budgets, and add the 1.6x excursion at 320k. *(item 5)*
3. Discussion (ii): stop attributing the 57.6 nT primary-region floor to the +-5 % envelope alone (Table II gives 4.4 nT); either qualify or cite the full-sweep attribution. *(F3)*
4. Sec. IV C: "about 40 % of the difference" -> 65 % (or reword the denominator). *(F4)*
5. Minor while editing: the 4.4 nT sentence cites Table I instead of Table II; Sec. III C/IV A "marginalised" -> "profiled"; "0.2-3.5 %" -> "0.02-3.6 %"; commit the scripts that regenerate `session_table.json` and `condition_scaled.json`.

The numerical backbone of the paper - Tables I-III, both ladder laws, both crossovers, the efficiency-vs-CRLB statements, the eta ladder, the full-sweep T2*-free experiment (independently re-fitted here), the figures and the appendix audit numbers - is exactly reproducible from `results/*.json` and the real traces. No fabricated, phantom or unreproducible result was found.
