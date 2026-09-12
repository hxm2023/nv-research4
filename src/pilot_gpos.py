"""G-Pos pilot (pre-registered): can a structured estimator beat classical per-trace
fitting at the two lowest photon budgets (real Sheet1=5k, Sheet2=10k)?

Protocol (frozen before running):
  * Ground truth: applied field B_nom = 1071.4*n nT (primary, conservative, includes
    instrument systematic); secondary reference B_ref = per-column fit at Sheet8 (640k).
  * Prior window for the fine-estimation task: |B - B_nom| <= 3 grid steps (3214.2 nT).
    (Physically canonical sensitivity scenario: precision of a field near a known value.)
  * Methods (identical trace, identical protocol):
      lm_free    : LM multistart inside window, free envelope
      fft_rife   : FFT+Rife frequency estimate
      grid_bayes : marginal posterior over B, profiling A/C, marginalizing T2,phi0
      joint_lm   : LM over all 40 columns sharing one envelope (uses only same-sheet data)
  * Metric: deltaB = |B_hat - B_true| per column; median and (for paired tests) per-column
    differences; sensitivity eta = deltaB*sqrt(t_total), t_total = r*sum(tau_i + t_ovh).
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.baselines import fft_rife, grid_bayes, joint_lm, lm_multistart
from src.data_pipeline import REP_LEVELS, load_dc
from src.model import GAMMA, crlb_sigma_B

WIN = 3 * 1071.4  # nT


def t_total(reps_idx, t_ovh_us):
    ds = load_dc()
    return REP_LEVELS[reps_idx] * float(np.sum(ds.tau_us + t_ovh_us))


def main(sheets=(0, 1), out="results/pilot_gpos.json", include_joint=True):
    ds = load_dc()
    tau = ds.tau_us
    res = {"protocol": {"window_nT": WIN, "tau_off_ns": 18.6,
                        "gt": "B_nom = 1071.4*n nT", "sheets": [s + 1 for s in sheets]},
           "methods": {}}

    # reference B from Sheet8 (640k) for the secondary metric
    ref_path = "results/reference_B_sheet8.json"
    if os.path.exists(ref_path):
        B_ref = np.array(json.load(open(ref_path))["B_ref"])
    else:
        L8 = lm_multistart(tau, ds.signal[7][:, 0], ds.B_nT[0] - WIN, ds.B_nT[0] + WIN,
                           n_starts=9)
        fits = []
        for c in range(40):
            r = lm_multistart(tau, ds.signal[7][:, c], ds.B_nT[c] - WIN, ds.B_nT[c] + WIN,
                              n_starts=16)
            fits.append(r["B"] if r else np.nan)
        B_ref = np.array(fits)
        json.dump({"B_ref": B_ref.tolist(),
                   "note": "per-column LM fit at Sheet8 (640k reps), free envelope"},
                  open(ref_path, "w"), indent=2)

    for si in sheets:
        y_all = ds.signal[si]
        B_nom = ds.B_nT
        r_lvl = REP_LEVELS[si]
        sig = 0.207 * np.sqrt(5000 / r_lvl)
        method_B = {}

        t0 = time.time()
        lm_B = np.full(40, np.nan)
        for c in range(40):
            r = lm_multistart(tau, y_all[:, c], B_nom[c] - WIN, B_nom[c] + WIN, n_starts=25)
            if r:
                lm_B[c] = r["B"]
        method_B["lm_free"] = lm_B
        print(f"  sheet{si+1} lm_free {time.time()-t0:.1f}s", flush=True)

        t0 = time.time()
        fr_B = np.full(40, np.nan)
        for c in range(40):
            r = fft_rife(tau, y_all[:, c], B_nom[c] - WIN, B_nom[c] + WIN)
            if r:
                fr_B[c] = r["B"]
        method_B["fft_rife"] = fr_B
        print(f"  sheet{si+1} fft_rife {time.time()-t0:.1f}s", flush=True)

        t0 = time.time()
        gb_B = np.full(40, np.nan); gb_sd = np.full(40, np.nan)
        for c in range(40):
            bg = np.linspace(B_nom[c] - WIN, B_nom[c] + WIN, 241)
            r = grid_bayes(tau, y_all[:, c], bg, sig)
            if r:
                gb_B[c] = r["B"]; gb_sd[c] = r["sd"]
        method_B["grid_bayes"] = gb_B
        method_B["grid_bayes_sd"] = gb_sd
        print(f"  sheet{si+1} grid_bayes {time.time()-t0:.1f}s", flush=True)

        if include_joint:
            t0 = time.time()
            r = joint_lm(tau, y_all, B_nom)
            method_B["joint_lm"] = r["B"]
            print(f"  sheet{si+1} joint_lm {time.time()-t0:.1f}s", flush=True)

        # CRLB references
        crlb_known = np.array([crlb_sigma_B(tau, B, 0.128, 0.89, 5.4, 1.8, 0.0, sig)
                               for B in B_nom])

        sheet_res = {"reps": int(r_lvl), "sigma": float(sig),
                     "t_total_1ovh": t_total(si, 0.0), "crlb_known_median": float(np.median(crlb_known))}
        for name, Bv in method_B.items():
            if name.endswith("_sd"):
                continue
            err_nom = np.abs(Bv - B_nom)
            err_ref = np.abs(Bv - B_ref)
            sheet_res[name] = {
                "median_err_nom": float(np.nanmedian(err_nom)),
                "mean_err_nom": float(np.nanmean(err_nom)),
                "median_err_ref": float(np.nanmedian(err_ref)),
                "frac_within_500": float(np.mean(err_nom < 500)),
                "errors_nom": np.round(err_nom, 1).tolist(),
            }
        res["methods"][f"sheet{si+1}"] = sheet_res
        print(f"=== Sheet{si+1} (r={int(r_lvl)}) ===", flush=True)
        for name in method_B:
            if name.endswith("_sd"):
                continue
            d = sheet_res[name]
            print(f"  {name:12s} mederr(nom)={d['median_err_nom']:8.1f} nT  "
                  f"mederr(ref)={d['median_err_ref']:8.1f}  <500nT: {d['frac_within_500']*100:4.0f}%",
                  flush=True)
        print(f"  CRLB_known median = {np.median(crlb_known):.1f} nT", flush=True)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
