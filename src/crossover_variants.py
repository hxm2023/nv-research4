"""Crossover r* for each pooled-model variant (referee round-2, item 1).

For every variant of the shared model we fit the same two-term law to the full 8-level
ladder on real columns 7-40 and solve for the crossover against the per-trace ladder:

    deltaB(r) = sqrt(A^2 * (5000/r) + b^2),   r* = 5000 (A_lm^2 - A_var^2) / b_var^2

Variants: all shared (A, C, p, phi0, T2* shared), T2* per column (the paper's partial
pooling), contrast A per column, stretch p per column. The per-trace ladder is the
reference in every case.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, ".")
from src.data_pipeline import REP_LEVELS, load_dc
from src.robustness_checks import fit_law, pooled_fit

OUT = "results/crossover_variants.json"
VARIANTS = {"all shared": (), "T2 per column": ("T2",), "A per column": ("A",),
            "p per column": ("p",)}


def main():
    ds = load_dc()
    tau = ds.tau_us
    Bt = ds.B_nT[6:40]
    res = json.load(open(OUT)) if os.path.exists(OUT) else {"variants": {}}
    reps = np.array(REP_LEVELS, dtype=float)

    # per-trace reference ladder
    ev = json.load(open("results/blind_eval.json"))["sheets"]
    lm_ladder = np.array([np.sqrt(np.mean((np.array(ev[f"sheet{si+1}"]["lm_refine"])
                                           - ds.B_nT)[6:40] ** 2)) for si in range(8)])
    A_lm, b_lm = fit_law(reps, lm_ladder)
    res["per_trace"] = {"A_nT": A_lm, "floor_nT": b_lm, "ladder": lm_ladder.tolist()}
    print(f"per-trace: A={A_lm:.1f} b={b_lm:.1f}", flush=True)

    for tag, free in VARIANTS.items():
        if tag in res["variants"]:
            continue
        t0 = time.time()
        ladder = []
        for si in range(8):
            Y = ds.signal[si][:, 6:40]
            from src.blind_eval import fft_blind
            Bf = np.array([fft_blind(tau, Y[:, c]) for c in range(Y.shape[1])])
            B = pooled_fit(tau, Y, Bf, free=free)
            ladder.append(float(np.sqrt(np.mean((B - Bt) ** 2))))
        ladder = np.array(ladder)
        A, b = fit_law(reps, ladder)
        rstar = (5000.0 * (A_lm**2 - A**2) / b**2) if (A_lm > A and b > 0) else float("nan")
        res["variants"][tag] = {"A_nT": A, "floor_nT": b, "ladder": ladder.tolist(),
                                "crossover_reps": rstar, "wall_s": time.time() - t0}
        json.dump(res, open(OUT, "w"), indent=2)
        print(f"{tag:>14}: A={A:8.1f} b={b:7.1f}  r*={rstar:,.0f}  "
              f"({time.time()-t0:.0f}s)", flush=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
