"""Publication figures for the L5 paper (reads only the result JSONs).

Design rules: revtex single-column width (8.6 cm), 8-9 pt type, no in-figure titles
(the caption carries that), error bars wherever a confidence interval exists, log-log
where the physics is a power law.

fig1_ladder     two panels: (a) deltaB(r) with bootstrap CIs + fitted floor law +
                crossover; (b) estimator bias(r) - the mechanism, same x axis
fig2_bounds     the two Cramer-Rao bounds (free vs joint) and measured efficiencies
fig3_control    synthetic control with exact ground truth
fig4_envelope   measured envelope inhomogeneity across the 40 field columns
fig5_eta        eta(r) with declared per-point overhead scenarios
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, ".")
from src.data_pipeline import REP_LEVELS, load_dc

OUT = "paper/figures"
plt.rcParams.update({
    "font.size": 8, "axes.labelsize": 8, "legend.fontsize": 7,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "figure.dpi": 200,
    "savefig.bbox": "tight", "axes.grid": True, "grid.alpha": 0.25,
    "grid.linewidth": 0.4, "axes.linewidth": 0.6, "lines.linewidth": 1.2,
    "legend.frameon": False, "axes.titlepad": 3,
})

COL = {"lm_refine": "#1f77b4", "joint_refine": "#d62728", "partial_pool": "#2ca02c"}
MK = {"lm_refine": "o", "joint_refine": "s", "partial_pool": "^"}
LAB = {"lm_refine": "per-trace LM",
       "joint_refine": "pooled (shared envelope)",
       "partial_pool": "pooled (per-column $T_2^*$)"}
NETC = "#8b5cf6"


def load_all():
    a = json.load(open("results/analysis_v2.json"))
    return a


def res_net_ladder(ds):
    """5-seed residual nets at the largest step count (the paper's network numbers)."""
    p = "results/blind_res_nets.json"
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    by = {}
    for r in d["runs"]:
        if r["kind"] == "set":
            by.setdefault(r["steps"], []).append(r)
    steps = max((s for s, rs in by.items() if len(rs) >= 5), default=max(by))
    rs = by[steps]
    yy, lo, hi = [], [], []
    for si in range(8):
        rms = np.array([np.sqrt(np.mean(((np.array(x["real"][f"sheet{si+1}"]["B_hat"])
                                          - ds.B_nT)[6:40]) ** 2)) for x in rs])
        yy.append(float(np.median(rms)))
        lo.append(float(np.percentile(rms, 25)))
        hi.append(float(np.percentile(rms, 75)))
    return np.array(REP_LEVELS, float), np.array(yy), np.array(lo), np.array(hi), len(rs)


def _fmt_r(x, pos):
    return f"{x/1e3:.0f}k" if x < 1e6 else f"{x/1e6:.0f}M"


def fig1(a, ds):
    reps = np.array(sorted(int(k[1:]) for k in a["tables"]["cols7_40"]), float)
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(3.4, 4.1), sharex=True,
                                 gridspec_kw={"height_ratios": [2.1, 1.0], "hspace": 0.08})
    # (a) ladder. Bands are VARIABILITY, not confidence intervals: for the classical
    # estimators they are the column-to-column interquartile range of the same session,
    # for the network the spread across training seeds. Encoded separately.
    for m in ["lm_refine", "joint_refine", "partial_pool"]:
        y, qlo, qhi = [], [], []
        for r in reps:
            e = a["tables"]["cols7_40"][f"r{int(r)}"].get(m)
            if not e:
                y.append(np.nan); qlo.append(np.nan); qhi.append(np.nan); continue
            y.append(e["rmse"])
            qlo.append(e["rmse_ci"][0]); qhi.append(e["rmse_ci"][1])
        ax.fill_between(reps, qlo, qhi, color=COL[m], alpha=0.12, lw=0)
        ax.plot(reps, y, marker=MK[m], ms=3.2, lw=1.1, color=COL[m], label=LAB[m])
    net = res_net_ladder(ds)
    if net:
        rr_, yy_, lo_, hi_, n_ = net
        ax.fill_between(rr_, lo_, hi_, color=NETC, alpha=0.18,
                        edgecolor="none")
        ax.plot(rr_, yy_, marker="D", ms=3.0, lw=1.1, color=NETC,
                label=f"amortized network ({n_} seeds)")
    rr = np.logspace(np.log10(4000), np.log10(700000), 200)
    fl = a["floor_law"]["cols7_40"]
    for m, ls in [("lm_refine", "--"), ("joint_refine", ":")]:
        A, b = fl[m]["A_nT"], fl[m]["floor_nT"]
        ax.plot(rr, np.sqrt(A**2 * 5000 / rr + b**2), ls, color=COL[m], lw=0.9, alpha=0.85)
    ax.axvspan(4000, 8000, color="0.5", alpha=0.07, lw=0)
    rstar = fl["crossover_reps"]
    ax.axvline(rstar, color="k", lw=0.7, alpha=0.55)
    _exp = 4 if rstar < 1e5 else (5 if rstar < 1e6 else 6)
    ax.annotate(rf"$r^*={rstar/10**_exp:.0f}\times10^{{{_exp}}}$", xy=(rstar, 520),
                xytext=(rstar * 0.72, 900), fontsize=6.5, color="0.15",
                va="center", ha="right",
                arrowprops=dict(arrowstyle="-", lw=0.5, color="0.35", shrinkA=1, shrinkB=1))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylabel(r"field RMSE $\delta B$ (nT)")
    ax.set_ylim(40, 2000)
    ax.set_xlim(4300, 900000)
    ax.legend(loc="lower left", ncol=1, handlelength=1.6, labelspacing=0.22,
              borderaxespad=0.3)
    ax.text(5600, 1750, "lowest\nbudget", fontsize=6.0, color="0.4", ha="center",
            va="top")
    # (b) bias
    for m in ["lm_refine", "joint_refine", "partial_pool"]:
        y = [a["tables"]["cols7_40"][f"r{int(r)}"].get(m, {}).get("bias", np.nan)
             for r in reps]
        bx.plot(reps, y, marker=MK[m], ms=3.0, lw=1.1, color=COL[m])
    bx.axhline(0, color="k", lw=0.6)
    bx.set_xscale("log")
    bx.set_xlim(4200, 900000)
    bx.set_ylim(-90, 230)
    bx.set_yticks([-50, 0, 50, 100, 150, 200])
    bx.set_xlabel(r"repetitions per $\tau$ point, $r$")
    bx.set_ylabel("bias (nT)", labelpad=1)
    bx.xaxis.set_major_formatter(FuncFormatter(_fmt_r))
    fig.align_ylabels([ax, bx])
    sec = ax.secondary_xaxis("top", functions=(lambda x: x / 150.0, lambda x: x * 150.0))
    sec.set_xlabel("detected photons per delay point", fontsize=7)
    sec.tick_params(labelsize=6.5)
    fig.savefig(f"{OUT}/fig1_ladder.pdf"); fig.savefig(f"{OUT}/fig1_ladder.png")
    plt.close(fig)


def fig2(a):
    """The two bounds and how close each estimator comes to its own."""
    reps = np.array(sorted(int(k[1:]) for k in a["tables"]["cols7_40"]), float)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 2.5))
    free = [a["crlb_medians"][f"r{int(r)}"]["free_median"] for r in reps]
    joint = [a["crlb_medians"][f"r{int(r)}"]["joint_median"] for r in reps]
    ax.plot(reps, free, "--", marker="o", ms=3, color=COL["lm_refine"],
            label="free-envelope bound (per trace)")
    ax.plot(reps, joint, ":", marker="s", ms=3, color=COL["joint_refine"],
            label="joint bound (shared envelope, 40 cols)")
    ax.fill_between(reps, joint, free, color="0.5", alpha=0.12, lw=0)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"repetitions per $\tau$ point, $r$")
    ax.set_ylabel(r"field bound $\sigma_B$ (nT)")
    ax.xaxis.set_major_formatter(FuncFormatter(_fmt_r))
    ax.legend(loc="upper right")
    ax.annotate("", xy=(reps[0], joint[0]), xytext=(reps[0], free[0]),
                arrowprops=dict(arrowstyle="<->", lw=0.7, color="0.3"))
    ax.text(reps[0] * 1.15, np.sqrt(np.asarray(free[0]) * np.asarray(joint[0])), "1.8x",
            fontsize=7, color="0.25")
    # both estimators divided by the SAME (joint) bound: a common absolute reference,
    # so an estimator cannot look efficient merely by being normalised to a loose bound
    for m in ["lm_refine", "joint_refine"]:
        y = [a["tables"]["cols7_40"][f"r{int(r)}"][m]["rmse"]
             / a["tables"]["cols7_40"][f"r{int(r)}"]["joint_refine"]["crlb_own"]
             for r in reps]
        bx.plot(reps, y, marker=MK[m], ms=3, color=COL[m], label=LAB[m])
    bx.axhline(1.0, color="k", lw=0.7)
    bx.text(0.03, 1.05, "joint CRB", transform=bx.get_yaxis_transform(),
            fontsize=6.5, color="0.35", va="bottom")
    bx.set_xscale("log"); bx.set_yscale("log")
    bx.set_xlabel(r"repetitions per $\tau$ point, $r$")
    bx.set_ylabel("RMSE / joint bound")
    bx.xaxis.set_major_formatter(FuncFormatter(_fmt_r))
    bx.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig2_bounds.pdf"); fig.savefig(f"{OUT}/fig2_bounds.png")
    plt.close(fig)


def fig3():
    d = json.load(open("results/control_pooling_bias.json"))
    reps = np.array([r["reps"] for r in d["rows"]], float)
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    for key, m, lab in [("lm", "lm_refine", "per-trace LM"),
                        ("pool_full", "joint_refine", "pooled (shared $T_2^*$)"),
                        ("pool_partial", "partial_pool", "pooled (per-column $T_2^*$)")]:
        y = [r[key].get("rmse", r[key]["median"]) for r in d["rows"]]
        q25 = np.array([r[key].get("q25", np.nan) for r in d["rows"]], float)
        q75 = np.array([r[key].get("q75", np.nan) for r in d["rows"]], float)
        if np.isfinite(q25).all() and np.isfinite(q75).all():
            ax.fill_between(reps, q25, q75, color=COL[m], alpha=0.12, edgecolor="none")
        ax.plot(reps, y, marker=MK[m], ms=3.2, color=COL[m], label=lab)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"repetitions per $\tau$ point, $r$")
    ax.set_ylabel(r"field RMSE $\delta B$ (nT)")
    ax.xaxis.set_major_formatter(FuncFormatter(_fmt_r))
    ax.legend(loc="lower left")
    fig.savefig(f"{OUT}/fig3_control.pdf"); fig.savefig(f"{OUT}/fig3_control.png")
    plt.close(fig)


def fig4():
    env = np.array(json.load(open("results/envelope_sheet8.json"))["env_sheet8"])
    names = [r"$A$ (contrast)", r"$C$ (offset)", r"$T_2^*$ ($\mu$s)",
             r"$p$ (stretch)", r"$\phi_0$ (rad)"]
    rng = np.random.default_rng(0)
    fig, axes = plt.subplots(1, 5, figsize=(6.9, 1.6))
    for k, (ax, nm) in enumerate(zip(axes, names)):
        v = env[:, k]
        ax.scatter(v, rng.uniform(-0.25, 0.25, len(v)), s=6, color="#4c72b0",
                   alpha=0.8, linewidths=0)
        ax.axvline(v.mean(), color="k", lw=0.6, alpha=0.5)
        ax.set_yticks([])
        ax.set_xlabel(nm, fontsize=7.5)
        ax.tick_params(labelsize=6.5)
        ax.set_ylim(-0.6, 0.6)
        if k == 4:
            ang = np.exp(1j * v).mean()
            ax.set_title(rf"$|R|={np.abs(ang):.3f}$", fontsize=6.5)
        else:
            ax.set_title(rf"$\sigma/\mu={v.std()/np.abs(v.mean()):.2f}$", fontsize=6.5)
        if k == 3:
            n_sat = int((v >= 3.99).sum())
            ax.annotate(f"{n_sat} at bound", xy=(v.max(), 0.28),
                        xytext=(v.max() - 1.5, 0.46), fontsize=6,
                        arrowprops=dict(arrowstyle="->", lw=0.5))
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig4_envelope.pdf"); fig.savefig(f"{OUT}/fig4_envelope.png")
    plt.close(fig)


def fig5():
    ds = load_dc()
    tau_sum = float(np.sum(ds.tau_us))
    a = json.load(open("results/analysis_v2.json"))
    reps = np.array(sorted(int(k[1:]) for k in a["tables"]["cols7_40"]), float)
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    for m, ls in [("lm_refine", "-"), ("joint_refine", "-")]:
        base = []
        for r in reps:
            rmse = a["tables"]["cols7_40"][f"r{int(r)}"][m]["rmse"]
            base.append(rmse * np.sqrt(r * (tau_sum + 300)))
        band_lo, band_hi = [], []
        for r, b in zip(reps, base):
            rmse = a["tables"]["cols7_40"][f"r{int(r)}"][m]["rmse"]
            band_lo.append(rmse * np.sqrt(r * (tau_sum + 150)))
            band_hi.append(rmse * np.sqrt(r * (tau_sum + 600)))
        ax.fill_between(reps, band_lo, band_hi, color=COL[m], alpha=0.15, lw=0)
        ax.plot(reps, base, ls, marker=MK[m], ms=3, color=COL[m], label=LAB[m])
    net = res_net_ladder(ds)
    if net:
        rr_, yy_, lo_, hi_, n_ = net
        tt = np.sqrt(rr_ * (tau_sum + 300))
        ax.plot(rr_, np.array(yy_) * tt, color=NETC, marker="D", ms=3,
                label="amortized network")
        ax.fill_between(rr_, np.array(lo_) * tt, np.array(hi_) * tt,
                        color=NETC, alpha=0.18, edgecolor="none")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"repetitions per $\tau$ point, $r$")
    ax.set_ylabel(r"$\eta=\delta B\sqrt{t_{\rm total}}$  (nT$\sqrt{\mu{\rm s}}$)")
    ax.xaxis.set_major_formatter(FuncFormatter(_fmt_r))
    ax.legend(loc="lower left")
    ax.text(0.98, 0.95, r"band: $t_{\rm ovh}\in[0.5,2]\,\mu$s", transform=ax.transAxes,
            fontsize=6.2, ha="right", va="top", color="0.35")
    fig.savefig(f"{OUT}/fig5_eta.pdf"); fig.savefig(f"{OUT}/fig5_eta.png")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ds = load_dc()
    a = load_all()
    fig1(a, ds); fig2(a); fig3(); fig4(); fig5()
    print("figures written to", OUT)
