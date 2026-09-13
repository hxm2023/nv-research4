"""Referee-demanded robustness checks.

(1) Noise-model validation: are the fit residuals white? The Cramer-Rao bounds are only
    meaningful if the per-point noise is uncorrelated and stationary. We test lag-1 and
    lag-2 autocorrelation of the residuals of per-trace fits on real data, per sheet.
(2) Crossover uncertainty: bootstrap the floor-law fit by resampling the 34 columns, and
    report a confidence interval for r* instead of a point value.
(3) Model-mismatch attribution: compare the pooled bias floor when the shared parameters
    are relaxed one at a time (leave-one-free), on real data, to check that the floor is
    attributable to the relaxation time rather than to field-dependent contrast/phase.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, ".")
from src.data_pipeline import REP_LEVELS, load_dc
from src.model import ramsey

TAU_OFF = 0.0186
OUT = "results/robustness_checks.json"


def fit_one(tau, y, B0, W=3214.2, n_starts=9):
    from src.baselines import lm_multistart
    r = lm_multistart(tau, y, B0 - W, B0 + W, n_starts=n_starts)
    return r


def acf_residuals(tau, y, fit, max_lag=4):
    B, A, C, T2, p, phi0 = fit["B"], fit["A"], fit["C"], fit["T2"], fit["p"], fit["phi0"]
    r = y - ramsey(tau, B, A, C, T2, p, phi0, TAU_OFF)
    r = r - r.mean()
    denom = np.dot(r, r)
    return [float(np.dot(r[:-k], r[k:]) / denom) for k in range(1, max_lag + 1)]


def pooled_fit(tau, Y, B_init, free=()):
    """Shared-envelope fit; 'free' lists per-column parameters to release."""
    ncol = Y.shape[1]
    B_init = np.asarray(B_init, dtype=float)
    bad = ~np.isfinite(B_init)
    if bad.any():
        B_init = np.where(bad, 20000.0, B_init)
    W = np.array([max(3 * 1071.4, 0.05 * b) for b in B_init])

    def unpack(th):
        k = ncol
        B = th[:k]
        A = th[k] if "A" not in free else th[k:k + ncol]
        k2 = k + (1 if "A" not in free else ncol)
        C = th[k2] if "C" not in free else th[k2:k2 + ncol]
        k3 = k2 + (1 if "C" not in free else ncol)
        p = th[k3] if "p" not in free else th[k3:k3 + ncol]
        k4 = k3 + (1 if "p" not in free else ncol)
        phi = th[k4] if "phi" not in free else th[k4:k4 + ncol]
        k5 = k4 + (1 if "phi" not in free else ncol)
        T2 = th[k5:k5 + ncol] if "T2" in free else np.full(ncol, th[k5])
        return B, A, C, T2, p, phi

    def expand(v, n):
        return np.full(n, v) if np.ndim(v) == 0 else v

    def resid(th):
        B, A, C, T2, p, phi = unpack(th)
        A = expand(A, ncol); C = expand(C, ncol); p = expand(p, ncol)
        phi = expand(phi, ncol); T2 = expand(T2, ncol)
        return np.concatenate([ramsey(tau, B[c], A[c], C[c], T2[c], p[c], phi[c], TAU_OFF)
                               - Y[:, c] for c in range(ncol)])

    th0, lo, hi = [], [], []
    th0 += list(B_init); lo += list(B_init - W); hi += list(B_init + W)
    for nm, v0, l, h in [("A", 0.127, 0.02, 0.45), ("C", 0.889, 0.5, 1.2),
                         ("p", 2.0, 0.8, 4.0), ("phi", 0.0, -np.pi, np.pi)]:
        if nm in free:
            th0 += [v0] * ncol; lo += [l] * ncol; hi += [h] * ncol
        else:
            th0 += [v0]; lo += [l]; hi += [h]
    # allocate T2 as ONE parameter when shared and ncol when free: allocating ncol entries
    # for the shared case leaves dead parameters with zero gradient and stalls the solver
    if "T2" in free:
        th0 += [5.4] * ncol; lo += [2.5] * ncol; hi += [15.0] * ncol
    else:
        th0 += [5.4]; lo += [2.5]; hi += [15.0]
    best, best_cost = None, np.inf
    # starts: the FFT estimate at several shared relaxation times, plus the per-trace
    # maximum-likelihood solution, which is reliable at every budget and removes the
    # initialisation sensitivity of the joint problem
    starts = [(np.array(th0, dtype=float), t2) for t2 in ([5.4] if "T2" in free
                                                          else [4.0, 5.4, 7.0])]
    try:
        from src.baselines import lm_multistart
        B_pt = np.array([lm_multistart(tau, Y[:, c], max(500.0, B_init[c] - W[c]),
                                      min(45000.0, B_init[c] + W[c]), n_starts=9)["B"]
                         for c in range(ncol)])
        th_pt = np.array(th0, dtype=float)
        th_pt[:ncol] = np.clip(B_pt, lo[:ncol], hi[:ncol])
        starts.append((th_pt, 5.4))
    except Exception:
        pass
    for th, t2 in starts:
        if "T2" not in free:
            th[-1] = t2
        try:
            r = least_squares(resid, th, bounds=(np.array(lo), np.array(hi)),
                              max_nfev=500 * ncol)
        except Exception:
            continue
        if r.cost < best_cost:
            best, best_cost = r, r.cost
    if best is None:                       # every start raised: fall back to a plain solve
        best = least_squares(resid, np.array(th0), bounds=(np.array(lo), np.array(hi)),
                             max_nfev=500 * ncol)
    return best.x[:ncol]


def fit_law(reps, rmse):
    def resid(p):
        A, b = np.abs(p)
        return np.sqrt(A**2 * (5000.0 / reps) + b**2) - rmse
    sol = least_squares(resid, [rmse[0] * np.sqrt(reps[0] / 5000.0), 0.3 * rmse[-1]],
                        bounds=([1e-3, 0], [1e6, 1e4]))
    A, b = np.abs(sol.x)
    return float(A), float(b)


def main():
    import sys as _s
    parts = set(_s.argv[1:]) or {"1", "2", "3"}
    ds = load_dc()
    tau = ds.tau_us
    # merge with whatever earlier parts already computed (never clobber)
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}

    # (1) residual whiteness
    if "1" in parts:
        print("=== residual autocorrelation of per-trace fits (real data) ===", flush=True)
        acf = {}
        for si in [0, 3, 7]:
            fits = [fit_one(tau, ds.signal[si][:, c], ds.B_nT[c]) for c in range(6, 40)]
            acfs = np.array([acf_residuals(tau, ds.signal[si][:, c], fits[i])
                             for i, c in enumerate(range(6, 40))])
            acf[f"sheet{si+1}"] = {"mean_acf_lag1": float(acfs[:, 0].mean()),
                                   "mean_acf_lag2": float(acfs[:, 1].mean()),
                                   "sd_acf_lag1": float(acfs[:, 0].std()),
                                   "n": int(len(acfs))}
            print(f"  sheet{si+1} r={int(REP_LEVELS[si]):>7}: lag1={acfs[:,0].mean():+.4f} "
                  f"(sd {acfs[:,0].std():.3f}), lag2={acfs[:,1].mean():+.4f}", flush=True)
        print("  (white noise => |acf| ~ 1/sqrt(300) = 0.058)", flush=True)
        out["residual_autocorrelation"] = acf
        json.dump(out, open(OUT, "w"), indent=2)

    # (2) crossover CI by bootstrapping columns
    if "2" in parts:
        print("=== crossover confidence interval (bootstrap over columns) ===", flush=True)
        a = json.load(open("results/analysis_v2.json"))
        T = a["tables"]["cols7_40"]
        reps = np.array(sorted(int(k[1:]) for k in T), float)
        lm = json.load(open("results/blind_eval.json"))["sheets"]
        rng = np.random.default_rng(0)
        rstar_boot = []
        for _ in range(200):
            idx = rng.integers(6, 40, size=34)
            rl, rp = [], []
            for si in range(8):
                sh = lm[f"sheet{si+1}"]
                e_lm = np.abs(np.array(sh["lm_refine"]) - ds.B_nT)[idx]
                e_po = np.abs(np.array(sh["joint_refine"]) - ds.B_nT)[idx]
                rl.append(np.sqrt(np.mean(e_lm ** 2)))
                rp.append(np.sqrt(np.mean(e_po ** 2)))
            A1, b1 = fit_law(reps, np.array(rl))
            A2, b2 = fit_law(reps, np.array(rp))
            if A1 > A2 and b2 > 0:
                rstar_boot.append(5000.0 * (A1**2 - A2**2) / b2**2)
        rstar_boot = np.array(rstar_boot)
        ci = [float(np.percentile(rstar_boot, 2.5)), float(np.percentile(rstar_boot, 97.5))]
        print(f"  r* = {np.median(rstar_boot):,.0f}  (95% CI {ci[0]:,.0f} - {ci[1]:,.0f}), "
              f"{len(rstar_boot)}/200 bootstrap draws resolvable", flush=True)
        out["crossover_bootstrap"] = {"median": float(np.median(rstar_boot)),
                                      "ci95": ci, "n_draws": int(len(rstar_boot))}
        json.dump(out, open(OUT, "w"), indent=2)

    # (3) which shared parameter causes the floor? leave-one-free comparison at 640k
    if "3" in parts:
        print("=== pooled bias floor: which shared constraint costs? (sheet 8, r=640k) ===",
              flush=True)
        Y = ds.signal[7][:, 6:40]          # columns 7-40 only, the primary region
        from src.blind_eval import fft_blind
        Bf = np.array([fft_blind(tau, Y[:, c]) for c in range(Y.shape[1])])
        Bt = ds.B_nT[6:40]
        attrib = {}
        for tag, free in [("all shared", ()), ("T2 free", ("T2",)), ("p free", ("p",)),
                          ("A free", ("A",)), ("C free", ("C",))]:
            B = pooled_fit(tau, Y, Bf, free=free)
            e = B - Bt
            attrib[tag] = {"rmse": float(np.sqrt(np.mean(e ** 2))),
                           "bias": float(np.mean(e))}
            out["floor_attribution_sheet8"] = attrib
            json.dump(out, open(OUT, "w"), indent=2)
            print(f"  {tag:>12}: RMSE {attrib[tag]['rmse']:7.1f} nT   "
                  f"bias {attrib[tag]['bias']:+7.1f} nT", flush=True)
        out["floor_attribution_sheet8"] = attrib
        json.dump(out, open(OUT, "w"), indent=2)

    json.dump(out, open(OUT, "w"), indent=2)
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
