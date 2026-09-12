"""Train the set-conditioned amortized posterior on jindun (>=5 seeds) and evaluate
on the REAL 8-level photon ladder (sheets 1-8), reporting per-column errors.

Rigor: 5 training seeds; test sheets never used for training; evaluation on the frozen
real traces only. Every number written with its provenance (seed, steps, ckpt hash).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_pipeline import REP_LEVELS, load_dc
from src.estimators.set_conditional import SetPosteriorNet, predict_set, train_set

OUT = "results/set_conditional.json"


def evaluate_seed(net, ds, device, tag):
    """Per-sheet, per-column errors of the set-conditioned estimator on REAL data."""
    out = {}
    ref = None
    if os.path.exists("results/reference_B_sheet8.json"):
        ref = np.array(json.load(open("results/reference_B_sheet8.json"))["B_ref"])
    for si in range(8):
        r = REP_LEVELS[si]
        sig = 0.207 * np.sqrt(5000 / r)
        m, s, _ = predict_set(net, ds.signal[si], ds.B_nT, sig, device=device)
        e = np.abs(m - ds.B_nT)
        out[f"sheet{si+1}"] = {
            "reps": int(r),
            "median_err_nom": float(np.median(e)),
            "mean_err_nom": float(np.mean(e)),
            "median_err_ref": float(np.median(np.abs(m - ref))) if ref is not None else None,
            "frac_within_500": float(np.mean(e < 500)),
            "mean_post_sd": float(np.mean(s)),
            "errors_nom": np.round(e, 1).tolist(),
            "B_hat": np.round(m, 1).tolist(),
            "post_sd": np.round(s, 1).tolist(),
        }
        print(f"  [{tag}] sheet{si+1} r={int(r):>6}: med(nom)={np.median(e):7.1f} "
              f"med(ref)={out[f'sheet{si+1}']['median_err_ref']:7.1f} "
              f"<500={np.mean(e < 500) * 100:3.0f}%  post_sd={np.mean(s):6.1f}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--cols", type=int, default=40)
    ap.add_argument("--sessions", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--width", type=int, default=96)
    ap.add_argument("--only-cols", type=int, default=0,
                    help="if >0 restrict training columns to the first N (leakage control)")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    ds = load_dc()
    tau = ds.tau_us
    print(f"device={device} steps={args.steps} seeds={args.seeds} cols={args.cols}", flush=True)

    res = json.load(open(OUT)) if os.path.exists(OUT) else {"runs": []}
    done = {r["seed"] for r in res["runs"] if r.get("steps") == args.steps}

    for seed in range(args.seeds):
        if seed in done:
            print(f"seed {seed} already done, skipping", flush=True)
            continue
        t0 = time.time()
        torch.manual_seed(seed)
        net = SetPosteriorNet(width=args.width)
        cols_pool = (np.arange(1, args.only_cols + 1) if args.only_cols > 0
                     else np.arange(1, 41))
        losses = train_set(net, tau, steps=args.steps, n_sessions=args.sessions,
                           n_cols=args.cols, lr=args.lr, seed=seed, device=device,
                           log_every=max(200, args.steps // 10), cols_pool=cols_pool,
                           ckpt=f"checkpoints/set_seed{seed}.pt")
        dt = time.time() - t0
        sd = net.state_dict()
        h = hashlib.sha256()
        for k in sorted(sd):
            h.update(sd[k].cpu().numpy().tobytes())
        entry = {"seed": seed, "steps": args.steps, "sessions": args.sessions,
                 "cols": args.cols, "lr": args.lr, "width": args.width,
                 "train_loss": float(np.mean(losses[-200:])),
                 "wall_s": dt, "ckpt_sha256": h.hexdigest()[:16],
                 "only_cols": args.only_cols, "device": device}
        entry["real"] = evaluate_seed(net, ds, device, f"seed{seed}")
        res["runs"].append(entry)
        json.dump(res, open(OUT, "w"), indent=2)
        print(f"seed {seed} done in {dt:.0f}s, wrote {OUT}", flush=True)

    # aggregate across seeds
    print("\n=== aggregate over seeds (median of per-seed medians) ===", flush=True)
    for si in range(8):
        v = [r["real"][f"sheet{si+1}"]["median_err_nom"] for r in res["runs"]
             if "real" in r and f"sheet{si+1}" in r["real"]]
        if v:
            print(f"  sheet{si+1} r={int(REP_LEVELS[si]):>6}: "
                  f"median={np.median(v):7.1f} nT  (range {min(v):.1f}-{max(v):.1f}, n={len(v)})",
                  flush=True)


if __name__ == "__main__":
    main()
