"""Blind partial-pooling baseline (the strongest classical comparator).

Shares the phase frame and the contrast/offset/stretch across the session but lets each
column keep its own T2* - the structure that matches the real instrument (T2* spread
5.40 +- 0.29 us measured). Initialised blind from the same FFT+Rife estimate as every
other method, so it has no setpoint information.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, ".")
from src.blind_eval import fft_blind
from src.data_pipeline import REP_LEVELS, load_dc
from src.model import ramsey

TAU_OFF = 0.0186
OUT = "results/blind_partial_pool.json"


def partial_pool(tau, Y, B_init, tau_off_us=TAU_OFF):
    ncol = Y.shape[1]
    W = np.array([max(3 * 1071.4, 0.05 * b) for b in B_init])

    def unpack(th):
        B = th[:ncol]
        A, C, p, phi0 = th[ncol:ncol + 4]
        T2 = th[ncol + 4:ncol + 4 + ncol]
        return B, A, C, T2, p, phi0

    def resid(th):
        B, A, C, T2, p, phi0 = unpack(th)
        return np.concatenate([ramsey(tau, B[c], A, C, T2[c], p, phi0, tau_off_us) - Y[:, c]
                               for c in range(ncol)])

    x0 = np.concatenate([B_init, [0.127, 0.889, 2.0, 0.0], np.full(ncol, 5.4)])
    lo = np.concatenate([np.maximum(500, B_init - W), [0.02, 0.5, 0.8, -np.pi],
                         np.full(ncol, 2.5)])
    hi = np.concatenate([np.minimum(45000, B_init + W), [0.45, 1.2, 4.0, np.pi],
                         np.full(ncol, 15.0)])
    r = least_squares(resid, x0, bounds=(lo, hi), max_nfev=400 * ncol)
    return r.x[:ncol]


def main():
    ds = load_dc()
    tau = ds.tau_us
    res = json.load(open(OUT)) if os.path.exists(OUT) else {"sheets": {}}
    for si in range(8):
        key = f"sheet{si+1}"
        if key in res["sheets"]:
            continue
        Y = ds.signal[si]
        B_fft = np.array([fft_blind(tau, Y[:, c]) for c in range(40)])
        t0 = time.time()
        B = partial_pool(tau, Y, B_fft)
        res["sheets"][key] = {"reps": int(REP_LEVELS[si]),
                              "B_hat": np.round(B, 1).tolist(),
                              "wall_s": time.time() - t0}
        e = np.abs(B - ds.B_nT)
        print(f"{key} r={int(REP_LEVELS[si]):>7}: med={np.median(e):7.1f} "
              f"rmse={np.sqrt(np.mean(e**2)):7.1f} "
              f"(cols7-40: med={np.median(e[6:]):.1f} rmse={np.sqrt(np.mean(e[6:]**2)):.1f}) "
              f"{time.time()-t0:.0f}s", flush=True)
        json.dump(res, open(OUT, "w"), indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
