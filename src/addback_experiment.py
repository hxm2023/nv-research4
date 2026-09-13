"""Add-back experiment (referee round 3, item 2).

Start from the primary-region session (columns 7-40) and add the sub-cycle settings back one
at a time, from the most identifiable of them (column 6) to the least (column 1). For each
session we refit the pooled model on every sheet, fit the two-term law and report A, b, r*.
A continuous degradation shows the effect is governed by identifiability rather than by an ad
hoc exclusion of exactly six columns.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, ".")
from src.blind_eval import fft_blind
from src.data_pipeline import REP_LEVELS, load_dc
from src.robustness_checks import fit_law, pooled_fit

OUT = "results/addback_experiment.json"


def main():
    ds = load_dc()
    tau = ds.tau_us
    reps = np.array(REP_LEVELS, dtype=float)
    ev = json.load(open("results/blind_eval.json"))["sheets"]
    lm = np.array([np.sqrt(np.mean((np.array(ev[f"sheet{s+1}"]["lm_refine"]) - ds.B_nT)[6:40] ** 2))
                   for s in range(8)])
    A_lm, b_lm = fit_law(reps, lm)
    out = json.load(open(OUT)) if os.path.exists(OUT) else {
        "per_trace": {"A": A_lm, "b": b_lm}, "sessions": {}}

    # add back in order of decreasing single-trace identifiability (6 first, 1 last)
    order = [6, 5, 4, 3, 2, 1]
    for k in range(len(order) + 1):
        cols = list(range(6, 40)) + order[:k]
        tag = f"n{len(cols)}"
        if tag in out["sessions"]:
            continue
        t0 = time.time()
        ladder = []
        for s in range(8):
            Y = ds.signal[s][:, cols]
            Bf = np.array([fft_blind(tau, Y[:, c]) for c in range(len(cols))])
            B = pooled_fit(tau, Y, Bf)
            Bt = ds.B_nT[cols]
            ladder.append(float(np.sqrt(np.mean((B - Bt) ** 2))))
        A, b = fit_law(reps, np.array(ladder))
        rstar = 5000 * (A_lm**2 - A**2) / b**2 if (A_lm > A and b > 0) else float("nan")
        out["sessions"][tag] = {"n_cols": len(cols), "added": order[:k],
                                "ladder": ladder, "A_nT": A, "floor_nT": b,
                                "crossover_reps": rstar, "wall_s": time.time() - t0}
        json.dump(out, open(OUT, "w"), indent=2)
        print(f"{tag:>4} ({len(cols)} settings, added {order[:k]}): "
              f"A={A:7.1f} b={b:6.1f} r*={rstar:,.0f}  ({time.time()-t0:.0f}s)", flush=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
