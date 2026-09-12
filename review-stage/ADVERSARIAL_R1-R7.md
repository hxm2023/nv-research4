# Adversarial Review R1–R7 — L5 "Estimator-limited sensitivity of NV Ramsey magnetometry at low photon budget"

Referee stance: hostile, physics-journal (PRA/PRApplied/OL class). Review date 2026-09-12.
Ground truth read: `CLAUDE.md`, `deep-experiment-logs/CANDIDATE_KILL_LOG.md`,
`deep-experiment-logs/SCOOP_CHECK_2026-09-12.md`, `results/ladder_eval.json`,
`results/pilot_gpos.json`, `results/reference_B_sheet8.json`, `results/envelope_sheet8.json`,
`src/{data_pipeline,baselines,model,ladder_eval,pilot_gpos,synth,train_amortized}.py`,
`src/estimators/amortized.py`, plus sibling repos `nv-research` (L1) and its `paper/main_v4.tex`,
`LIVE_STATE.md`, `CLAUDE.md`. All numbers below were independently recomputed in this session
from the shipped JSONs and the real `.xls`.

---

## R1 — Is the gain an artifact?

### VERDICT: **FATAL**

### R1.0 — The killer: an UNTRAINED network beats every method on the headline metric

I instantiated `PosteriorNet()` with **random weights (never trained, never loaded from a
checkpoint)** and ran the paper's own evaluation path (`predict` → `|B_hat − B_nom|`) on the real
5k/10k sheets:

| estimator | sheet1 (5k) median \|ΔB\| | sheet2 (10k) |
|---|---|---|
| **random untrained net** | **3.5 nT** (100 % within 500 nT) | **3.8 nT** (100 %) |
| `lm_free` (classical, 25 starts) | 569.9 nT | 455.0 nT |
| `joint_lm` (pooled, headline) | 307.0 nT | 207.7 nT |
| CRLB (known envelope) | 415.2 nT | 293.6 nT |

The untrained net's posterior is essentially uniform (mean entropy 5.44 vs ln 241 = 5.485;
`results/train_seed0.log` shows the training loss stuck at 5.4833–5.4855 through step 3600),
so its posterior mean is ≈ the prior centre, which `src/estimators/amortized.py:67` sets to
`B_center = 1071.4 × n` — i.e. **exactly the ground truth `B_nom`**. The metric is therefore
minimised by "return the prior centre", and it reports 3.5 nT for a device that measures nothing.

This is not a hypothetical: the trained model is *the same object* (loss still at the uniform
value), so as of this writing L5's ML vehicle already scores ~3.5 nT on its own headline metric
while having zero skill. Worse, the synthetic training target is `t_true = (B − B_center)/W_NT`
(`amortized.py:99`), so the network is trained to answer "how far from the field you were told to
expect", and at test time it is told the true field to ±3214 nT. **Any** hedge toward the prior
centre is rewarded by the metric as if it were precision.

The mirror-image fact: for *both* classical estimators the shrinkage parameter λ = 0 is optimal.
With `B_hat(λ) = B_nom + λ(B_hat − B_nom)`, the median \|error\| is minimised at λ = 0 (error 0)
for `lm_free` and `joint_lm` at every rep level (5k…640k). The comparison harness cannot
distinguish a measurement from a lookup.

### R1.1 — (a) The metric is contaminated by the per-column instrument systematic — YES, and it is the dominant term above ~160k reps

From `reference_B_sheet8.json` (per-column 640k LM fit) minus `B_nom = 1071.4·n`:

- cols 7–40: deviations −107 … +139 nT (median \|dev\| ≈ 44 nT), i.e. a real per-column
  systematic of order 50–140 nT that is *not* estimator noise;
- cols 1–6: −2078, −597, −324, +188, +391, +1261 nT — these columns are not measurable
  per-trace even at 640k (`lm_free` median \|err\| at 640k on cols 1–6 is still **929 nT**), so
  `B_ref` is itself unusable there and `B_nom` is the only available truth.

Consequences: (i) at 640k the CRLB is 36.7 nT while the systematic floor is ~44–140 nT, so the
whole 640k row measures the coil/calibration, not the estimator — which is exactly why the
significance vanishes (p = 0.51); (ii) at 40k the headline `joint_lm` = 85.8 nT is *below* the
systematic floor of cols 1–6 and comparable to the floor of cols 7–40, so "85.8 nT" is not an
estimator uncertainty. The paper must either (a) define the estimand as the *applied* field with
an explicit per-column systematic budget, or (b) use an off-grid/independently calibrated truth.
Neither exists today.

### R1.2 — (b) `joint_lm` "beating the CRLB" is a comparison error, not a bug in the fit

Recomputed with the three CRLBs already present (but unused) in `src/model.py`:

| sheet | lm_med | CRLB known-env | CRLB **free-env** (per-trace, correct for `lm_free`) | CRLB **joint** (shared env, 40 cols) |
|---|---|---|---|---|
| 5k | 569.9 | 415.2 | **726.1** | **381.4** |
| 10k | 455.0 | 293.6 | **513.4** | **299.3** |

Two errors compound:

1. **Wrong baseline bound.** `lm_free` estimates six parameters per trace (B, A, C, T2, p, φ0),
   so its bound is the free-envelope CRLB (726 nT at 5k), not the known-envelope CRLB (415 nT).
   `src/ladder_eval.py:76` uses only `crlb_sigma_B` (known envelope).
   `crlb_sigma_B_free_envelope` and `crlb_sigma_B_joint` are defined in `src/model.py:35,55` and
   **are called from nowhere in the repository** (verified by grep). The claim "classical
   per-trace fitting is 1.6–2.2× above the achievable bound" compares a 6-parameter fit to a
   1-parameter bound. Against its own bound, `lm_free` at 5k is 570/726 = **0.79**, i.e. *below*
   the bound, not 1.4× above it.
2. **Median vs. σ.** The CRLB bounds the standard deviation. For a zero-mean Gaussian the median
   \|error\| is 0.674σ. The correct "efficient-unbiased" reference for a median statistic is
   0.674 × CRLB: 726→489 nT (per-trace) and 381→257 nT (joint) at 5k. Against those, `lm_free`
   is 570/489 = **1.17×** and `joint_lm` is 307/257 = **1.19×**. Both estimators sit at the same
   ~1.2× inefficiency. **There is no "classical gap to the bound" for pooling to close.**

What pooling actually does is *move the bound*: 726 → 381 nT at 5k (1.90×) and 513 → 299 (1.72×).
Measured ratios 1.86× and 2.19× are indistinguishable from these bound ratios. The honest claim
is "pooling the instrument nuisance across a field sweep improves the *achievable* per-point
sensitivity by ~1.9× at 5k", which is a textbook property of nuisance-parameter pooling, not an
estimator-efficiency recovery and not an ML result.

### R1.3 — (c) The shared-φ0 constraint: physically defensible, but it is the majority of the gain and it is not L5's

`|R| = 0.955` (5k) / 0.992 (640k) and φ0 scatter 0.12 rad at 640k confirm the phase frame is a
genuine instrument property. But the decomposition in `CANDIDATE_KILL_LOG.md:40–42` says
envelope-sharing alone gives 1.29× (5k) / 1.12× (10k), while the full joint fit gives 1.86× /
2.19×. The φ0 share is therefore **1.44× at 5k and 1.96× at 10k** — i.e. the dominant term is the
shared phase frame, which is L1's `confirm_tau_off` / phase-anchoring result (see R7).

### R1.4 — Concrete code defects found

- **Bound rails as "measurements."** `src/baselines.py:129–132` constrains `B ∈ [0.75, 1.25]·B_init`
  and initialises at `B_init`, with `B_init = B_nom` (`ladder_eval.py:71`, `pilot_gpos.py:102`).
  The joint estimator is thus *told the true field to ±25 %*. `joint_lm` returned
  **1339.2499999999998 = 1.25 × 1071.4 exactly**, in *both* sheet1 and sheet2 (`ladder_eval.json`
  sheet1/sheet2 `joint_lm[0]`) — the estimator railed on the constraint. The reported 267.8 nT
  "error" for column 1 in both sheets is the *width of the constraint*, not a measurement. 2 of
  320 joint estimates rail; `lm_free` rails at its ±3214.2 nT window on 1–2 columns per low-rep
  sheet (cols 3 and 5 at 5k, both contributing exactly 3214.2 nT). Rail hits must be reported as
  fit failures, not as samples in a median.
- **Ablation numbers have no provenance.** 570→443/405 (envelope-only) and 570→374/227
  (external-prior variant) appear only as prose in `CANDIDATE_KILL_LOG.md:40–42`. No script, no
  JSON, no CSV exists (grep for `443|405|374|227|ablation|envelope_only` in `*.py` returns
  nothing). This violates the constitution's claim↔CSV↔script red line, and it is precisely the
  ablation that is supposed to prove non-overlap with L1.
- **`t_ovh = 0`.** `ladder_eval.py:92` calls `t_total_us(r_lvl, 0.0)`; the constitution requires
  an explicit `t_ovh` with 0.5×/1×/2× sensitivity. At `t_ovh = 1 µs`, Σ(τ+1 µs) = 1203 µs vs
  903 µs (η × 1.15 for both methods), so ratios survive, but the paper cannot ship an η axis
  without declaring this.
- The noise law is **verified**: the robust 3-point estimator gives 0.2079/0.1500/0.1072/0.0745/
  0.0533/0.0370/0.0263/0.0183 per sheet, i.e. 1.002–1.035× the assumed 0.207·√(5000/r). No
  sigma-side artefact. σ is not the explanation for R1.2.

### What would neutralise R1

A metric that cannot be gamed by the prior: report (i) signed bias and RMSE against a
truth *not* used to construct the estimator's prior, (ii) an off-grid test set (fields between
the 1071.4 nT grid points, where "return the centre" fails), (iii) charge the pooled estimator
its bound explicitly (`crlb_sigma_B_joint`) and the per-trace baseline its own
(`crlb_sigma_B_free_envelope`), (iv) report both as σ-equivalent, not median, or scale both by
0.674, and (v) run the untrained-net and constant-`B_nom` controls in every table.

---

## R2 — Is `lm_multistart` a weak baseline?

### VERDICT: **SERIOUS** (the specific "too few starts" attack is refuted; the "wrong parameterisation" attack stands and is unanswered)

Attacks I *tried to land and could not*:

- **Start count.** `lm_free` (25 starts) vs `lm_free_hi` (100 starts, `ladder_eval.py:58–67`) on
  the two test sheets are numerically identical to ≤0.06 nT for almost every column
  (`ladder_eval.json` `lm_free` vs `lm_free_hi`). The baseline is not start-starved. This attack
  fails honestly.
- **Window asymmetry.** Re-running the classical LM with the *same* ±25 % prior window that
  `joint_lm` gets (`lm_multistart(tau, y, 0.75·B_nom, 1.25·B_nom, n_starts=25)`), first attempt,
  this session, on the real data:

  | sheet | lm (wide window, shipped) | lm (matched ±25 % window) | joint | joint/lm_matched | p |
  |---|---|---|---|---|---|
  | 5k | 569.9 | **552.1** | 307.0 | 1.80× | 3.1e-2 |
  | 10k | 455.0 | **404.8** | 207.7 | 1.95× | 6.3e-5 |
  | 40k | 234.3 | **223.3** | 85.8 | 2.60× | 2.0e-6 |
  | 640k | 51.0 | **51.0** | 60.4 | 0.84× | 0.51 |

  Matching the prior does **not** close the gap. The pooling gain is real *as a data-processing
  gain* (though see R1.2 for what it means).

Attacks that land:

1. **There is no ML in the comparison at all.** `joint_lm` *is* a classical estimator — LM on a
   larger parameter vector. The pilot's positive result is "classical joint fitting beats
   classical per-trace fitting", i.e. the pre-registered G-Pos test (amortized estimator vs
   classical baseline, `CLAUDE.md` G-Pos) was **not run**. The pilot cannot support the ML claim
   it is cited for.
2. **The strong classical baseline already exists and is not in any result file.**
   `CANDIDATE_KILL_LOG.md:41–42` reports an *external-prior* variant (population-mean envelope
   from real high-rep fits + calibrated φ0, **no within-sheet pooling**) reaching 374 nT at 5k and
   227 nT at 10k. Compared with `joint_lm`'s 307/208, that classical, non-ML, empirical-Bayes
   estimator closes **79 %** of the 5k gap and **92 %** of the 10k gap. The ML vehicle must beat
   *that*, not per-trace LM. Against it the amortized contribution is ≤1.09–1.22×, i.e. below the
   pre-registered 1.2× falsification threshold at 10k.
3. **The correct strong baseline is profile likelihood over B with the envelope estimated from
   the same session** — which is *exactly* `joint_lm`. So the paper's "our estimator beats the
   classical baseline" reduces to "the classical baseline with more data beats the classical
   baseline with less data". A referee will not accept `joint_lm` as the *proposed* method and
   `lm_multistart` as the *baseline*: they are the same estimator under two parameterisations.

### What would neutralise R2

Report the external-prior/empirical-Bayes classical estimator as the primary baseline, with
matched information (same population envelope, same φ0 convention) and matched tuning; show the
amortized estimator beats it by a pre-registered margin, ≥5 seeds, on off-grid fields.

---

## R3 — Statistics

### VERDICT: **FATAL** as currently reported

1. **The pre-registered gate is not met.** G-Pos requires p < 0.01 and ≥3 seeds. At 5k the
   reported p is **1.41e-2 > 0.01**. Only 10k passes (2.8e-5). The kill log nevertheless presents
   5k as the headline. There are no seeds at all (LM is deterministic); the ≥3-seed requirement is
   unmet for every claim.
2. **Multiplicity across the 8-level ladder.** The same test is run at 8 rep levels and the
   narrative keeps 7 and explains away the 8th (640k, p = 0.51) as "the instrument systematic
   floor". Bonferroni over 8 levels requires p < 0.00625; **the 5k result fails that too**. The
   kill log's single sentence about 640k is post-hoc rescue of a falsified regime, not a
   pre-registered exclusion (the systematic floor is not independent of the hypothesis: a
   floor-limited regime is exactly where a bound-improving estimator must show no gain).
3. **The effect does not survive splitting by the region the sibling line says is solved.**
   Restricting to cols 7–40 (L1's "classically solved", ≥7.5 µT):

   | sheet | lm | joint | ratio | p (n = 34) |
   |---|---|---|---|---|
   | 5k | 551.9 | 382.7 | 1.44× | **0.143 (n.s.)** |
   | 10k | 373.3 | 205.3 | 1.82× | 2.5e-4 |
   | 20k | 278.6 | 157.2 | 1.77× | 0.053 |
   | 40k | 213.9 | 82.0 | 2.61× | 4.2e-5 |

   Restricting to cols 1–6: ratio 9.6× at 5k but **p = 0.0625 with n = 6** (the Wilcoxon floor) —
   untestable. So the 5k significance is manufactured by *mixing* two regions, neither of which
   is significant alone, and the column set that supplies the ratio (1–6) cannot be tested at
   all. n = 6 per region across 8 sheets is not enough for the claims being made about "the
   boundary/sub-cycle regime".
4. **Column independence.** 40 columns are a single swept-field session on one instrument.
   Cross-sheet correlations of the per-column signed errors are weak (r = +0.07…+0.31), so I
   cannot demonstrate a large independence violation — but the shared per-column systematic
   (R1.1) means the 40 paired differences are not exchangeable in the way Wilcoxon assumes. The
   correct unit of replication is the session; there is one session.
5. **Wrong statistic for the metric of record.** The constitution says η (or reps-to-target) is
   the headline. The ladder reports *median* \|ΔB\|, then computes η from it. A median is not a
   sensitivity: it does not enter `η = δB·√t_total`, does not propagate to a confidence interval,
   and is below the CRLB even for an unbiased efficient estimator (0.674σ). Likewise, "median
   error" hides the failure tail that the paper itself (W5) claims is the point: at 5k the
   `lm_free` fraction within 500 nT is 42 % vs 68 % for joint — a tail claim reported with no CI
   and no test.
6. **Overall η is flat (as it must be) — and the headline ratios are bound ratios.** Recomputed:
   η_lm = 1.21e6 → 1.23e6 nT·√µs from 5k to 640k (ratio 1.01), η_joint = 6.52e5 → 1.45e6
   (ratio **2.23**, i.e. *worse*). The joint estimator's own metric of record degrades by 2.2×
   between the lowest and highest budget. Any referee will read that as the model becoming biased
   at high SNR (see R1.1: at 640k the shared-envelope assumption costs 18 % vs the free-envelope
   fit), not as a sensitivity result.

### What would neutralise R3

Pre-register one primary budget (5k), one primary statistic (RMSE or σ-equivalent, with bias),
one region (all columns, or cols 7–40 declared in advance), and report the rest as exploratory
with CIs; give the reps-to-target-δB curve with bootstrap CIs on reps (not on δB); run the
tail comparison as a formal test; and report the 640k reversal as a falsification of the
shared-envelope model rather than as a footnote.

---

## R4 — Protocol honesty: does the joint estimator use time/data the classical one cannot?

### VERDICT: **SERIOUS** (fixable only by an explicit change of estimand)

Both estimators are handed all 40 columns; the classical one simply discards the cross-column
structure. So there is no *data* asymmetry. The asymmetry is in the **accounting**:

- `eta_*_ovh0` is computed with `t_total_us(r_lvl, 0.0)` and the default `n_cols=1`
  (`ladder_eval.py:26–28,92`). Each per-column δB is thus divided by √(one column's time) while
  the estimator that produced it borrowed information from 39 other columns (and, in the
  amortized case, from a prior trained on 6 other sheets). Under the constitution's literal
  definition — "t_total = the actual accumulation time of the data used by *that* estimate" —
  the pooled estimator consumed 40× the time, and its η is √40 = 6.3× worse than reported. Under
  the sweep interpretation (40 field values are the deliverable), the per-column accounting is
  fair and the result stands.
- The paper currently sits on the fence: it quotes the canonical *single-point* sensitivity
  η = δB√t (Taylor/Barry) while the estimator consumes a session. A referee will call this out.

Two related honesty gaps: (i) the estimators are given the field grid `B_nom` as the window
centre *and* the joint estimator is initialised at it and bounded to ±25 % of it (R1.4), so both
are measurement protocols for "a field already known to ±3 µT"; the abstract must say this; (ii)
`t_ovh` is not declared (R1.4).

### What would neutralise R4

Define a session-level figure of merit explicitly, e.g.
`η_session = median_c |B_hat_c − B_c| · √(t_session / N_points)` with `t_session` including
`t_ovh`, and show the classical baseline evaluated under the identical accounting. Also report
the single-point variant where the pooled method is *not* allowed (one column only), to show the
gain is genuinely a session-level effect.

---

## R5 — Novelty: is "pooling shared nuisance parameters across a session" new?

### VERDICT: **SERIOUS** (not a kill, but there is no paper in the current framing)

Pooling a shared nuisance across observations is standard hierarchical/empirical-Bayes
estimation, joint multi-trace fitting, and multi-task learning; the CRLB improvement from
sharing nuisance parameters is textbook. The measured effect is fully consistent with the bound
improvement (R1.2: 1.86× measured vs 1.90× bound at 5k), so a referee will correctly say
"this is the expected nuisance-pooling gain, where is the physics?".

The only genuinely interesting *scientific* content visible in the data is the **region × budget
structure**: the per-trace likelihood is degenerate for sub-cycle records (cols 1–6) and for
partially-cycled records (cols 7–12) at low repetition counts, and the degeneracy is broken by
the shared frame. That is a real, quantifiable identifiability statement — **but it is L1's**
(R7). What would make it publishable as L5: a quantitative *law* for when pooling pays, e.g.
"the per-trace estimation of the nuisance envelope consumes a fraction f(r, cycles) of the
Fisher information such that the sensitivity ratio is bounded by √((ν+1)/1)", validated on real
data and predictive of the crossover (measured crossover between 5k and 640k here); plus an
off-grid demonstration that the pooled method does not merely shrink toward a known grid. Without
the off-grid test the current effect is indistinguishable from shrinkage (R1.0).

---

## R6 — Venue

### VERDICT: **SERIOUS → FATAL if submitted as is**

What is on the table today: a real-data demonstration that a standard pooling estimator beats a
per-trace estimator by 1.4–2.6× on a metric that (i) an untrained network wins with 3.5 nT,
(ii) is floored by a 50–140 nT per-column instrument systematic above 160k reps, (iii) cannot be
significant at the primary budget after multiplicity, and (iv) is computed against the wrong CRLB.
There is no new physical insight, no new protocol, no new law, no hardware, and the neural
component is currently a uniform posterior (training loss pinned at ln 241). PRA/PRApplied/OL
will reject on significance/framing alone; the correct venue if it were cleaned up would be
Metrologia / Meas. Sci. Technol. / a statistics-of-measurement venue, and even there the pooling
result would need the off-grid and bias-corrected analysis to be novel.

---

## R7 — Anti-overlap with L1/L3/L4

### VERDICT: **FATAL**

L1 (`nv-research`) already claims, in `paper/main_v4.tex` (abstract, §Sensitivity, Fig. 3):

- "NV Ramsey magnetometry degrades sharply when fewer than one oscillation cycle fits in the
  measurement window: the likelihood flattens into a shallow plateau, and multi-start fits return
  errors that **do not improve with measurement time**" — i.e. the exact phenomenon L5 labels
  "estimator-limited at low photon budget";
- "Anchoring the phase and T2* … cuts the boundary-regime median error on 32 real traces from
  401 nT to 76 nT" — the shared-phase-frame mechanism, 5.3×, which L5 calls "pooling φ0";
- the sensitivity section with **η = δB√t on the same real data, the same 8 rep levels, the same
  boundary columns 3–6**, showing free LM's repetition-independent plateau and η ∝ √N, with the
  same CRLB ladder quoted ("analytic CRLB for B falls from 417 to 37 nT") — compare L5's
  `crlb_known` median 415.2 (5k) and 36.7 (640k);
- the shrinkage caveat in the abstract: "at sub-cycle fields the accuracy is **shrinkage to the
  calibrated basin, not information the marginal lacks**" — the exact caveat that invalidates
  L5's CRLB comparison, already published by the sibling line;
- L1's `LIVE_STATE.md` A3: "cols 1-2 unbiased CRLB = 1.38–92.6 µT … APCE 157 nT … narrower than
  the unbiased CRLB = biased estimator from prior shrinkage."
- L1's `CLAUDE.md`: "cols 3–6 … = ESTIMABLE BOUNDARY regime (the paper's target); cols 7+ (≥7.5 µT)
  classically solved — no ML claim."

The L5 kill log's defence is that L1's sensitivity section "used a √N proxy on cols 3–6, n = 4",
whereas L5 uses a proper `t_total` and n = 40. That is cosmetic: `t_total = r·Σ(τ+t_ovh)` is
*exactly proportional* to N, so η_L5 = δB√(cN) is the same proxy up to a constant. The only real
differences are n = 40 vs 4 and the within-sheet joint fit instead of an external anchor.

And the data say the effect is not a photon-budget effect at all. Splitting by region and rep
level (recomputed):

| r | gain cols 1–6 (lm/joint) | gain cols 7–40 |
|---|---|---|
| 5k | 9.57× | 1.44× |
| 10k | 6.05× | 1.82× |
| 20k | 11.94× | 1.77× |
| 40k | 5.36× | 2.61× |
| 80k | 6.29× | 2.00× |
| 160k | 2.75× | 1.26× |
| 320k | 10.05× | 1.66× |
| 640k | **7.16×** | **0.98×** |

The gain tracks the **fringe order** (column), not the photon budget: it is largest and roughly
constant at cols 1–6 across the *entire* 128× rep range including the highest budget, and it
vanishes at the highest budget in the region L5 claims as its own ("L1 declared solved"). A
low-photon-budget paper whose effect is strongest at the highest photon budget and absent in the
region it claims is not a low-photon-budget paper; it is L1's sub-cycle/boundary identifiability
story again. Additionally, the shared-φ0 term (1.44×/1.96×, R1.3) is L1's calibration result,
and the "envelope-only" ablation (1.29×/1.12×) that is supposed to establish independence has no
script or result file (R1.4).

### What would neutralise R7

Show an effect that (i) is confined to L1's declared-solved region (cols 7+), (ii) grows with
decreasing photon budget *within* that region (it currently does the opposite at 640k), and
(iii) survives with φ0 fixed externally to L1's published value and with the envelope supplied
from L1's published population rather than re-estimated within the sheet. Under that protocol the
residual gain is ~1.12× (10k) — below the pre-registered falsification threshold.

---

## Overall: **KILLED**

Not because the code is buggy (it is mostly careful), but because the three load-bearing claims
are each invalid on the team's own shipped data: the metric is gameable to 3.5 nT by an untrained
network; the "1.6–2.2× above the achievable bound" comparison uses the wrong CRLB for the
baseline and compares a median to a standard deviation (corrected: both estimators are ~1.2×
above their *own* bounds, and the pooling gain equals the bound improvement); and the effect's
dependence is on fringe order, not photon budget, in the exact region the sibling line L1 has
already claimed and published. Recommended disposition per the constitution: **pivot within the
direction** (W3 sensitivity-oriented training, or W4 atlas framed as an identifiability law) —
or, more honestly, fold the pooling result into L1 as its session-level analysis rather than
opening a fifth line.

### Three most dangerous points, in priority order

1. **R1.0 — an untrained network scores 3.5 nT on the headline metric** because the prior window
   is centred on the ground truth. Every number in the ladder is therefore an upper bound on
   "distance from the prior centre", not a measurement error. This invalidates the comparison
   harness wholesale and is trivially reproducible (`PosteriorNet()` with random weights,
   `predict`, `|B_hat − B_nom|`).
2. **R7 — the effect is a fringe-order/identifiability effect, not a low-photon-budget effect**,
   and L1 has already published the plateau, the 402→76 nT anchoring gain, the same CRLB ladder,
   and the shrinkage caveat. Gain at cols 1–6 is 7–12× at *every* rep level including 640k; gain
   at cols 7–40 collapses to 0.98× at 640k. The "L5 owns low budget on solved columns" claim is
   falsified by the repo's own JSON.
3. **R1.2/R3 — the quantitative claim ("classical is 1.6–2.2× above the bound; pooling recovers
   it") is a comparison error.** Per-trace LM must be compared to the free-envelope CRLB
   (`crlb_sigma_B_free_envelope`, 726 nT at 5k) and a median statistic to 0.674σ; against those
   both methods sit at ~1.17–1.19× of their own bounds, and the measured 1.86× equals the
   1.90× bound improvement from pooling. Also: 5k p = 0.014 fails the pre-registered p < 0.01 and
   Bonferroni (0.05/8); cols 7–40 alone give p = 0.143; cols 1–6 alone give p = 0.0625 with n = 6.
