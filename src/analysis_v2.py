"""Unified v2 analysis: blind protocol, CRLB-anchored efficiency, crossover law.

Addresses adversarial points R1.2/R3/R4:
  * compares each estimator against its OWN bound (free-envelope CRLB for per-trace
    fitting, joint CRLB for pooled fitting) - never a 1-parameter bound for a
    6-parameter estimator;
  * uses RMSE (a sigma-equivalent) as the primary statistic, with the median reported
    alongside and the 0.674 factor applied when the median is used;
  * reports the estimator's consumption explicitly: eta is computed with a declared
    per-point overhead t_ovh and BOTH a single-column and a session accounting;
  * regions are reported separately and the primary region is pre-registered here.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, ".")
from src.data_pipeline import REP_LEVELS, load_dc
from src.model import crlb_sigma_B, crlb_sigma_B_free_envelope, crlb_sigma_B_joint

TAU_OFF = 0.0186
SHEETS = list(range(8))
REGIONS = {"cols7_40": slice(6, 40), "cols1_6": slice(0, 6), "all": slice(0, 40)}


def load_methods():
    """Merge the classical (blind_eval) and neural (blind_nets) result files."""
    out = {}
    p = "results/blind_eval.json"
    if os.path.exists(p):
        d = json.load(open(p))
        for k, v in d["sheets"].items():
            si = int(k.replace("sheet", "")) - 1
            out.setdefault(si, {})
            for m, key in [("fft", "fft"), ("lm_refine", "lm_refine"),
                           ("joint_refine", "joint_refine")]:
                if key in v:
                    out[si][m] = np.array(v[key])
    p3 = "results/blind_partial_pool.json"
    if os.path.exists(p3):
        d3 = json.load(open(p3))
        for k, v in d3.get("sheets", {}).items():
            si = int(k.replace("sheet", "")) - 1
            out.setdefault(si, {})["partial_pool"] = np.array(v["B_hat"])
    p2 = "results/blind_nets.json"
    if os.path.exists(p2):
        d = json.load(open(p2))
        # group by (sheet, kind) so seeds can be ensembled
        stash = {}
        for run in d["runs"]:
            kind = "net_set" if run["kind"] == "set" else "net_trace"
            for k, v in run["real"].items():
                si = int(k.replace("sheet", "")) - 1
                stash.setdefault((si, kind), []).append(np.array(v["B_hat"]))
        for (si, kind), arrs in stash.items():
            out.setdefault(si, {})
            out[si][kind] = arrs[0]
            if len(arrs) >= 3:
                out[si][kind + "_ens"] = np.median(np.stack(arrs, axis=0), axis=0)
            out[si][kind + "_nseeds"] = len(arrs)
    return out


def bootstrap_ci(err, n_boot=2000, stat=np.sqrt, seed=0, alpha=0.05):
    """Bootstrap CI of the RMSE over columns (the unit of replication available)."""
    rng = np.random.default_rng(seed)
    n = len(err)
    if n < 3:
        return float("nan"), float("nan")
    vals = [stat(np.mean(rng.choice(err, size=n, replace=True) ** 2)) for _ in range(n_boot)]
    return float(np.quantile(vals, alpha / 2)), float(np.quantile(vals, 1 - alpha / 2))


def crlb_table(ds):
    """Per-region CRLB medians at each rep level (nT): free-envelope (per-trace) and
    joint shared-envelope (40 columns). Also the known-envelope bound for reference."""
    env = np.array(json.load(open("results/envelope_sheet8.json"))["env_sheet8"])
    out = {}
    for si, r in enumerate(REP_LEVELS):
        sig = 0.207 * np.sqrt(5000 / r)
        free = np.array([crlb_sigma_B_free_envelope(ds.tau_us, ds.B_nT[c], *env[c], sig)
                         for c in range(40)])
        kn = np.array([crlb_sigma_B(ds.tau_us, ds.B_nT[c], *env[c], sig) for c in range(40)])
        joint = crlb_sigma_B_joint(ds.tau_us, ds.B_nT, *env.mean(axis=0), sig)
        out[int(r)] = {"free": free, "known": kn, "joint": joint}
    return out


def fit_floor_law(reps, rmse):
    """deltaB(r) = sqrt(A^2*(5000/r) + b^2): photon-limited part + bias floor."""
    from scipy.optimize import least_squares
    r = np.asarray(reps, dtype=float)
    y = np.asarray(rmse, dtype=float)
    def resid(p):
        A, b = np.abs(p)
        return np.sqrt(A**2 * (5000.0 / r) + b**2) - y
    sol = least_squares(resid, [y[0] * np.sqrt(r[0] / 5000.0), 0.3 * y[-1]],
                        bounds=([1e-3, 0], [1e6, 1e4]))
    A, b = np.abs(sol.x)
    return float(A), float(b), float(np.sqrt(np.mean(sol.fun**2)))


def main():
    ds = load_dc()
    Bt = ds.B_nT
    methods = load_methods()
    crl = crlb_table(ds)
    ovh = {"t_ovh_0.5us": 0.5, "t_ovh_1us": 1.0, "t_ovh_2us": 2.0}
    res = {"protocol": "v2 blind", "tau_sum_us": float(np.sum(ds.tau_us)),
           "crlb_medians": {}, "tables": {}}

    for r, v in crl.items():
        res["crlb_medians"][f"r{r}"] = {
            "free_median": float(np.median(v["free"])),
            "known_median": float(np.median(v["known"])),
            "joint_median": float(np.median(v["joint"])),
        }

    print("=== v2 analysis: RMSE vs own CRLB, per region ===")
    for reg, sl in REGIONS.items():
        print(f"\n--- region {reg} ---")
        hdr = (f"{'r':>7} {'method':>16} {'RMSE':>8} {'med':>7} {'bias':>8} "
               f"{'CRLB_own':>9} {'eff':>6} {'[95% CI RMSE]':>18}")
        print(hdr)
        for si in SHEETS:
            r = int(REP_LEVELS[si])
            if si not in methods:
                continue
            for m in ["lm_refine", "joint_refine", "partial_pool", "net_set_ens",
                      "net_set", "net_trace_ens", "net_trace"]:
                if m.endswith("_seeds"):
                    continue
                if m not in methods[si]:
                    continue
                err = (methods[si][m] - Bt)[sl]
                ae = np.abs(err)
                rmse = float(np.sqrt(np.mean(err**2)))
                med = float(np.median(ae))
                bias = float(np.mean(err))
                if m in ("lm_refine", "net_trace", "net_trace_ens"):
                    bound = float(np.median(crl[r]["free"][sl]))
                else:
                    bound = float(np.median(crl[r]["joint"][sl]))
                eff = rmse / bound
                lo, hi = bootstrap_ci(err)
                res["tables"].setdefault(reg, {}).setdefault(f"r{r}", {})[m] = {
                    "rmse": rmse, "median": med, "bias": bias, "crlb_own": bound,
                    "efficiency": eff, "rmse_ci": [lo, hi],
                }
                print(f"{r:>7} {m:>16} {rmse:>8.1f} {med:>7.1f} {bias:>8.1f} "
                      f"{bound:>9.1f} {eff:>6.2f} [{lo:>7.1f},{hi:>8.1f}]")

    # floor law + crossover
    print("\n=== floor law deltaB(r)=sqrt(A^2*5000/r + b^2) and crossover ===")
    reps = [int(r) for r in REP_LEVELS]
    for reg in ["cols7_40", "all"]:
        fits = {}
        for m in ["lm_refine", "joint_refine"]:
            ys = []
            for si in SHEETS:
                r = int(REP_LEVELS[si])
                if si in methods and m in methods[si]:
                    err = (methods[si][m] - Bt)[REGIONS[reg]]
                    ys.append(float(np.sqrt(np.mean(err**2))))
                else:
                    ys.append(np.nan)
            A, b, rms = fit_floor_law(reps, ys)
            fits[m] = {"A_nT": A, "floor_nT": b, "fit_rms": rms, "rmse": ys}
            print(f"  {reg} {m:>14}: A={A:8.1f} nT  floor b={b:7.1f} nT  (fit rms {rms:.1f})")
        if "lm_refine" in fits and "joint_refine" in fits:
            A1 = fits["lm_refine"]["A_nT"]; A2 = fits["joint_refine"]["A_nT"]
            b2 = fits["joint_refine"]["floor_nT"]
            if A1 > A2 and b2 > 0:
                # deltaB^2 = A^2*(5000/r) + b^2 ; equalise per-trace and pooled
                rstar = 5000.0 * (A1**2 - A2**2) / b2**2
                fits["crossover_reps"] = float(rstar)
                print(f"  {reg} crossover r* = {rstar:,.0f} repetitions "
                      f"(photon-limited gain equals the {b2:.0f} nT pooling floor)")
        res.setdefault("floor_law", {})[reg] = fits

    # eta with declared overheads, per budget (η must be read along the ladder)
    print("\n=== eta = RMSE * sqrt(t_total) per budget, region cols7_40 ===")
    tau_sum = float(np.sum(ds.tau_us))
    for name, t_ovh in ovh.items():
        t_col = tau_sum + 300 * t_ovh
        print(f"  {name} (t_total(r) = r * {t_col:.0f} us):")
        hdr = f"    {'r':>7}"
        for m in ["lm_refine", "joint_refine"]:
            hdr += f" {m:>16}"
        hdr += f" {'best':>10} {'ratio lm/best':>13}"
        print(hdr)
        for si in SHEETS:
            r = int(REP_LEVELS[si])
            if si not in methods:
                continue
            vals = {}
            for m in ["lm_refine", "joint_refine"]:
                if m in methods[si]:
                    err = (methods[si][m] - Bt)[REGIONS["cols7_40"]]
                    vals[m] = float(np.sqrt(np.mean(err**2))) * np.sqrt(r * t_col)
            if len(vals) == 2:
                best = min(vals.values())
                print(f"    {r:>7} {vals['lm_refine']:>16.3e} {vals['joint_refine']:>16.3e} "
                      f"{best:>10.3e} {vals['lm_refine'] / best:>13.2f}")
                res.setdefault("eta_per_budget", {}).setdefault(name, {})[f"r{r}"] = {
                    "lm_refine": vals["lm_refine"], "joint_refine": vals["joint_refine"],
                    "best": best}
    res["eta"] = {"tau_sum_us": tau_sum,
                  "accounting": "per-column time (session task: 40 field values are the "
                                "deliverable, so one column's accumulation time is charged "
                                "to each estimate; the single-column variant is the "
                                "external-prior estimator reported separately)"}
    json.dump(res, open("results/analysis_v2.json", "w"), indent=2)
    print("\nwrote results/analysis_v2.json")


if __name__ == "__main__":
    main()
