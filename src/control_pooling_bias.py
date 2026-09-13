"""Mechanism control (synthetic, allowed for mechanism checks, NOT headline evidence).

Question: is the high-photon-budget deficit of session-pooled fitting a genuine
shared-model bias, or an artefact of the joint optimiser being worse?

Design: generate synthetic sessions at a chosen budget with KNOWN per-column B and
KNOWN per-column envelope variation (drawn from the real fitted population), then
compare per-trace LM vs pooled LM vs partial pooling. Ground truth exact => the
bias/variance decomposition is clean. The real-data ladder stays the headline; this
control only explains WHY the crossover exists.
"""
from __future__ import annotations

import json
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, ".")
from src.model import ramsey
from src.synth import gen_traces, sample_envelope, sigma_at

TAU_OFF = 0.0186


def fit_one(tau, y, B0, W=3214.2, n_starts=9):
    from src.baselines import lm_multistart
    r = lm_multistart(tau, y, B0 - W, B0 + W, n_starts=n_starts)
    return r["B"] if r else np.nan


def fit_pooled(tau, Y, B_init, shared_T2=True, tau_off_us=TAU_OFF, W=3214.2):
    ncol = Y.shape[1]

    def unpack(th):
        B = th[:ncol]
        if shared_T2:
            A, C, T2, p, phi0 = th[ncol:ncol + 5]
            T2v = np.full(ncol, T2)
        else:
            A, C, p, phi0 = th[ncol:ncol + 4]
            T2v = th[ncol + 4:ncol + 4 + ncol]
        return B, A, C, T2v, p, phi0

    def resid(th):
        B, A, C, T2v, p, phi0 = unpack(th)
        return np.concatenate([ramsey(tau, B[c], A, C, T2v[c], p, phi0, tau_off_us) - Y[:, c]
                               for c in range(ncol)])

    if shared_T2:
        x0 = np.concatenate([B_init, [0.127, 0.889, 5.4, 2.0, 0.0]])
        lo = np.concatenate([B_init - W, [0.02, 0.5, 3.0, 0.8, -np.pi]])
        hi = np.concatenate([B_init + W, [0.45, 1.2, 12.0, 4.0, np.pi]])
    else:
        x0 = np.concatenate([B_init, [0.127, 0.889, 2.0, 0.0], np.full(ncol, 5.4)])
        lo = np.concatenate([B_init - W, [0.02, 0.5, 0.8, -np.pi], np.full(ncol, 3.0)])
        hi = np.concatenate([B_init + W, [0.45, 1.2, 4.0, np.pi], np.full(ncol, 12.0)])
    r = least_squares(resid, x0, bounds=(lo, hi), max_nfev=400 * ncol)
    return r.x[:ncol]


def main(seed=0, n_rep=3):
    tau = 20e-3 * np.arange(1, 301)  # us
    rng = np.random.default_rng(seed)
    rows = []
    for reps in [5000, 10000, 40000, 160000, 640000]:
        sig = sigma_at(reps)
        errs = {"lm": [], "pool_full": [], "pool_partial": []}
        for _ in range(n_rep):
            B_true = 1071.4 * rng.integers(1, 41, size=40).astype(float)
            env = sample_envelope(rng, 40)            # per-column envelope (real spread)
            Y = gen_traces(tau, B_true, env, sig, rng)  # (n_cols, n_tau)
            W = 3214.2
            errs["lm"].append(np.abs(np.array([fit_one(tau, Y[c], B_true[c], W)
                                               for c in range(40)]) - B_true))
            errs["pool_full"].append(np.abs(fit_pooled(tau, Y.T, B_true, True) - B_true))
            errs["pool_partial"].append(np.abs(fit_pooled(tau, Y.T, B_true, False) - B_true))
        row = {"reps": int(reps), "sigma": float(sig)}
        for k, v in errs.items():
            e = np.concatenate(v)
            row[k] = {"median": float(np.median(e)), "mean": float(np.mean(e)),
                      "rmse": float(np.sqrt(np.mean(e ** 2))),
                      "q25": float(np.percentile(e, 25)),
                      "q75": float(np.percentile(e, 75))}
        rows.append(row)
        print(f"r={reps:>7}: lm med={row['lm']['median']:7.1f} | "
              f"pool_full med={row['pool_full']['median']:7.1f} | "
              f"pool_partial med={row['pool_partial']['median']:7.1f}", flush=True)
    json.dump({"note": "synthetic mechanism control (not headline evidence)",
               "seed": seed, "n_rep": n_rep, "rows": rows},
              open("results/control_pooling_bias.json", "w"), indent=2)
    print("wrote results/control_pooling_bias.json")


if __name__ == "__main__":
    main()
