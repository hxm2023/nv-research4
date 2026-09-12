"""Amortized neural posterior over B from a single Ramsey trace.

q(t | y, context) where t = (B - B_center)/W in [-1, 1], conditioned on the
nominal window center and the photon-budget level log10(sigma). Trained on
instrument-anchored synthetic traces (real envelope population, real noise law,
flat B prior inside the window). One network serves the whole repetition ladder.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.synth import gen_dataset, sigma_at  # noqa: E402

W_NT = 3 * 1071.4
N_BINS = 241
Y_MEAN, Y_SCALE = 0.89, 0.13


class PosteriorNet(nn.Module):
    def __init__(self, n_bins=N_BINS, width=96, n_blocks=5):
        super().__init__()
        self.inp = nn.Conv1d(3, width, kernel_size=7, padding=3)
        blocks = []
        for _ in range(n_blocks):
            blocks.append(ResBlock(width, dil=2 ** (_ % 3 + 1)))
        self.blocks = nn.Sequential(*blocks)
        self.head = nn.Sequential(
            nn.Linear(2 * width + 2, 256), nn.GELU(),
            nn.Linear(256, 256), nn.GELU(),
            nn.Linear(256, n_bins),
        )

    def forward(self, y_norm, ctx):
        # y_norm (B,300), ctx (B,2) = [B_center/4e4, log10(sigma)]
        x = y_norm.unsqueeze(1).expand(-1, 1, -1)
        ctx_ch = ctx.unsqueeze(-1).expand(-1, 2, y_norm.shape[-1])
        h = torch.cat([x, ctx_ch], dim=1)
        h = F.gelu(self.inp(h))
        h = self.blocks(h)
        h = torch.cat([h.mean(dim=-1), h.amax(dim=-1), ctx], dim=-1)
        return self.head(h)


class ResBlock(nn.Module):
    def __init__(self, width, dil=1):
        super().__init__()
        self.c1 = nn.Conv1d(width, width, 5, padding=2 * dil, dilation=dil)
        self.c2 = nn.Conv1d(width, width, 5, padding=2 * dil, dilation=dil)
        self.n1 = nn.GroupNorm(8, width)
        self.n2 = nn.GroupNorm(8, width)

    def forward(self, x):
        h = F.gelu(self.n1(self.c1(x)))
        h = self.n2(self.c2(h))
        return F.gelu(x + h)


def _batch(n, tau, rng, reps_pool):
    reps = rng.choice(np.asarray(reps_pool, dtype=float), size=n)
    B_center = 1071.4 * rng.integers(1, 41, size=n)
    B = B_center + rng.uniform(-W_NT, W_NT, size=n)
    # real data lives on positive fields; cos is even so B and -B are indistinguishable
    # with a free phase - keep training fields strictly positive as in the experiment
    while True:
        bad = B < 300.0
        if not bad.any():
            break
        B[bad] = B_center[bad] + rng.uniform(-W_NT, W_NT, size=int(bad.sum()))
    sigma = np.array([sigma_at(r) for r in reps])
    from src.synth import sample_envelope, gen_traces
    env = sample_envelope(rng, n)
    Y = gen_traces(tau, B, env, sigma, rng)
    return Y, B, B_center, sigma


def train(net, tau, steps=4000, batch=256, lr=2e-3, n_bins=N_BINS, log_every=500,
          reps_pool=(5000, 10000, 20000, 40000, 80000, 160000, 320000, 640000),
          seed=0, device="cpu", ckpt=None):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    net.to(device).train()
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps)
    bin_centers = np.linspace(-W_NT, W_NT, n_bins)
    bin_w = bin_centers[1] - bin_centers[0]
    losses = []
    for step in range(steps):
        Y, B, Bc, sigma = _batch(batch, tau, rng, reps_pool)
        yt = torch.tensor((Y - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)
        ctx = torch.tensor(np.stack([Bc / 4e4, np.log10(sigma)], axis=1),
                           dtype=torch.float32, device=device)
        t_true = torch.tensor((B - Bc) / W_NT, dtype=torch.float32, device=device)
        logits = net(yt, ctx)
        # hard bin target (optimum of softmax-CE is the true discretized posterior;
        # a narrower-than-achievable soft target would make the loss unlearnable)
        idx = torch.clamp(((t_true + 1) / 2 * (n_bins - 1)).round().long(), 0, n_bins - 1)
        target = F.one_hot(idx, n_bins).float()
        target = target * (1 - 0.01) + 0.01 / n_bins
        loss = -(target * F.log_softmax(logits, dim=-1)).sum(dim=-1).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        losses.append(loss.item())
        if log_every and (step + 1) % log_every == 0:
            print(f"  step {step+1}/{steps} loss {np.mean(losses[-log_every:]):.4f}", flush=True)
    if ckpt:
        os.makedirs(os.path.dirname(ckpt), exist_ok=True)
        torch.save({"state": net.state_dict(), "W_NT": W_NT, "N_BINS": n_bins}, ckpt)
    return losses


@torch.no_grad()
def predict(net, Y, B_center, sigma, device="cpu", n_bins=N_BINS):
    net.eval().to(device)
    yt = torch.tensor((Y - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)
    B_center = np.asarray(B_center, dtype=float)
    if np.ndim(sigma) == 0:
        sigma = np.full(len(B_center), float(sigma))
    ctx = torch.tensor(np.stack([B_center / 4e4, np.log10(sigma)], axis=1),
                       dtype=torch.float32, device=device)
    logits = net(yt, ctx)
    p = F.softmax(logits, dim=-1).cpu().numpy()
    centers = np.linspace(-W_NT, W_NT, n_bins)
    mean = (p * centers).sum(axis=1) + B_center
    var = (p * (centers[None, :] - (mean[:, None] - B_center[:, None])) ** 2).sum(axis=1)
    return mean, np.sqrt(np.clip(var, 0, None)), p
