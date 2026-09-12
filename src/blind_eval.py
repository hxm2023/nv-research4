"""BLIND estimation protocol (non-degenerate) — protocol v2, 2026-09-12.

Why v2: protocol v1 evaluated |B_hat - B_nom| with the estimation window centred on
B_nom. Since the applied field IS the nominal setpoint to within the instrument
systematic (~51 nT), the constant estimator "return the setpoint" scored better than
every real estimator. v1 is VOID (adversarial gate R1, review-stage/ADVERSARIAL_R1-R7.md).

v2 protocol (frozen):
  * Task: estimate an UNKNOWN field from one full 300-point real trace. The estimator is
    given B in [500, 45000] nT (the instrument range) and the calibrated conventions
    (tau_off = 18.6 ns, envelope population from high-rep data) - never the setpoint.
  * All classical methods start from the SAME blind FFT+Rife estimate of that trace
    (standard practice in the field), so the comparison isolates the refinement step.
  * Metric: |B_hat - B_true| with B_true = 1071.4*n nT (the applied setpoint); the
    ~51 nT setpoint systematic is 2 orders of magnitude below low-budget errors and is
    reported as a caveat, not swept under the rug.
  * Methods:
      fft_rife     : blind FFT peak + Rife interpolation (init for the others)
      lm_refine    : LM multistart refinement from the FFT estimate (per trace)
      joint_refine : session-pooled LM (shared envelope + phase frame), same FFT inits
      (amortized network evaluated separately by src/eval_blind_net.py)
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, ".")
from src.baselines import fft_rife, lm_multistart
from src.data_pipeline import REP_LEVELS, load_dc
from src.model import GAMMA, ramsey

TAU_OFF = 0.0186
B_LO, B_HI = 500.0, 45000.0
OUT = "results/blind_eval.json"


def fft_blind(tau, y):
    r = fft_rife(tau, y, B_LO, B_HI)
    return r["B"] if r else np.nan


def lm_refine(tau, y, B_init, win=None, n_starts=9):
    """LM refinement around the FFT estimate (window = +-5% of B_init by default)."""
    if not np.isfinite(B_init):
        return np.nan
    W = win if win is not None else max(3 * 1071.4, 0.05 * B_init)
    r = lm_multistart(tau, y, max(B_LO, B_init - W), min(B_HI, B_init + W),
                      n_starts=n_starts)
    return r["B"] if r else np.nan


def joint_refine(tau, Y, B_init, win=None, tau_off_us=TAU_OFF):
    """Session-pooled refinement: shared A, C, T2*, p, phi0; per-column B.
    Bounds are centred on each column's own blind FFT estimate - identical
    information to lm_refine (no setpoint knowledge)."""
    ncol = Y.shape[1]
    W = np.asarray([win if win is not None else max(3 * 1071.4, 0.05 * b)
                    for b in B_init], dtype=float)
    if not np.isfinite(B_init).all():
        bad = ~np.isfinite(B_init)
        B_init = np.where(bad, 20000.0, B_init)

    def resid(th):
        B = th[:ncol]
        A, C, T2, p, phi0 = th[ncol:ncol + 5]
        out = np.empty((len(tau), ncol))
        for c in range(ncol):
            out[:, c] = ramsey(tau, B[c], A, C, T2, p, phi0, tau_off_us) - Y[:, c]
        return out.ravel()

    x0 = np.concatenate([B_init, [0.127, 0.889, 5.4, 2.0, 0.0]])
    lo = np.concatenate([np.maximum(B_LO, B_init - W), [0.02, 0.5, 2.0, 0.8, -np.pi]])
    hi = np.concatenate([np.minimum(B_HI, B_init + W), [0.45, 1.2, 15.0, 4.0, np.pi]])
    r = least_squares(resid, x0, bounds=(lo, hi), max_nfev=400 * ncol)
    return r.x[:ncol]


def main(sheets=range(8)):
    ds = load_dc()
    tau = ds.tau_us
    res = json.load(open(OUT)) if __import__("os").path.exists(OUT) else {
        "protocol": {"version": 2, "task": "blind estimation, unknown field",
                     "range_nT": [B_LO, B_HI], "metric": "|B_hat - B_true|",
                     "init": "shared blind FFT+Rife for all classical methods"},
        "sheets": {}}

    for si in sheets:
        key = f"sheet{si+1}"
        e = res["sheets"].get(key, {})
        Y = ds.signal[si]
        r_lvl = REP_LEVELS[si]
        e["reps"] = int(r_lvl)
        if "fft" not in e:
            B_fft = np.array([fft_blind(tau, Y[:, c]) for c in range(40)])
            e["fft"] = np.round(B_fft, 1).tolist()
            print(f"{key} fft init median|err|={np.median(np.abs(B_fft - ds.B_nT)):.0f}",
                  flush=True)
            res["sheets"][key] = e
            json.dump(res, open(OUT, "w"), indent=2)

        B_fft = np.array(e["fft"])
        if "lm_refine" not in e:
            t0 = time.time()
            B = np.array([lm_refine(tau, Y[:, c], B_fft[c]) for c in range(40)])
            e["lm_refine"] = np.round(B, 1).tolist()
            print(f"{key} lm_refine done {time.time()-t0:.0f}s", flush=True)
            res["sheets"][key] = e
            json.dump(res, open(OUT, "w"), indent=2)

        if "joint_refine" not in e:
            t0 = time.time()
            B = joint_refine(tau, Y, B_fft)
            e["joint_refine"] = np.round(B, 1).tolist()
            print(f"{key} joint_refine done {time.time()-t0:.0f}s", flush=True)
            res["sheets"][key] = e
            json.dump(res, open(OUT, "w"), indent=2)

        # summary for this sheet
        Bt = ds.B_nT
        print(f"=== {key} r={int(r_lvl)} === median |err| (nT):", flush=True)
        for m in ["fft", "lm_refine", "joint_refine"]:
            v = np.abs(np.array(e[m]) - Bt)
            print(f"    {m:14s} med={np.median(v):8.1f} mean={np.mean(v):8.1f} "
                  f"<500nT={np.mean(v<500)*100:3.0f}% <1000nT={np.mean(v<1000)*100:3.0f}% "
                  f"max={np.max(v):9.0f}", flush=True)

    # eta table
    print("\n=== blind eta(r) (median |err|, t_ovh=0) ===", flush=True)
    T = lambda r: float(r) * float(np.sum(tau))
    for si in range(8):
        e = res["sheets"][f"sheet{si+1}"]
        Bt = ds.B_nT
        med = {m: float(np.median(np.abs(np.array(e[m]) - Bt)))
               for m in ["fft", "lm_refine", "joint_refine"] if m in e}
        if not med:
            continue
        t = T(e["reps"])
        line = f"  r={e['reps']:>7}: " + "  ".join(
            f"{m}={v:7.1f} (eta={v*np.sqrt(t):.2e})" for m, v in med.items())
        print(line, flush=True)
    json.dump(res, open(OUT, "w"), indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
