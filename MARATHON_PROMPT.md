# Marathon Prompt (mission order — CLAUDE.md is the constitution)

```
/research-pipeline "Run nv-research4 — NV×AI line #5, direction LOCKED by user: estimate
high-precision magnetic field B from LOW-SNR Ramsey data (few repetitions / low photon
budget); evaluation metric = sensitivity eta = deltaB * sqrt(t_total) — must minimize
BOTH estimate uncertainty and total experimental accumulation time of the data used.
GOAL: an innovative POSITIVE-result paper (AI×NV, physics journal). READ CLAUDE.md FIRST
— it defines the metric protocol (eta curves across the 8-rep ladder, time-overhead
scenarios 0.5x/1x/2x), the anti-overlap gate vs L1 (boundary+calibration-anchor+UQ —
eta is the shared instrument's prior discovery, cite only), L3/L4 (sparse dwell design —
FORBIDDEN territory; L5 keeps the full 300-point sweep and varies only the photon budget),
the G-Pos feasibility gate (a pre-registered minimal pilot on Sheet1-2 5k/10k showing an
honest positive: e.g., reaching deltaB* with X reps where classical needs Y× more,
p<0.01, >=3 seeds; pivot if absent; NEVER manufacture positivity), and data rules (REAL
data_lab mandatory in all evaluation — copy from nv-research/old/ttmnv2_old/data_lab;
synthetic allowed for training only, anchored to real parameter/noise scenarios). LOCKED
conventions: B nT, gamma=2*pi*28e-6 rad/(us*nT), tau=20n ns, Gaussian decay, tau_off
~18.6 ns correction (cite L1's confirm_tau_off). Phase 0-1 (0 GPU): deep survey +
>=5 candidates (>=3 fresh) + CANDIDATE_KILL_LOG + scoop check (ML-for-NV,
few-shot/photon-efficient magnetometry, sensitivity-oriented estimation) + adversarial
R1-R7 (incl. R7 'is this just L1/L3/L4?') + the G-Pos pilot + 6-dim scoring (>=26/30,
AI-novelty >=4) -> PHASE0/PHASE1_DECISION committed. Rigor: unified eval, frozen audited
splits, >=5 seeds for learned methods, paired Wilcoxon + bootstrap CI, provenance rows
for every number, PAPER_CLAIM_AUDIT before submission-ready. Compute: jindun work dir
/data_3/repo/nv-research4 ONLY; DYNAMIC GPU check before every launch (any card with a
foreign process is off-limits regardless of index; verify owners via /proc/<pid>/cwd;
coordinate with L1 line; release GPUs after runs); local RTX 5060 smoke only. GitHub:
https://github.com/hxm2023/nv-research4 (code/JSON only; lab raw data not uploaded
without confirmation). Timeline: Phase 0-1 in ~2 weeks, decisions committed; ask user
before scope changes/journal choice." --deep_mode: true, auto_write: true,
auto_proceed: true, venue: "physics journal (PRA/PRApplied/OL class)", arxiv_download: true
```
