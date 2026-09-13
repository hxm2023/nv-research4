"""Block-wise referee review of the manuscript via the DashScope (qwen3.8-max) API.

The single large request never returned; small requests return in seconds, so the review
is split into three independently submittable blocks. Usage:
    python tools_codex_review_blocks.py neural
    python tools_codex_review_blocks.py figures
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))


def expand(tex: str, numbers: str) -> str:
    macros = dict(re.findall(r"\\newcommand\{\\([a-zA-Z]+)\}\{([^}]*)\}", numbers))
    for _ in range(3):
        tex = re.sub(r"\\([a-zA-Z]+)", lambda m: macros.get(m.group(1), m.group(0)), tex)
    return tex


def ladder_table():
    a = json.load(open(os.path.join(ROOT, "results", "analysis_v2.json")))
    T = a["tables"]["cols7_40"]
    d = json.load(open(os.path.join(ROOT, "results", "blind_res_nets.json")))
    ds_B = 1071.4
    import numpy as np
    runs = [r for r in d["runs"] if r["kind"] == "set" and r["steps"] == 30000]
    rows = ["r | lm | pool | partial | net(5 seeds)"]
    for k in sorted(T, key=lambda x: int(x[1:])):
        si = int(k[1:]) // 5000
        i = {5000: 0, 10000: 1, 20000: 2, 40000: 3, 80000: 4, 160000: 5,
             320000: 6, 640000: 7}[int(k[1:])]
        Bt = ds_B * np.arange(1, 41)
        net = np.median([np.sqrt(np.mean(((np.array(r["real"][f"sheet{i+1}"]["B_hat"]) - Bt)[6:40]) ** 2))
                         for r in runs])
        g = lambda m: T[k].get(m, {}).get("rmse", float("nan"))
        rows.append(f"{k[1:]} | {g('lm_refine'):.0f} | {g('joint_refine'):.0f} | "
                    f"{g('partial_pool'):.0f} | {net:.0f}")
    return "\n".join(rows)


BLOCKS = {
    "neural": """Strict physics-journal referee. Focus ONLY on the machine-learning component
of this study and on claim-evidence fidelity. Under 700 words.

SETTING: real NV-diamond Ramsey data, 8 repetition levels (5e3 to 6.4e5), 40 field settings,
full 300-point delay sweep, one session on one instrument. Six-parameter per-trace
maximum-likelihood fitting is efficient against its own free-envelope Cramer-Rao bound.
Pooling a shared relaxation envelope and phase frame across the 40 field settings lowers the
bound by 1.8x but introduces a bias floor of 156 nT from measured envelope inhomogeneity
(T2* = 5.40 +- 0.29 us); the two fit deltaB(r) = sqrt(A^2*(5000/r) + b^2) with A = 785,
b = 28 nT (per-trace) and A = 417, b = 156 nT (pooled), crossing at r* = 9e4 repetitions
(95% CI 4.9e4 - 1.3e5 by column bootstrap). A synthetic control with exact ground truth
reproduces the crossover.

THE NEURAL ESTIMATOR: a spectral trunk (windowed rFFT magnitude, log-magnitude and
unit-normalised real/imaginary parts of the same trace) plus a permutation-invariant
attention block over the 40 columns, outputting a 512-bin posterior over a correction to the
trace's own blind FFT+Rife estimate (+-8 uT). Trained by cross-entropy on instrument-anchored
synthetic sessions (envelope drawn from the measured population, per-column T2*, one shared
phase frame per session, measured shot-noise law, blind uniformly distributed fields); five
seeds; median over seeds reported.

MEASURED RMSE (nT), columns 7-40:
{rung}

QUESTIONS (answer each, citing the numbers):
1. The network is worse than classical pooling at 5k-40k and best of all methods at
   80k-320k. Is that a meaningful budget-dependent-sharing behaviour or an undertrained-model
   artefact? What specific evidence would separate the two explanations?
2. The network is conditioned on the noise level (log sigma) but never told the instrument
   model structure or which parameters are shared. Is the claim 'structure-free
   budget-adaptive inference' supported by the numbers above?
3. Is the synthetic training set (built from the measured envelope population and noise law,
   with no real low-budget traces) adequate, or does it risk a simulation-to-reality gap that
   the evaluation would not reveal? What check would you demand?
4. Does the paper overstate the neural contribution anywhere? Quote the weakest claim you can
   find and rewrite it in a form the data support.
""",
    "figures": """Strict physics-journal referee, FIGURES AND PRESENTATION only. Under 700 words.

The manuscript has five figures (two-column ca. 8.6 cm wide, revtex):
F1 two panels sharing an x axis: (a) field RMSE vs repetitions per delay point for four
   estimators (per-trace LM, pooled shared-envelope, pooled per-column T2*, amortized
   network) with percentile bootstrap error bars, the fitted two-term floor law as curves,
   a vertical line at the crossover r* = 9e4 and a shaded strip marking the lowest measured
   budget; (b) signed bias vs the same x axis on a linear scale.
F2 full width, two panels: left, the two Cramer-Rao bounds (free-envelope vs joint) with the
   1.8x gap shaded; right, each estimator's RMSE divided by its own bound.
F3 synthetic control with exact ground truth: median |dB| vs repetitions for per-trace,
   full pooling and partial pooling.
F4 five histograms: the relaxation envelope parameters across the 40 field columns
   (contrast, offset, T2* with sigma/mu = 5%, stretch p with a 'bound' arrow at the
   saturated value 4.0, and phase phi0 with its circular standard deviation).
F5 sensitivity eta = dB*sqrt(t_total) vs repetitions for per-trace and pooled inference,
   with a shaded band for the per-point overhead t_ovh between 0.5 and 2 us.

QUESTIONS:
1. Is this the right figure set for the claim (a photon-budget-dependent crossover in the
   optimal estimation strategy)? What is redundant, what is missing?
2. Are any of the five potentially misleading? In particular: F1 mixes bootstrap error bars
   over 34 field columns (which are not independent experimental replications, since all
   columns come from ONE session on ONE instrument) with the interquartile spread over
   training seeds for the network - is that defensible, and how should it be presented?
3. F3 uses medians while F1 uses RMSE. Is that inconsistency acceptable if the caption says
   so, or should it be unified?
4. What single additional panel or figure would most strengthen the paper for a physics
   referee? Be concrete about what it should plot.
5. Comment on axis choices (log-log where the physics is a power law, linear for bias) and
   on whether the crossover annotation is clear enough to be read without the caption.
""",
}


def main():
    block = sys.argv[1]
    prompt = BLOCKS[block].format(**{"rung": ladder_table()})
    key = os.environ["DASHSCOPE_API_KEY"]
    body = json.dumps({"model": "qwen3.8-max", "input": prompt}).encode()
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/responses",
        data=body, headers={"Authorization": f"Bearer {key}",
                            "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        out = json.load(r)
    text = "\n".join(c["text"] for item in out.get("output", [])
                     if item.get("type") == "message"
                     for c in item.get("content", []) if c.get("type") == "output_text")
    p = os.path.join(ROOT, "review-stage", f"CODEX_REVIEW_{block}.md")
    open(p, "w", encoding="utf-8").write(f"# Referee review block: {block}\n\n{text}\n")
    print(f"wrote {p} ({len(text)} chars)\n")
    print(text[:2500])


if __name__ == "__main__":
    main()
