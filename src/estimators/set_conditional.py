"""Set-conditioned (in-context) amortized posterior: the ML vehicle of L5.

A measurement session yields N_c traces (one per field column) that share the
instrument's relaxation envelope (A, C, T2*, p) and phase frame (phi0) but have
distinct fields B_c. The network reads the WHOLE set and, for each column, emits a
posterior over (B_c - B_center_c). This is the amortized counterpart of the classical
pooled LM: it marginalises the shared nuisance instead of point-estimating it, and the
session representation is inferred in-context (no retraining per session).

Everything it consumes comes from the same session's data - no external field knowledge.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.estimators.amortized import N_BINS, W_NT, Y_MEAN, Y_SCALE  # noqa: E402
from src.synth import gen_traces, sample_envelope, sigma_at  # noqa: E402


class SetPosteriorNet(nn.Module):
    """Per-trace encoder -> session embedding (attention pooling) -> per-trace posteriors."""

    def __init__(self, n_bins=N_BINS, width=96, n_blocks=4, emb=128):
        super().__init__()
        self.n_bins = n_bins
        self.inp = nn.Conv1d(3, width, kernel_size=7, padding=3)
        self.blocks = nn.Sequential(*[ResBlock(width, dil=2 ** (i % 3 + 1))
                                      for i in range(n_blocks)])
        self.proj = nn.Sequential(nn.Linear(2 * width + 2, emb), nn.GELU())
        self.attn = nn.MultiheadAttention(emb, num_heads=4, batch_first=True)
        self.head = nn.Sequential(
            nn.Linear(2 * emb + 2, 256), nn.GELU(),
            nn.Linear(256, 256), nn.GELU(),
            nn.Linear(256, n_bins),
        )

    def encode(self, y_norm, ctx):
        # y_norm (N,T), ctx (N,2)
        x = y_norm.unsqueeze(1)
        ctx_ch = ctx.unsqueeze(-1).expand(-1, 2, y_norm.shape[-1])
        h = F.gelu(self.inp(torch.cat([x, ctx_ch], dim=1)))
        h = self.blocks(h)
        feat = torch.cat([h.mean(-1), h.amax(-1), ctx], dim=-1)
        return self.proj(feat)

    def forward(self, y_norm, ctx):
        """y_norm (B, N, T), ctx (B, N, 2) -> logits (B, N, n_bins)."""
        B, N, T = y_norm.shape
        f = self.encode(y_norm.reshape(B * N, T), ctx.reshape(B * N, 2))
        f = f.reshape(B, N, -1)
        sess, _ = self.attn(f, f, f)          # in-context session representation
        sess_mean = f.mean(dim=1, keepdim=True).expand_as(f)
        z = torch.cat([f, sess - sess_mean, ctx.reshape(B * N, 2).reshape(B, N, 2)], dim=-1)
        return self.head(z.reshape(B * N, -1)).reshape(B, N, self.n_bins)


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


def session_batch(n_sessions, n_cols, tau, rng, reps_pool, cols_pool=None):
    """One synthetic session = n_cols traces sharing envelope + phi0, distinct B."""
    reps = rng.choice(np.asarray(reps_pool, dtype=float), size=n_sessions)
    sigma = np.array([sigma_at(r) for r in reps])
    if cols_pool is None:
        cols_pool = np.arange(1, 41)
    cols = rng.choice(np.asarray(cols_pool), size=(n_sessions, n_cols), replace=True)
    Bc = 1071.4 * cols.astype(float)
    B = Bc + rng.uniform(-W_NT, W_NT, size=(n_sessions, n_cols))
    while True:
        bad = B < 300.0
        if not bad.any():
            break
        B[bad] = Bc[bad] + rng.uniform(-W_NT, W_NT, size=int(bad.sum()))
    Y = np.empty((n_sessions, n_cols, len(tau)))
    for s in range(n_sessions):
        env = sample_envelope(rng, 1, jitter=True)[0]
        env = np.repeat(env[None, :], n_cols, axis=0)
        Y[s] = gen_traces(tau, B[s], env, sigma[s], rng)
    return Y, B, Bc, sigma


def train_set(net, tau, steps=3000, n_sessions=8, n_cols=40, lr=2e-3, seed=0,
              device="cpu", log_every=250, reps_pool=(5000, 10000, 20000, 40000,
                                                        80000, 160000, 320000, 640000),
              ckpt=None):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    net.to(device).train()
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps)
    losses = []
    for step in range(steps):
        Y, B, Bc, sigma = session_batch(n_sessions, n_cols, tau, rng, reps_pool)
        yt = torch.tensor((Y - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)
        ctx = torch.tensor(np.stack([Bc / 4e4, np.tile(np.log10(sigma)[:, None], (1, n_cols))],
                                    axis=-1), dtype=torch.float32, device=device)
        t_true = torch.tensor((B - Bc) / W_NT, dtype=torch.float32, device=device)
        logits = net(yt, ctx)
        idx = torch.clamp(((t_true + 1) / 2 * (N_BINS - 1)).round().long(), 0, N_BINS - 1)
        tgt = F.one_hot(idx, N_BINS).float() * 0.99 + 0.01 / N_BINS
        loss = -(tgt * F.log_softmax(logits, -1)).sum(-1).mean()
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 5.0)
        opt.step(); sched.step()
        losses.append(loss.item())
        if log_every and (step + 1) % log_every == 0:
            print(f"  step {step+1}/{steps} loss {np.mean(losses[-log_every:]):.4f}", flush=True)
    if ckpt:
        os.makedirs(os.path.dirname(ckpt), exist_ok=True)
        torch.save({"state": net.state_dict(), "W_NT": W_NT, "N_BINS": N_BINS}, ckpt)
    return losses


@torch.no_grad()
def predict_set(net, Y, B_center, sigma, device="cpu", n_bins=N_BINS):
    """Y (N,T) one session -> (mean, sd, post) per column."""
    net.eval().to(device)
    B_center = np.asarray(B_center, dtype=float)
    N = len(B_center)
    sig = np.full(N, float(sigma)) if np.ndim(sigma) == 0 else np.asarray(sigma, dtype=float)
    yt = torch.tensor((Y - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)[None]
    ctx = torch.tensor(np.stack([B_center / 4e4, np.log10(sig)], axis=1),
                       dtype=torch.float32, device=device)[None]
    logits = net(yt, ctx)[0]
    p = F.softmax(logits, dim=-1).cpu().numpy()
    centers = np.linspace(-W_NT, W_NT, n_bins)
    mean = (p * centers).sum(axis=1) + B_center
    var = (p * (centers[None, :] - (mean[:, None] - B_center[:, None])) ** 2).sum(axis=1)
    return mean, np.sqrt(np.clip(var, 0, None)), p
