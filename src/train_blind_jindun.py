"""Train blind amortized estimators (per-trace and set-conditioned) on jindun with
>=5 seeds and evaluate on the REAL 8-level ladder. Protocol v2 (blind task).

Provenance: every run records seed, steps, config, checkpoint hash, and per-sheet
per-column errors on real data.
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
from src.estimators.blind import (BlindSetNet, BlindTraceNet, fft_init_batch,
                                  predict_blind, train_blind)

OUT = "results/blind_nets.json"


def evaluate(net, which, ds, device, tag):
    out = {}
    ref = None
    p = "results/reference_B_sheet8.json"
    if os.path.exists(p):
        ref = np.array(json.load(open(p))["B_ref"])
    for si in range(8):
        r = REP_LEVELS[si]
        sig = 0.207 * np.sqrt(5000 / r)
        Yc = ds.signal[si].T                      # (n_cols, n_tau)
        fi = fft_init_batch(Yc[None])[0]
        m, s, _ = predict_blind(net, Yc, sig, which=which, device=device, fft_init=fi)
        e = np.abs(m - ds.B_nT)
        out[f"sheet{si+1}"] = {
            "reps": int(r), "median_err_nom": float(np.median(e)),
            "mean_err_nom": float(np.mean(e)),
            "median_err_ref": float(np.median(np.abs(m - ref))) if ref is not None else None,
            "frac_within_500": float(np.mean(e < 500)),
            "frac_within_1000": float(np.mean(e < 1000)),
            "mean_post_sd": float(np.mean(s)),
            "errors_nom": np.round(e, 1).tolist(),
            "B_hat": np.round(m, 1).tolist(),
            "post_sd": np.round(s, 1).tolist(),
        }
        print(f"  [{tag}] sheet{si+1} r={int(r):>6}: med={np.median(e):7.1f} "
              f"mean={np.mean(e):7.1f} <500={np.mean(e < 500) * 100:3.0f}% "
              f"post_sd={np.mean(s):6.0f}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="set", choices=["set", "trace", "both"])
    ap.add_argument("--steps", type=int, default=12000)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--sessions", type=int, default=6)
    ap.add_argument("--cols", type=int, default=40)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--width", type=int, default=96)
    ap.add_argument("--arch", default="spec", choices=["spec", "cnn"])
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    ds = load_dc()
    tau = ds.tau_us
    kinds = ["set", "trace"] if args.which == "both" else [args.which]
    print(f"device={device} kinds={kinds} steps={args.steps} seeds={args.seeds}", flush=True)

    res = json.load(open(OUT)) if os.path.exists(OUT) else {"runs": []}
    done = {(r["kind"], r["seed"], r["steps"]) for r in res["runs"]}

    for kind in kinds:
        for seed in range(args.seeds):
            if (kind, seed, args.steps) in done:
                print(f"{kind} seed {seed} already done", flush=True)
                continue
            t0 = time.time()
            torch.manual_seed(seed)
            net = (BlindSetNet(arch=args.arch) if kind == "set"
                   else BlindTraceNet(arch=args.arch))
            losses = train_blind(net, tau, which=kind, steps=args.steps,
                                 n_sessions=args.sessions, n_cols=args.cols,
                                 lr=args.lr, seed=seed, device=device, arch=args.arch,
                                 log_every=max(200, args.steps // 10),
                                 ckpt=f"checkpoints/blind_{kind}_seed{seed}.pt")
            dt = time.time() - t0
            sd = net.state_dict()
            h = hashlib.sha256()
            for k in sorted(sd):
                h.update(sd[k].cpu().numpy().tobytes())
            entry = {"kind": kind, "seed": seed, "steps": args.steps,
                     "sessions": args.sessions, "cols": args.cols, "lr": args.lr,
                     "width": args.width, "arch": args.arch, "train_loss": float(np.mean(losses[-200:])),
                     "wall_s": dt, "ckpt_sha256": h.hexdigest()[:16], "device": device}
            entry["real"] = evaluate(net, kind, ds, device, f"{kind}-s{seed}")
            res["runs"].append(entry)
            json.dump(res, open(OUT, "w"), indent=2)
            print(f"{kind} seed {seed} done in {dt:.0f}s", flush=True)

    print("\n=== aggregate (median over seeds of per-seed medians) ===", flush=True)
    for kind in kinds:
        for si in range(8):
            v = [r["real"][f"sheet{si+1}"]["median_err_nom"] for r in res["runs"]
                 if r["kind"] == kind and r["steps"] == args.steps and "real" in r]
            if v:
                print(f"  {kind:5s} sheet{si+1} r={int(REP_LEVELS[si]):>6}: "
                      f"median={np.median(v):7.1f} (n={len(v)})", flush=True)


if __name__ == "__main__":
    main()
