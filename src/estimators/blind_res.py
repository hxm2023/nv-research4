"""Residual (FFT-anchored) amortized posterior - Phase 2 vehicle.

Instead of regressing the absolute field over [500, 45000] nT (1024 coarse bins, which
both caps the resolution at ~43 nT and invites systematic bias), the network predicts a
CORRECTION to the blind FFT+Rife estimate of the same trace:

    q(delta | trace),  B_hat = B_fft + E[delta],  delta in [-W, +W]

Every method in the comparison starts from the same FFT+Rife estimate, so this is the
amortized analogue of the classical LM refinement - the same information, a learned
inference rule. Resolution is (2W)/(n_bins) = 31 nT at W=8000, and the parameterisation
removes the absolute-regression bias.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.estimators.blind import B_HI, B_LO, SpectralTrunk, _Trunk, fft_init_batch  # noqa: E402
from src.synth import gen_traces, sample_envelope, sigma_at  # noqa: E402

W_NT = 8000.0
N_BINS = 512
Y_MEAN, Y_SCALE = 0.89, 0.13
_BINS = np.linspace(-W_NT, W_NT, N_BINS)


class ResTraceNet(nn.Module):
    """q(delta | one trace, log sigma, fft init)."""

    def __init__(self, n_bins=N_BINS, arch="spec"):
        super().__init__()
        self.trunk = SpectralTrunk() if arch != "cnn" else _Trunk()
        self.head = nn.Sequential(nn.Linear(self.trunk.out_dim, 512), nn.GELU(),
                                  nn.Linear(512, 512), nn.GELU(),
                                  nn.Linear(512, n_bins))

    def forward(self, y_norm, ctx):
        return self.head(self.trunk(y_norm, ctx))


class ResSetNet(nn.Module):
    """q(delta_c | whole session) - set-conditioned residual inference."""

    def __init__(self, n_bins=N_BINS, arch="spec", emb=192):
        super().__init__()
        self.trunk = SpectralTrunk() if arch != "cnn" else _Trunk()
        self.proj = nn.Sequential(nn.Linear(self.trunk.out_dim, emb), nn.GELU())
        self.attn = nn.MultiheadAttention(emb, num_heads=4, batch_first=True)
        self.head = nn.Sequential(nn.Linear(3 * emb + 3, 512), nn.GELU(),
                                  nn.Linear(512, 512), nn.GELU(),
                                  nn.Linear(512, n_bins))

    def forward(self, y_norm, ctx):
        B, N, T = y_norm.shape
        f = self.proj(self.trunk(y_norm.reshape(B * N, T), ctx.reshape(B * N, 3)))
        f = f.reshape(B, N, -1)
        ctx_r = ctx.reshape(B, N, 3)
        att, _ = self.attn(f + ctx_r[:, :, 1:2], f, f)
        return self.head(torch.cat([f, att, att - f, ctx_r], dim=-1)
                         ).reshape(B, N, -1)


def session_batch_res(n_sessions, n_cols, tau, rng, reps_pool, env_mode="percol_shared_phase"):
    from src.estimators.blind import blind_session_batch
    Y, B, sigma = blind_session_batch(n_sessions, n_cols, tau, rng, reps_pool,
                                      env_mode=env_mode)
    return Y, B, sigma


def _ctx(Y, sigma, device, fft_init):
    yt = torch.tensor((Y - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)
    fi = np.asarray(fft_init, dtype=float)
    return yt, torch.tensor(fi / B_HI, dtype=torch.float32, device=device)


def train_res(net, tau, which="set", steps=20000, n_sessions=6, n_cols=40, lr=2e-3,
              seed=0, device="cpu", log_every=500, arch="spec", env_mode="percol_shared_phase",
              reps_pool=(5000, 10000, 20000, 40000, 80000, 160000, 320000, 640000),
              ckpt=None):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    net.to(device).train()
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps)
    losses = []
    for step in range(steps):
        Y, B, sigma = session_batch_res(n_sessions, n_cols, tau, rng, reps_pool, env_mode)
        fi = fft_init_batch(Y)
        yt, fft_t = _ctx(Y, sigma, device, fi)
        ls = torch.tensor(np.tile(np.log10(sigma)[:, None], (1, n_cols)),
                          dtype=torch.float32, device=device)
        ctx = torch.stack([torch.zeros_like(fft_t), ls, fft_t], dim=-1)
        delta = torch.tensor((B - fi) / W_NT, dtype=torch.float32, device=device)
        logits = net(yt, ctx) if which == "set" else net(
            yt.reshape(-1, yt.shape[-1]),
            ctx.reshape(-1, 3)).reshape(n_sessions, n_cols, -1)
        idx = torch.clamp(((delta + 1) / 2 * (N_BINS - 1)).round().long(), 0, N_BINS - 1)
        tgt = F.one_hot(idx, N_BINS).float() * 0.99 + 0.01 / N_BINS
        loss = -(tgt * F.log_softmax(logits, -1)).sum(-1).mean()
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 5.0)
        opt.step(); sched.step()
        losses.append(loss.item())
        if log_every and (step + 1) % log_every == 0:
            print(f"  [{which}-res] step {step+1}/{steps} loss {np.mean(losses[-log_every:]):.4f}",
                  flush=True)
    if ckpt:
        os.makedirs(os.path.dirname(ckpt), exist_ok=True)
        torch.save({"state": net.state_dict(), "W_NT": W_NT, "N_BINS": N_BINS,
                    "which": which, "arch": arch}, ckpt)
    return losses


@torch.no_grad()
def predict_res(net, Y, sigma, which="set", device="cpu", fft_init=None):
    """Y (n_cols, n_tau). Returns (B_hat, sd, post)."""
    net.eval().to(device)
    Y = np.asarray(Y, dtype=float)
    if Y.shape[0] != 40 and Y.shape[1] == 40:
        Y = Y.T
    if fft_init is None:
        fft_init = fft_init_batch(Y[None])[0]
    fi = np.asarray(fft_init, dtype=float)
    if which == "set":
        yt, fft_t = _ctx(Y[None], np.array([sigma]), device, fi[None])
        ls = np.full((1, len(fi)), np.log10(float(sigma)))
        ctx = torch.stack([torch.zeros_like(fft_t), torch.tensor(ls, dtype=torch.float32,
                                                                device=device), fft_t],
                          dim=-1)
        logits = net(yt, ctx)[0]
    else:
        yt, fft_t = _ctx(Y, np.array([sigma]), device, fi)
        ls = np.log10(float(sigma))
        ctx = torch.stack([torch.zeros_like(fft_t),
                           torch.full_like(fft_t, ls), fft_t], dim=-1)
        logits = net(yt, ctx)
    p = F.softmax(logits, -1).cpu().numpy()
    dmean = (p * _BINS).sum(axis=1)
    var = (p * (_BINS[None, :] - dmean[:, None]) ** 2).sum(axis=1)
    return fi + dmean, np.sqrt(np.clip(var, 0, None)), p
