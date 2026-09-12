"""Prior-window sweep: how does classical per-trace fitting degrade when the field is
less well known a priori? Decides whether a learned/structured estimator has a real
advantage beyond the pooled-LM classical implementation.

Task is unchanged (estimate B from the same full 300-point real trace); only the prior
width changes. The estimator may use the window; nothing else changes.
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, ".")
from src.baselines import lm_multistart
from src.data_pipeline import REP_LEVELS, load_dc

GRID = 1071.4
WINDOWS = [3, 6, 10, 20]  # in grid steps
OUT = "results/window_sweep.json"


def main(sheets=(0, 1)):
    ds = load_dc()
    tau = ds.tau_us
    ref = np.array(json.load(open("results/reference_B_sheet8.json"))["B_ref"])
    res = {}
    for si in sheets:
        Y = ds.signal[si]
        Bn = ds.B_nT
        for w in WINDOWS:
            W = w * GRID
            t0 = time.time()
            # scale starts with window size so the classical method is not starved
            n_starts = {3: 25, 6: 49, 10: 64, 20: 81}[w]
            B = np.full(40, np.nan)
            for c in range(40):
                lo, hi = max(200.0, Bn[c] - W), Bn[c] + W
                r = lm_multistart(tau, Y[:, c], lo, hi, n_starts=n_starts)
                if r:
                    B[c] = r["B"]
            e_nom = np.abs(B - Bn)
            e_ref = np.abs(B - ref)
            res[f"sheet{si+1}_w{w}"] = {
                "reps": int(REP_LEVELS[si]), "window_nT": W, "n_starts": n_starts,
                "median_err_nom": float(np.nanmedian(e_nom)),
                "mean_err_nom": float(np.nanmean(e_nom)),
                "median_err_ref": float(np.nanmedian(e_ref)),
                "frac_within_500": float(np.mean(e_nom < 500)),
                "frac_within_1000": float(np.mean(e_nom < 1000)),
                "max_err_nom": float(np.nanmax(e_nom)),
                "B_hat": np.round(B, 1).tolist(),
                "wall_s": time.time() - t0,
            }
            r = res[f"sheet{si+1}_w{w}"]
            print(f"sheet{si+1} r={int(REP_LEVELS[si]):>6} window=±{W:7.0f} nT "
                  f"({w:2d} steps): med={r['median_err_nom']:7.1f} mean={r['mean_err_nom']:7.1f} "
                  f"<500={r['frac_within_500']*100:3.0f}% <1000={r['frac_within_1000']*100:3.0f}% "
                  f"max={r['max_err_nom']:8.0f} ({r['wall_s']:.0f}s)", flush=True)
            json.dump(res, open(OUT, "w"), indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
