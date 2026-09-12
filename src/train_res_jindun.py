"""Train residual (FFT-anchored) amortized estimators on jindun, evaluate on real data."""
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
from src.estimators.blind import fft_init_batch
from src.estimators.blind_res import ResSetNet, ResTraceNet, predict_res, train_res

OUT = "results/blind_res_nets.json"


def evaluate(net, which, ds, device, tag):
    out = {}
    ref = None
    if os.path.exists("results/reference_B_sheet8.json"):
        ref = np.array(json.load(open("results/reference_B_sheet8.json"))["B_ref"])
    for si in range(8):
        r = REP_LEVELS[si]
        sig = 0.207 * np.sqrt(5000 / r)
        Yc = ds.signal[si].T
        fi = fft_init_batch(Yc[None])[0]
        m, s, _ = predict_res(net, Yc, sig, which=which, device=device, fft_init=fi)
        e = (m - ds.B_nT)
        out[f"sheet{si+1}"] = {
            "reps": int(r), "median_err_nom": float(np.median(np.abs(e))),
            "mean_err_nom": float(np.mean(np.abs(e))), "bias_nom": float(np.mean(e)),
            "rmse_nom": float(np.sqrt(np.mean(e ** 2))),
            "median_err_ref": float(np.median(np.abs(m - ref))) if ref is not None else None,
            "frac_within_500": float(np.mean(np.abs(e) < 500)),
            "mean_post_sd": float(np.mean(s)),
            "errors_nom": np.round(np.abs(e), 1).tolist(),
            "B_hat": np.round(m, 1).tolist(),
        }
        print(f"  [{tag}] sheet{si+1} r={int(r):>6}: med={np.median(np.abs(e)):7.1f} "
              f"rmse={np.sqrt(np.mean(e ** 2)):7.1f} bias={np.mean(e):+8.1f} "
              f"<500={np.mean(np.abs(e) < 500) * 100:3.0f}%", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="both", choices=["set", "trace", "both"])
    ap.add_argument("--steps", type=int, default=20000)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--sessions", type=int, default=6)
    ap.add_argument("--cols", type=int, default=40)
    ap.add_argument("--lr", type=float, default=2e-3)
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
            net = ResSetNet() if kind == "set" else ResTraceNet()
            losses = train_res(net, tau, which=kind, steps=args.steps,
                               n_sessions=args.sessions, n_cols=args.cols, lr=args.lr,
                               seed=seed, device=device,
                               log_every=max(500, args.steps // 8),
                               ckpt=f"checkpoints/res_{kind}_seed{seed}.pt")
            dt = time.time() - t0
            sd = net.state_dict()
            h = hashlib.sha256()
            for k in sorted(sd):
                h.update(sd[k].cpu().numpy().tobytes())
            entry = {"kind": kind, "seed": seed, "steps": args.steps,
                     "sessions": args.sessions, "cols": args.cols, "lr": args.lr,
                     "train_loss": float(np.mean(losses[-200:])), "wall_s": dt,
                     "ckpt_sha256": h.hexdigest()[:16], "device": device}
            entry["real"] = evaluate(net, kind, ds, device, f"{kind}-s{seed}")
            res["runs"].append(entry)
            json.dump(res, open(OUT, "w"), indent=2)
            print(f"{kind} seed {seed} done in {dt:.0f}s", flush=True)


if __name__ == "__main__":
    main()
