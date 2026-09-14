"""Regenerate results/session_table.json: the pooled-model laws under two session
definitions (primary region = columns 7-40; full sweep = all 40 settings) and two sharing
patterns (all shared; T2* per column). Produces the numbers in the manuscript's Table II
and the surrounding text.

Usage: python -m src.session_table
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, ".")
from src.blind_eval import fft_blind
from src.data_pipeline import REP_LEVELS, load_dc
from src.robustness_checks import fit_law, pooled_fit

OUT = "results/session_table.json"


def ladder_for(ds, cols, free, score_cols=slice(6, 40)):
    """RMSE ladder (one value per repetition level) over the real sheets."""
    tau = ds.tau_us
    lad = []
    for si in range(8):
        Y = ds.signal[si][:, cols]
        Bf = np.array([fft_blind(tau, Y[:, c]) for c in range(len(cols))])
        B = pooled_fit(tau, Y, Bf, free=free)
        e = (B - ds.B_nT[cols])
        m = np.ones(len(cols), dtype=bool)
        if cols == list(range(40)):
            keep = [c for c in cols if c not in range(6)]
            m = np.isin(cols, keep)
        lad.append(float(np.sqrt(np.mean(e[m] ** 2))))
    return lad


def main():
    ds = load_dc()
    reps = np.array(REP_LEVELS, dtype=float)
    ev = json.load(open("results/blind_eval.json"))["sheets"]
    lm = np.array([np.sqrt(np.mean((np.array(ev[f"sheet{s+1}"]["lm_refine"]) - ds.B_nT)[6:40] ** 2))
                   for s in range(8)])
    A_lm, b_lm = fit_law(reps, lm)

    out = {"per_trace": {"A": A_lm, "b": b_lm, "ladder": lm.tolist()}}

    def add(key, cols, free):
        lad = ladder_for(ds, cols, free)
        A, b = fit_law(reps, np.array(lad))
        r = 5000 * (A_lm**2 - A**2) / b**2 if (A_lm > A and b > 0) else float("nan")
        out[key] = {"cols": cols[0] + 1, "n_cols": len(cols),
                    "A": A, "b": b, "rstar": r, "ladder": lad}
        print(f"{key:28s}: n={len(cols):2d}  A={A:7.1f}  b={b:6.1f}  r*={r:,.0f}", flush=True)

    add("primary_all_shared", list(range(6, 40)), ())
    add("primary_T2_free", list(range(6, 40)), ("T2",))
    add("full_sweep_40", list(range(40)), ())
    add("full_sweep_40_T2free", list(range(40)), ("T2",))
    json.dump(out, open(OUT, "w"), indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
