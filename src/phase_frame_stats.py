"""Circular statistics of the instrument phase frame phi0 across the 40 field columns,
per repetition level. Produces results/phase_frame_stats.json so the paper's claim about
a shared phase frame has a provenance file.

Method: fix each column's own envelope to its high-budget fit, then fit (B, phi0) per
column; the circular concentration |R| = |mean(exp(i phi0))| measures how common the
phase is across columns (|R| -> 1 means one shared instrument phase).
"""
from __future__ import annotations

import json
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, ".")
from src.data_pipeline import REP_LEVELS, load_dc
from src.model import ramsey

TAU_OFF = 0.0186


def main():
    ds = load_dc()
    tau = ds.tau_us
    env = np.array(json.load(open("results/envelope_sheet8.json"))["env_sheet8"])
    out = {"method": "per-column (B, phi0) fit with that column's own envelope fixed",
           "sheets": {}}
    for si, r in enumerate(REP_LEVELS):
        phis = []
        for c in range(40):
            A, C, T2, p, _ = env[c]
            y = ds.signal[si][:, c]
            B0 = ds.B_nT[c]

            def resid(th, y=y, A=A, C=C, T2=T2, p=p, B0=B0):
                return ramsey(tau, th[0], A, C, T2, p, th[1], TAU_OFF) - y

            r_ = least_squares(resid, [B0, 0.0],
                               bounds=([B0 - 3214.2, -20], [B0 + 3214.2, 20]),
                               max_nfev=800)
            phis.append(float(r_.x[1]))
        phis = np.array(phis)
        z = np.exp(1j * phis).mean()
        R = float(np.abs(z))
        out["sheets"][f"sheet{si+1}"] = {
            "reps": int(r),
            "phi0_mean_rad": float(np.angle(z)),
            "circular_concentration": R,
            "circular_std_rad": float(np.sqrt(-2 * np.log(max(R, 1e-9)))),
            "phi0_values": [round(x, 4) for x in phis],
        }
        print(f"sheet{si+1} r={int(r):>7}: |R|={R:.4f}  mean phi0={np.angle(z):+.4f} rad  "
              f"circ std={np.sqrt(-2*np.log(max(R,1e-9))):.3f} rad", flush=True)
    json.dump(out, open("results/phase_frame_stats.json", "w"), indent=2)
    print("wrote results/phase_frame_stats.json")


if __name__ == "__main__":
    main()
