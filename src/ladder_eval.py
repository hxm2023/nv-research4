"""Full 8-rep-ladder evaluation of classical baselines vs shared-envelope joint LM.

Produces the eta(r) curve input data (unified eval, real data, all 8 sheets):
  deltaB(r) per method, t_total(r) = r * sum(tau_i + t_ovh), eta = deltaB*sqrt(t_total).
Also a paired Wilcoxon of per-column errors (joint vs lm_free) per sheet.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.baselines import joint_lm, lm_multistart
from src.data_pipeline import REP_LEVELS, load_dc
from src.model import crlb_sigma_B

WIN = 3 * 1071.4
OUT = "results/ladder_eval.json"


def t_total_us(reps, t_ovh_us, n_cols=1):
    ds = load_dc()
    return reps * float(np.sum(ds.tau_us + t_ovh_us)) * n_cols


def main(sheets=range(8), n_starts=25):
    ds = load_dc()
    tau = ds.tau_us
    res = {"window_nT": WIN, "tau_off_ns": 18.6, "sheets": {}}
    if os.path.exists(OUT):
        res.update(json.load(open(OUT)))

    for si in sheets:
        y_all = ds.signal[si]
        B_nom = ds.B_nT
        r_lvl = REP_LEVELS[si]
        sig = 0.207 * np.sqrt(5000 / r_lvl)
        entry = res["sheets"].get(f"sheet{si+1}", {})
        entry.update({"reps": int(r_lvl), "sigma": float(sig)})

        if "lm_free" not in entry:
            t0 = time.time()
            lm_B = np.full(40, np.nan)
            for c in range(40):
                r = lm_multistart(tau, y_all[:, c], B_nom[c] - WIN, B_nom[c] + WIN,
                                  n_starts=n_starts)
                if r:
                    lm_B[c] = r["B"]
            entry["lm_free"] = lm_B.tolist()
            entry["lm_free_t"] = time.time() - t0
            print(f"sheet{si+1} lm_free done in {time.time()-t0:.1f}s", flush=True)

        if "lm_free_hi" not in entry and si < 2:
            t0 = time.time()
            lm_B = np.full(40, np.nan)
            for c in range(40):
                r = lm_multistart(tau, y_all[:, c], B_nom[c] - WIN, B_nom[c] + WIN,
                                  n_starts=100)
                if r:
                    lm_B[c] = r["B"]
            entry["lm_free_hi"] = lm_B.tolist()
            print(f"sheet{si+1} lm_free_hi done in {time.time()-t0:.1f}s", flush=True)

        if "joint_lm" not in entry:
            t0 = time.time()
            r = joint_lm(tau, y_all, B_nom)
            entry["joint_lm"] = np.asarray(r["B"]).tolist()
            entry["joint_env"] = np.asarray(r["env"]).tolist()
            print(f"sheet{si+1} joint_lm done in {time.time()-t0:.1f}s", flush=True)

        crlb = [crlb_sigma_B(tau, B, 0.128, 0.89, 5.4, 1.8, 0.0, sig) for B in B_nom]
        entry["crlb_known"] = [float(x) for x in crlb]

        res["sheets"][f"sheet{si+1}"] = entry
        json.dump(res, open(OUT, "w"), indent=2)

    # summary + paired tests
    from scipy.stats import wilcoxon
    print("\n=== eta(r) ladder (median over 40 real columns; t_ovh=0) ===")
    print(f"{'sheet':>6} {'r':>8} {'lm_free':>9} {'joint':>9} {'CRLB':>8} "
          f"{'eta_lm':>10} {'eta_joint':>10} {'ratio':>6} {'wilcoxon_p':>11}")
    for si in range(8):
        e = res["sheets"][f"sheet{si+1}"]
        r_lvl = e["reps"]
        lm = np.array(e["lm_free"]); jt = np.array(e["joint_lm"])
        err_lm = np.abs(lm - ds.B_nT); err_jt = np.abs(jt - ds.B_nT)
        T = t_total_us(r_lvl, 0.0)
        eta_lm = float(np.median(err_lm)) * np.sqrt(T)
        eta_jt = float(np.median(err_jt)) * np.sqrt(T)
        try:
            st, p = wilcoxon(err_jt, err_lm)
        except Exception:
            p = float("nan")
        print(f"{si+1:>6} {int(r_lvl):>8} {np.median(err_lm):>9.1f} {np.median(err_jt):>9.1f} "
              f"{np.median(e['crlb_known']):>8.1f} {eta_lm:>10.3e} {eta_jt:>10.3e} "
              f"{eta_lm/eta_jt:>6.2f} {p:>11.2e}")
        e["eta_lm_ovh0"] = eta_lm; e["eta_joint_ovh0"] = eta_jt; e["wilcoxon_p"] = float(p)
    json.dump(res, open(OUT, "w"), indent=2)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
