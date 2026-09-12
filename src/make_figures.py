"""Publication figures for the L5 paper (reads only the result JSONs).

fig1_ladder.pdf     deltaB(r) with the fitted floor law and the crossover
fig2_bias.pdf       estimator bias vs photon budget (the mechanism)
fig3_control.pdf    synthetic control with exact ground truth
fig4_envelope.pdf   measured envelope inhomogeneity across the 40 field columns
fig5_eta.pdf        eta(r) with declared per-point overhead scenarios
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, ".")
from src.data_pipeline import REP_LEVELS, load_dc

OUT = "paper/figures"
plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "figure.dpi": 150,
                     "savefig.bbox": "tight", "axes.grid": True, "grid.alpha": 0.25})

COL = {"lm_refine": "#1f77b4", "joint_refine": "#d62728", "partial_pool": "#2ca02c",
       "net_set_ens": "#9467bd", "net_set": "#c5b0d5"}
LAB = {"lm_refine": "per-trace LM (free envelope)",
       "joint_refine": "session-pooled (shared envelope)",
       "partial_pool": "session-pooled (per-column $T_2^*$)",
       "net_set_ens": "amortized, session-conditioned",
       "net_set": "amortized (single seed)"}


def load():
    a = json.load(open("results/analysis_v2.json"))
    return a


def fig1(a):
    fig, ax = plt.subplots(figsize=(3.4, 2.7))
    reps = np.array([int(k[1:]) for k in a["tables"]["cols7_40"]], dtype=float)
    order = np.argsort(reps)
    reps = reps[order]
    for m in ["lm_refine", "joint_refine", "partial_pool", "net_set_ens"]:
        ys = []
        for k in [f"r{int(r)}" for r in reps]:
            e = a["tables"]["cols7_40"][k].get(m)
            ys.append(e["rmse"] if e else np.nan)
        ax.errorbar(reps, ys, yerr=None, marker="o", ms=3.5, lw=1.2, color=COL[m],
                    label=LAB[m])
    rr = np.logspace(np.log10(4000), np.log10(700000), 200)
    fl = a["floor_law"]["cols7_40"]
    for m, ls in [("lm_refine", "--"), ("joint_refine", ":")]:
        A, b = fl[m]["A_nT"], fl[m]["floor_nT"]
        ax.plot(rr, np.sqrt(A**2 * 5000 / rr + b**2), ls, color=COL[m], lw=1.0, alpha=0.9)
    rstar = fl["crossover_reps"]
    ax.axvline(rstar, color="k", lw=0.8, alpha=0.6)
    ax.annotate(rf"$r^*\approx{rstar/1e4:.0f}\times10^4$", (rstar, 40), fontsize=7,
                rotation=90, va="bottom", ha="right")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("repetitions per $\\tau$ point  $r$")
    ax.set_ylabel("field RMSE $\\delta B$ (nT)")
    ax.set_title("real data, columns 7–40", fontsize=8)
    ax.legend(loc="lower left", frameon=False)
    fig.savefig(f"{OUT}/fig1_ladder.pdf")
    fig.savefig(f"{OUT}/fig1_ladder.png")
    plt.close(fig)


def fig2(a):
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    reps = np.array([int(k[1:]) for k in a["tables"]["cols7_40"]], dtype=float)
    order = np.argsort(reps); reps = reps[order]
    for m in ["lm_refine", "joint_refine", "partial_pool"]:
        ys = [a["tables"]["cols7_40"][f"r{int(r)}"].get(m, {}).get("bias", np.nan)
              for r in reps]
        ax.plot(reps, ys, marker="o", ms=3.5, lw=1.2, color=COL[m], label=LAB[m])
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xscale("log")
    ax.set_xlabel("repetitions per $\\tau$ point  $r$")
    ax.set_ylabel("mean error $\\langle \\hat B - B\\rangle$ (nT)")
    ax.legend(loc="upper left", frameon=False)
    fig.savefig(f"{OUT}/fig2_bias.pdf"); fig.savefig(f"{OUT}/fig2_bias.png")
    plt.close(fig)


def fig3(a):
    d = json.load(open("results/control_pooling_bias.json"))
    reps = np.array([r["reps"] for r in d["rows"]], dtype=float)
    fig, ax = plt.subplots(figsize=(3.4, 2.7))
    for key, m, lab in [("lm", "lm_refine", "per-trace LM"),
                        ("pool_full", "joint_refine", "pooled (shared $T_2^*$)"),
                        ("pool_partial", "partial_pool", "pooled (per-column $T_2^*$)")]:
        ys = [r[key]["median"] for r in d["rows"]]
        ax.plot(reps, ys, marker="o", ms=3.5, lw=1.2, color=COL[m], label=lab)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("repetitions per $\\tau$ point  $r$")
    ax.set_ylabel("median $|\\delta B|$ (nT)")
    ax.set_title("synthetic control, exact ground truth", fontsize=8)
    ax.legend(loc="lower left", frameon=False)
    fig.savefig(f"{OUT}/fig3_control.pdf"); fig.savefig(f"{OUT}/fig3_control.png")
    plt.close(fig)


def fig4():
    env = np.array(json.load(open("results/envelope_sheet8.json"))["env_sheet8"])
    names = [r"$A$ (contrast)", r"$C$ (offset)", r"$T_2^*$ ($\mu$s)",
             r"$p$ (stretch)", r"$\phi_0$ (rad)"]
    fig, axes = plt.subplots(1, 5, figsize=(7.2, 1.9))
    for k, (ax, nm) in enumerate(zip(axes, names)):
        ax.hist(env[:, k], bins=12, color="#4c72b0", alpha=0.85)
        ax.set_xlabel(nm, fontsize=8)
        if k == 0:
            ax.set_ylabel("count", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.2)
    fig.suptitle("relaxation envelope across the 40 field columns (640k-repetition fits)",
                 fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig4_envelope.pdf"); fig.savefig(f"{OUT}/fig4_envelope.png")
    plt.close(fig)


def fig5():
    ds = load_dc()
    tau_sum = float(np.sum(ds.tau_us))
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    a = json.load(open("results/analysis_v2.json"))
    reps = np.array([int(k[1:]) for k in a["tables"]["cols7_40"]], dtype=float)
    order = np.argsort(reps); reps = reps[order]
    for m in ["lm_refine", "joint_refine"]:
        for t_ovh, ls in [(1.0, "-"), (0.5, "--"), (2.0, ":")]:
            t_tot = reps * (tau_sum + 300 * t_ovh)
            ys = [a["tables"]["cols7_40"][f"r{int(r)}"].get(m, {}).get("rmse", np.nan)
                  for r in reps]
            ax.plot(reps, np.array(ys) * np.sqrt(t_tot), ls, marker="o", ms=2.5, lw=1.0,
                    color=COL[m], alpha=0.9,
                    label=f"{LAB[m].split('(')[0].strip()}, $t_{{ovh}}$={t_ovh:g} $\\mu$s")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("repetitions per $\\tau$ point  $r$")
    ax.set_ylabel(r"$\eta=\delta B\sqrt{t_{\rm total}}$  (nT$\sqrt{\mu{\rm s}}$)")
    ax.legend(loc="upper left", frameon=False, fontsize=6.5)
    fig.savefig(f"{OUT}/fig5_eta.pdf"); fig.savefig(f"{OUT}/fig5_eta.png")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    a = load()
    fig1(a); fig2(a); fig3(a); fig4(); fig5()
    print("figures written to", OUT)
