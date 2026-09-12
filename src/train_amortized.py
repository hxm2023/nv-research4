"""Train the amortized posterior estimator and evaluate on REAL sheets 1-2.

Usage: python -m src.train_amortized --steps 12000 --seed 0 [--eval-only ckpt]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_pipeline import REP_LEVELS, load_dc
from src.estimators.amortized import (N_BINS, W_NT, Y_MEAN, Y_SCALE, PosteriorNet,
                                      _batch, predict, train)


def synth_val_loss(net, VY, VB, VBC, VS, device):
    net.eval()
    with torch.no_grad():
        yt = torch.tensor((VY - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)
        ctx = torch.tensor(np.stack([VBC / 4e4, np.log10(VS)], axis=1),
                           dtype=torch.float32, device=device)
        logits = net(yt, ctx)
        t = torch.tensor((VB - VBC) / W_NT, dtype=torch.float32, device=device)
        idx = torch.clamp(((t + 1) / 2 * (N_BINS - 1)).round().long(), 0, N_BINS - 1)
        tgt = F.one_hot(idx, N_BINS).float() * 0.99 + 0.01 / N_BINS
        return float(-(tgt * F.log_softmax(logits, -1)).sum(-1).mean())


def eval_real(net, ds, sheets=(0, 1), device="cuda", tag=""):
    out = {}
    ref = None
    if os.path.exists("results/reference_B_sheet8.json"):
        ref = np.array(json.load(open("results/reference_B_sheet8.json"))["B_ref"])
    for si in sheets:
        r = REP_LEVELS[si]
        sig = 0.207 * np.sqrt(5000 / r)
        Y = ds.signal[si]
        m, s, p = predict(net, Y.T, ds.B_nT, sig, device=device)
        e_nom = np.abs(m - ds.B_nT)
        out[f"sheet{si+1}"] = {
            "reps": int(r), "median_err_nom": float(np.median(e_nom)),
            "mean_err_nom": float(np.mean(e_nom)),
            "median_err_ref": float(np.median(np.abs(m - ref))) if ref is not None else None,
            "frac_within_500": float(np.mean(e_nom < 500)),
            "mean_post_sd": float(np.mean(s)),
            "errors_nom": np.round(e_nom, 1).tolist(),
            "B_hat": np.round(m, 1).tolist(),
            "post_sd": np.round(s, 1).tolist(),
        }
        print(f"  [{tag}] real sheet{si+1} r={int(r)}: mederr(nom)={np.median(e_nom):7.1f} "
              f"mederr(ref)={out[f'sheet{si+1}']['median_err_ref']:7.1f} "
              f"<500nT={np.mean(e_nom<500)*100:3.0f}%  post_sd={np.mean(s):6.1f}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=12000)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--width", type=int, default=96)
    ap.add_argument("--out", default="results/amortized_train.json")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    ds = load_dc()
    tau = ds.tau_us
    torch.manual_seed(args.seed)
    net = PosteriorNet(width=args.width)

    rngv = np.random.default_rng(999)  # frozen synthetic validation set
    VY, VB, VBC, VS = _batch(3000, tau, rngv,
                             (5000, 10000, 20000, 40000, 80000, 160000, 320000, 640000))

    t0 = time.time()
    losses = train(net, tau, steps=args.steps, batch=args.batch, seed=args.seed,
                   lr=args.lr, device=device, log_every=max(200, args.steps // 20),
                   ckpt=f"checkpoints/amortized_seed{args.seed}.pt")
    dt = time.time() - t0
    vl = synth_val_loss(net, VY, VB, VBC, VS, device)
    print(f"seed {args.seed}: train_loss={np.mean(losses[-200:]):.4f} synth_val={vl:.4f} "
          f"({dt:.0f}s)", flush=True)

    res = {"seed": args.seed, "steps": args.steps, "batch": args.batch, "lr": args.lr,
           "width": args.width, "train_loss": float(np.mean(losses[-200:])),
           "synth_val_loss": vl, "wall_s": dt, "device": device}
    res["synth_val"] = {}
    for reps, sig in [(5000, 0.207), (10000, 0.1464), (20000, 0.1035),
                      (40000, 0.0732), (640000, 0.0183)]:
        msk = VS == sig
        if msk.sum() == 0:
            continue
        m, s, _ = predict(net, VY[msk], VBC[msk], sig, device=device)
        e = np.abs(m - VB[msk])
        res["synth_val"][f"r{reps}"] = {"median": float(np.median(e)),
                                        "mean_post_sd": float(np.mean(s))}
    res["real"] = eval_real(net, ds, (0, 1), device=device, tag=f"seed{args.seed}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    prev = json.load(open(args.out)) if os.path.exists(args.out) else {"runs": []}
    prev["runs"].append(res)
    json.dump(prev, open(args.out, "w"), indent=2)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
