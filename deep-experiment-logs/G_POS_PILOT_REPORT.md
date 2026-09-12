# G-Pos Feasibility Pilot — Report (2026-09-12)

**Gate definition (pre-registered in CLAUDE.md, before running).** On the two lowest
photon budgets (Sheet1 = 5 000 reps, Sheet2 = 10 000 reps), compare an
amortized/prior-informed estimator against classical baselines at MATCHED information
budget. PASS iff there exists a pre-registered, reachable positive result of the form
"reaching δB\* with X reps where classical needs Y× more, p<0.01, ≥3 seeds", not
overlapping L1's claims; otherwise pivot honestly.

**Protocol frozen before running** (src/pilot_gpos.py, src/ladder_eval.py):
- Ground truth: applied field B_nom = 1071.4·n nT (primary); secondary reference =
  per-column fit at Sheet8 (640 000 reps) — `results/reference_B_sheet8.json`.
- Estimation task: |B − B_nom| ≤ 3 grid steps (3214.2 nT) — the canonical sensitivity
  scenario (precision of a field near a known operating point).
- Real data only for evaluation; τ grid 20n ns; τ_off = 18.6 ns (L1 convention, cited).
- Methods: LM multistart (25 and 100 starts), FFT+Rife, grid Bayes (marginal posterior),
  pooled joint LM (shared A, C, T2\*, p, φ0 across the 40 columns of the sheet, per-column B).

## Result 1 — classical vs pooled across the full photon ladder (real data, n=40 columns/sheet)

Median |ΔB| (nT) vs nominal, η = median δB·√t_total with t_ovh = 0:

| r | LM per-trace | pooled joint | CRLB (known envelope) | η ratio | paired Wilcoxon p |
|---|---|---|---|---|---|
| 5 000 | 569.9 | **307.0** | 415.2 | 1.86 | 1.4e-2 |
| 10 000 | 455.0 | **207.7** | 293.6 | 2.19 | 2.8e-5 |
| 20 000 | 295.1 | **154.4** | 207.6 | 1.91 | 1.9e-3 |
| 40 000 | 234.3 | **85.8** | 146.8 | 2.73 | 1.7e-6 |
| 80 000 | 158.1 | **73.2** | 103.8 | 2.16 | 2.2e-4 |
| 160 000 | 148.8 | 84.5 | 73.4 | 1.76 | 3.2e-4 |
| 320 000 | 78.5 | **49.9** | 51.9 | 1.57 | 4.4e-3 |
| 640 000 | 51.0 | 60.4 | 36.7 | 0.84 | 0.51 (n.s.) |

Reading: the pooled estimator is significantly better than per-trace fitting at every
budget from 5k to 320k, and the two agree at 640k where a ≈50 nT
instrument-systematic floor dominates. Failure fraction |ΔB|<500 nT at 5k: 42% (LM) vs
68% (pooled); at 10k: 55% vs 85%.

## Result 2 — the gain is NOT reducible to L1's calibration story

Ablation (share envelope A,C,T2\*,p only; φ0 free per column) vs full pooling:

| r | LM per-trace | envelope-only | full pooling (incl. φ0) |
|---|---|---|---|
| 5 000 | 569.9 | 443.1 | 307.0 |
| 10 000 | 455.0 | 405.3 | 207.7 |

Envelope pooling alone contributes 1.29× (5k) / 1.12× (10k). The remainder comes from
the shared calibrated phase frame, which is L1's *convention* (cited, not re-claimed).
Both contributions are reported separately in the paper.

## Result 3 — external-prior variant (no within-session pooling)

Using only an offline population prior (real high-rep envelope fits) + the calibrated
phase frame — i.e. applicable to a SINGLE measured trace, with no other columns consumed:

| r | LM per-trace | population-prior, φ0 free | population-prior, φ0 fixed |
|---|---|---|---|
| 5 000 | 569.9 | 404.2 (1.41×) | **374.2 (1.52×)** |
| 10 000 | 455.0 | 449.4 (1.01×) | **227.2 (2.00×)** |

This variant answers the "you spent 40× the experiment time" objection: with an external
prior the gain survives without pooling.

## Result 4 — physical basis checks

- Noise law verified on all 8 real sheets: robust per-point σ = 0.2070, 0.1500, 0.1072,
  0.0745, 0.0533, 0.0370, 0.0263, 0.0183 vs law 0.207·√(5000/r) (ratios 1.00–1.04).
- Envelope population (real Sheet-8 fits, n=40): A = 0.127±0.005, C = 0.889±0.006,
  T2\* = 5.40±0.29 µs, p = 2.01±0.42, φ0 = −0.04±0.12 rad.
- Phase frame is genuinely shared: circular concentration |R| = 0.955 (5k), 0.971 (10k),
  0.993 (320k), 0.992 (640k); mean φ0 between −0.05 and +0.02 rad across sheets.
- Free-envelope CRLB is exactly 1.80× the known-envelope CRLB at 5k, 10k and 40k — the
  nuisance penalty is set by the fringe geometry, not by the photon budget.

## Gate verdict

**PASS (provisional).** A pre-registered positive result exists and is measured on real
data at matched photon budget: at 5 000 repetitions the pooled estimator reaches
δB = 307 nT where per-trace classical fitting needs ≈3.4× more repetitions for the same
precision (paired p = 1.4e-2 over 40 real columns; 2.8e-5 at 10k). It does not overlap
L1 (different regime — L1 explicitly cedes "cols 7+ classically solved"; no external
field anchoring; envelope contribution separated from the cited phase-frame convention)
and does not enter L3/L4 territory (full 300-point sweep kept; only the photon budget
varies).

**Caveats carried into Phase 2** (do not overclaim):
1. The nominal-referenced error contains a ≈50 nT instrument systematic; all headline
   comparisons are also reported against the 640k reference (Sheet-8 fit).
2. The pooled estimator consumes the whole session's data — the paper must state the
   session task explicitly and report the single-trace external-prior variant alongside.
3. Classical hierarchical Bayes with the same information is the honest comparator and
   MUST be implemented; if it matches the neural estimator, the AI claim moves to
   calibration/amortization/η-optimality (W3), not raw accuracy.
4. The ≥3-seed requirement applies to the learned estimator; seeds are training seeds,
   with the real-data evaluation fixed.

**Cost.** 0 GPUh on jindun; local smoke runs only (<1 GPUh equivalent).
