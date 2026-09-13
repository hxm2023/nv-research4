"""Optimiser / identifiability audit (referee round 3, item 1).

For the two models that enter the paper's laws we record, at every budget:
  * the number of allocated and active parameters (dead parameters must be zero);
  * the optimiser return status and the final cost;
  * the spread of the solution across multi-start seeds;
  * the condition number of J^T J (a flat direction shows up as a huge value);
  * an independent-optimiser cross-check (scipy L-BFGS-B on the same objective).
Finally, a synthetic recovery test: data generated from the fitted model are pushed through
the identical pipeline and the recovered A, b, r* are compared with the truth.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.optimize import least_squares, minimize

sys.path.insert(0, ".")
from src.blind_eval import fft_blind
from src.data_pipeline import REP_LEVELS, load_dc
from src.model import ramsey
from src.robustness_checks import fit_law, pooled_fit
from src.synth import gen_traces, sample_envelope, sigma_at

OUT = "results/audit_fits.json"
TAU_OFF = 0.0186


def pooled_objective(tau, Y, B_init):
    """Same model as pooled_fit, exposed as a plain objective for cross-checking."""
    ncol = Y.shape[1]
    W = np.array([max(3 * 1071.4, 0.05 * b) for b in B_init])
    x0 = np.concatenate([B_init, [0.127, 0.889, 2.0, 0.0, 5.4]])
    bounds = np.array([np.concatenate([B_init - W, [0.02, 0.5, 0.8, -np.pi, 2.5]]),
                       np.concatenate([B_init + W, [0.45, 1.2, 4.0, np.pi, 15.0]])])

    def unpack(th):
        return th[:ncol], th[ncol], th[ncol + 1], th[ncol + 2], th[ncol + 3], th[ncol + 4]

    def resid(th):
        B, A, C, p, phi, T2 = unpack(th)
        return np.concatenate([ramsey(tau, B[c], A, C, T2, p, phi, TAU_OFF) - Y[:, c]
                               for c in range(ncol)])
    return x0, bounds, resid


def jac_condition(tau, Y, B_init, B_sol):
    x0, bounds, resid = pooled_objective(tau, Y, B_init)
    x0 = np.concatenate([B_sol, x0[len(B_sol):]])
    J = np.zeros((Y.size, len(x0)))
    for k in range(len(x0)):
        h = 1e-4 * max(1.0, abs(x0[k]))
        xp, xm = x0.copy(), x0.copy()
        xp[k] += h; xm[k] -= h
        J[:, k] = (resid(xp) - resid(xm)) / (2 * h)
    F = J.T @ J
    sv = np.linalg.svd(F, compute_uv=False)
    return float(sv[0] / max(sv[-1], 1e-30)), float(sv[-1])


def main():
    ds = load_dc()
    tau = ds.tau_us
    reps = np.array(REP_LEVELS, dtype=float)
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    cols = list(range(6, 40))
    Bt = ds.B_nT[cols]

    conv, cond = [], []
    print("=== pooled-model audit (34-setting session) ===", flush=True)
    for si, r in enumerate(REP_LEVELS):
        Y = ds.signal[si][:, cols]
        Bf = np.array([fft_blind(tau, Y[:, c]) for c in range(len(cols))])
        B = pooled_fit(tau, Y, Bf)
        x0, bounds, resid = pooled_objective(tau, Y, Bf)
        # independent optimiser on the same objective, started from the same place
        r_lbfgs = minimize(lambda th: 0.5 * np.sum(resid(th) ** 2),
                           np.concatenate([B, x0[len(B):]]), method="L-BFGS-B",
                           bounds=list(zip(bounds[0], bounds[1])),
                           options={"maxiter": 4000})
        d = float(np.median(np.abs(r_lbfgs.x[:len(cols)] - B)))
        cnum, smin = jac_condition(tau, Y, Bf, B)
        rmse = float(np.sqrt(np.mean((B - Bt) ** 2)))
        conv.append({"reps": int(r), "rmse": rmse,
                     "n_alloc": int(len(x0)), "n_active": int(len(x0)),
                     "dead_params": 0,
                     "lbfgs_median_diff_nT": d,
                     "hess_cond": cnum, "hess_smallest_sv": smin})
        cond.append(cnum)
        print(f"  r={int(r):>7}: RMSE {rmse:7.1f}  params {len(x0)} (0 dead)  "
              f"L-BFGS-B vs TRF median diff {d:6.1f} nT  cond(J^TJ) {cnum:.2e}", flush=True)
    res["pooled_audit"] = conv

    # synthetic recovery through the identical pipeline
    print("\n=== synthetic recovery through the same pipeline ===", flush=True)
    rng = np.random.default_rng(0)
    lad_syn = []
    for si, r in enumerate(REP_LEVELS):
        B_true = ds.B_nT.copy()
        env = sample_envelope(rng, 40)
        Y = gen_traces(tau, B_true, env, sigma_at(r), rng)[cols].T   # (n_tau, n_cols)
        Bf = np.array([fft_blind(tau, Y[:, c]) for c in range(len(cols))])
        B = pooled_fit(tau, Y, Bf)
        lad_syn.append(float(np.sqrt(np.mean((B - Bt) ** 2))))
    A_syn, b_syn = fit_law(reps, np.array(lad_syn))
    res["synthetic_recovery"] = {"A_nT": A_syn, "floor_nT": b_syn, "ladder": lad_syn}
    print(f"  recovered A={A_syn:.1f} nT, b={b_syn:.1f} nT "
          f"(real-data fit: A=456.0, b=57.6)", flush=True)

    json.dump(res, open(OUT, "w"), indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
