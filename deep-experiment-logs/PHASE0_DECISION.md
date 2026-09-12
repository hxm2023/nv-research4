# PHASE 0 DECISION — L5 (nv-research4)

**Date**: 2026-09-12 · **Decision**: PROCEED to Phase 1 gate (G-Pos) · **Compute spent**: 0 GPUh on jindun (local smoke only)

## Decision

Build the Phase-0 knowledge base and run the deep survey for the L5 cell
("low photon budget + FULL 300-point τ sweep + sensitivity-optimal estimation of B,
metric η = δB·√t_total"). Verified: the cell is **unoccupied**, its four walls have
neighbours, and the neighbour distance can be stated explicitly.

## Evidence

1. **Knowledge base built** (`research-wiki/knowledge_base/`):
   - `domain_overview.md` (429 lines, 32 verified references) — landscape, standard
     methods, sensitivity definitions, active directions, venues, and an explicit
     "open gaps" section.
   - `metrics_and_baselines.md` (309 lines) — metric definitions (δB, η, CRLB, coverage,
     failure rate), SOTA + classical + learned baselines with real citations, evaluation
     protocols, CRLB notes.
   - `field_conventions.md` (365 lines) — plot types, notation/units, reporting
     conventions, physics-journal paper structure, reviewer expectations.
   - `search.py` + `index.json` — keyword search over the KB; `papers/` populated by the
     arXiv download pass (see `papers/_download_log.json`).
2. **Scoop check** (`SCOOP_CHECK_2026-09-12.md`): 37 web queries + an independent raw
   arXiv-API sweep. Verdict **SAFE (qualified)** — no paper occupies the cell. Nearest
   misses: NVRNet (arXiv:2603.14144, few-sweep Ramsey but ¹³C hyperfine parameters, no
   δB/η, no classical matched-budget comparison), NCSU BNN (arXiv:2506.13469 /
   2512.11300, amortized BNN but on adaptive/sparse τ selection — L3/L4 territory — MSE
   metric), arXiv:2608.23934 (information-theoretic counter-argument, must be answered).
3. **Cell geometry confirmed**: the low-photon axis and the full-sweep axis are attacked
   separately in the literature, never jointly; the metric is almost never the headline;
   real-data learned B-estimators are thin and the sim-to-real gap is the recognised
   blocker — which is precisely where an instrument-anchored prior has leverage.

## Alternative rejected

Skipping Phase 0 because "the constitution already fixes the direction". Rejected: the
survey produced two facts that changed the plan — (a) the classical per-trace estimators
are already near their own free-envelope CRLB, so the only honest headroom is structural
(shared nuisance), and (b) ¹³C/NVRNet-style work uses acquisition-time reduction as its
headline, so L5 must differentiate on the *estimator-limited sensitivity* framing and
must not claim acquisition-time reduction as if it were new.

## Why not other cells (anti-overlap)

- Sparse/adaptive τ design — L3 (archived) + L4 (submitted) own it; forbidden by the
  constitution.
- Calibration anchoring as a discovery — L1 owns τ_off/φ0; L5 cites it as a convention.
- Speed of inference — forbidden as a headline by the constitution.

## Falsification

If the raw arXiv sweep or the adversarial round surfaces a paper that benchmarks
estimator-limited η(δB, t_total) on a full real sweep with matched-budget classical
baselines, Phase 1 stops and the direction pivots (cost: 0 GPUh).

## Cost / next

Cost: 0 GPUh on jindun; local CPU + RTX-5060 smoke only. Next: Phase 1 — candidate
generation, adversarial gate R1-R7, and the G-Pos pilot (see `G_POS_PILOT_REPORT.md`).
