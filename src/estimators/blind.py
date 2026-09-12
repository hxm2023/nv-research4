"""Blind amortized posterior over an unknown field (protocol v2).

Two models:
  BlindTraceNet : q(B | one trace)              - per-trace amortized inference
  BlindSetNet   : q(B | all traces of session)  - set-conditioned (pooled) inference,
                  the amortized counterpart of pooled classical fitting

B is represented on an absolute grid over [500, 45000] nT (1024 bins, 43.5 nT) so the
network never receives the setpoint. Training uses instrument-anchored synthetic
sessions (real envelope population, real noise law, shared envelope + phase frame
within a session, fields drawn uniformly over the instrument range).
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.estimators.amortized import ResBlock  # noqa: E402
from src.synth import gen_traces, sample_envelope, sigma_at  # noqa: E402

B_LO, B_HI = 500.0, 45000.0
N_BINS = 1024
Y_MEAN, Y_SCALE = 0.89, 0.13
BIN_W = (B_HI - B_LO) / (N_BINS - 1)
_BINS = np.linspace(B_LO, B_HI, N_BINS)


class _Trunk(nn.Module):
    """Trace encoder. Channel 2 carries the periodogram magnitude of the same trace:
    a linear invertible re-encoding of the input (no extra information), which gives
    the network direct access to the fringe-frequency feature. The classical
    FFT+Rife baseline uses the same transform."""

    def __init__(self, width=96, n_blocks=5, n_ch=4):
        super().__init__()
        self.inp = nn.Conv1d(n_ch, width, kernel_size=7, padding=3)
        self.blocks = nn.Sequential(*[ResBlock(width, dil=2 ** (i % 3 + 1))
                                      for i in range(n_blocks)])
        self.out_dim = 2 * width + 3

    @staticmethod
    def periodogram(y_norm):
        # y_norm (B,T) -> normalized log-periodogram on the same T grid
        n = y_norm.shape[-1]
        sp = torch.fft.rfft(y_norm, dim=-1).abs()
        sp = torch.log1p(sp)
        sp = sp / (sp.amax(dim=-1, keepdim=True) + 1e-6)
        r = torch.nn.functional.interpolate(sp.unsqueeze(1), size=n, mode="linear",
                                            align_corners=False)
        return r.squeeze(1)

    def forward(self, y_norm, ctx):
        x = y_norm.unsqueeze(1)
        pg = self.periodogram(y_norm).unsqueeze(1)
        ctx_ch = ctx.unsqueeze(-1).expand(-1, 3, y_norm.shape[-1])
        h = F.gelu(self.inp(torch.cat([x, pg, ctx_ch], dim=1)))
        h = self.blocks(h)
        return torch.cat([h.mean(-1), h.amax(-1), ctx], dim=-1)


class SpectralTrunk(nn.Module):
    """Spectral encoder: windowed rFFT magnitude + unit-normalised real/imag parts.

    This is a linear re-encoding of the same trace (no extra information); the network
    learns the frequency->field map and its refinement jointly with the envelope
    marginalisation. Motivated by learnability: a raw CNN must discover a matched-filter
    bank from scratch, which is prohibitively slow at 1024-way output resolution.
    """

    def __init__(self, T=300, width=384, depth=3):
        super().__init__()
        nb = T // 2 + 1  # 151
        self.register_buffer("win", torch.hann_window(T))
        self.nb = nb
        d_in = 4 * nb + 3  # m, lm, re, im, ctx(3)
        layers = []
        d = d_in
        for _ in range(depth):
            layers += [nn.Linear(d, width), nn.GELU(), nn.LayerNorm(width)]
            d = width
        self.mlp = nn.Sequential(*layers)
        self.out_dim = width

    def forward(self, y_norm, ctx):
        sp = torch.fft.rfft(y_norm * self.win, dim=-1)          # (B, nb) complex
        mag = sp.abs()
        m = mag / (mag.amax(dim=-1, keepdim=True) + 1e-8)
        lm = torch.log1p(mag) - torch.log1p(mag).mean(dim=-1, keepdim=True)
        re = sp.real / (mag + 1e-8)
        im = sp.imag / (mag + 1e-8)
        feat = torch.cat([m, lm, re, im, ctx], dim=-1)
        return self.mlp(feat)


class BlindTraceNet(nn.Module):
    """q(B | single trace, log sigma)."""

    def __init__(self, n_bins=N_BINS, width=96, arch="cnn"):
        super().__init__()
        self.arch = arch
        self.trunk = _Trunk(width) if arch == "cnn" else SpectralTrunk()
        self.head = nn.Sequential(nn.Linear(self.trunk.out_dim, 512), nn.GELU(),
                                  nn.Linear(512, 512), nn.GELU(),
                                  nn.Linear(512, n_bins))

    def forward(self, y_norm, ctx):
        return self.head(self.trunk(y_norm, ctx))


class BlindSetNet(nn.Module):
    """q(B_c | session) for every column c - set-conditioned (in-context) inference."""

    def __init__(self, n_bins=N_BINS, width=96, emb=192, arch="cnn"):
        super().__init__()
        self.arch = arch
        self.trunk = _Trunk(width) if arch == "cnn" else SpectralTrunk()
        self.proj = nn.Sequential(nn.Linear(self.trunk.out_dim, emb), nn.GELU())
        self.attn = nn.MultiheadAttention(emb, num_heads=4, batch_first=True)
        self.head = nn.Sequential(nn.Linear(3 * emb + 3, 512), nn.GELU(),
                                  nn.Linear(512, 512), nn.GELU(),
                                  nn.Linear(512, n_bins))

    def forward(self, y_norm, ctx):
        # y_norm (B,N,T), ctx (B,N,2)
        B, N, T = y_norm.shape
        f = self.proj(self.trunk(y_norm.reshape(B * N, T), ctx.reshape(B * N, 3)))
        f = f.reshape(B, N, -1)
        ctx_r = ctx.reshape(B, N, 3)
        # attend WITH the log-sigma context so columns at the same budget group together
        q = f + ctx_r[:, :, 1:2]  # broadcast log sigma into the query space
        att, _ = self.attn(q, f, f)
        return self.head(torch.cat([f, att, att - f, ctx_r], dim=-1)
                         ).reshape(B * N, -1).reshape(B, N, -1)


def blind_session_batch(n_sessions, n_cols, tau, rng, reps_pool, sorted_fields=True,
                        env_mode="percol_shared_phase"):
    """Session = n_cols traces with distinct unknown fields spanning the instrument range.

    env_mode:
      "percol_shared_phase" (default, matches the real instrument): each column draws its
        own relaxation envelope from the real fitted population; the phase frame phi0 is
        shared across the session (measured circular concentration |R| >= 0.955).
      "shared": one identical envelope for the whole session (upper bound on pooling).
    """
    reps = rng.choice(np.asarray(reps_pool, dtype=float), size=n_sessions)
    sigma = np.array([sigma_at(r) for r in reps])
    u = rng.uniform(0, 1, size=(n_sessions, n_cols))
    if sorted_fields:
        u = np.sort(u, axis=1)
    B = B_LO + u * (B_HI - B_LO)
    Y = np.empty((n_sessions, n_cols, len(tau)))
    for s in range(n_sessions):
        if env_mode == "shared":
            env = np.repeat(sample_envelope(rng, 1, jitter=True), n_cols, axis=0)
        else:
            env = sample_envelope(rng, n_cols, jitter=True)
            # a single instrument phase frame per session: use the session mean phi0
            env[:, 4] = env[:, 4].mean()
        Y[s] = gen_traces(tau, B[s], env, sigma[s], rng)
    return Y, B, sigma


def fft_init_batch(Y):
    """Vectorised blind FFT+Rife field estimate per trace - the same initialisation the
    classical baselines receive. A function of the trace alone; no setpoint information."""
    Y = np.asarray(Y, dtype=float)
    S, C, T = Y.shape
    y = Y - Y.mean(axis=-1, keepdims=True)
    w = np.hanning(T)
    sp = np.abs(np.fft.rfft(y * w, axis=-1))
    f = np.fft.rfftfreq(T, d=0.02)          # MHz (tau in us, 20 ns step)
    G = 28e-6                                # MHz per nT
    idx = np.where((f >= G * B_LO * 0.9) & (f <= G * B_HI * 1.1))[0]
    k = idx[np.argmax(sp[..., idx], axis=-1)]
    df = f[1] - f[0]
    out = np.empty((S, C))
    for s in range(S):
        for c in range(C):
            kk = int(k[s, c])
            f_hat = f[kk]
            if 0 < kk < sp.shape[-1] - 1:
                a, b, cc = sp[s, c, kk - 1], sp[s, c, kk], sp[s, c, kk + 1]
                d = 0.5 * (a - cc) / (a - 2 * b + cc + 1e-12)
                f_hat = f[kk] + float(np.clip(d, -0.5, 0.5)) * df
            out[s, c] = f_hat / G
    return out


def _to_tensors(Y, sigma, device, n_cols, fft_init=None):
    yt = torch.tensor((Y - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)
    ls = np.log10(sigma)
    if fft_init is None:
        fft_init = np.full((Y.shape[0], n_cols), 0.5 * (B_LO + B_HI))
    fi = np.asarray(fft_init, dtype=float) / B_HI
    ctx = np.stack([np.zeros_like(ls), ls, np.zeros_like(ls)], axis=-1)  # (S,3)
    ctx = np.repeat(ctx[:, None, :], n_cols, axis=1)
    ctx[..., 2] = fi
    return yt, torch.tensor(ctx, dtype=torch.float32, device=device)


def train_blind(net, tau, which="set", steps=6000, n_sessions=8, n_cols=40, lr=2e-3,
                seed=0, device="cpu", log_every=300, arch="cnn",
                env_mode="percol_shared_phase",
                reps_pool=(5000, 10000, 20000, 40000, 80000, 160000, 320000, 640000),
                ckpt=None):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    net.to(device).train()
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps)
    losses = []
    for step in range(steps):
        Y, B, sigma = blind_session_batch(n_sessions, n_cols, tau, rng, reps_pool,
                                          env_mode=env_mode)
        yt, ctx = _to_tensors(Y, sigma, device, n_cols, fft_init=fft_init_batch(Y))
        Bt = torch.tensor(B, dtype=torch.float32, device=device)
        if which == "set":
            logits = net(yt, ctx)
        else:
            logits = net(yt.reshape(-1, yt.shape[-1]), ctx.reshape(-1, 3)
                         ).reshape(n_sessions, n_cols, -1)
        idx = torch.clamp(((Bt - B_LO) / (B_HI - B_LO) * (N_BINS - 1)).round().long(),
                          0, N_BINS - 1)
        tgt = F.one_hot(idx, N_BINS).float() * 0.99 + 0.01 / N_BINS
        loss = -(tgt * F.log_softmax(logits, -1)).sum(-1).mean()
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 5.0)
        opt.step(); sched.step()
        losses.append(loss.item())
        if log_every and (step + 1) % log_every == 0:
            print(f"  [{which}] step {step+1}/{steps} loss {np.mean(losses[-log_every:]):.4f}",
                  flush=True)
    if ckpt:
        os.makedirs(os.path.dirname(ckpt), exist_ok=True)
        torch.save({"state": net.state_dict(), "which": which}, ckpt)
    return losses


@torch.no_grad()
def predict_blind(net, Y, sigma, which="set", device="cpu", n_bins=N_BINS,
                  fft_init=None):
    """Y: (n_cols, n_tau) traces of ONE real session (use signal.T)."""
    net.eval().to(device)
    Y = np.asarray(Y, dtype=np.float64)
    if Y.shape[0] != 40 and Y.shape[1] == 40:
        Y = Y.T  # accept (n_tau, n_cols) defensively
    Yb = Y[None] if which == "set" else Y
    ls = np.log10(float(sigma))
    if fft_init is None:
        tmp = _to_tensors(Yb[None] if which == "set" else Yb, np.array([sigma]),
                          device, len(Y), fft_init=None)[1]
    n = len(Y)
    if which == "set":
        yt = torch.tensor((Yb - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)
        ctx = torch.tensor(np.zeros((1, n, 3), dtype=np.float32), device=device)
        ctx[:, :, 1] = ls
        if fft_init is not None:
            ctx[0, :, 2] = torch.tensor(np.asarray(fft_init) / B_HI, dtype=torch.float32,
                                        device=device)
        logits = net(yt, ctx)[0]
    else:
        yt = torch.tensor((Yb - Y_MEAN) / Y_SCALE, dtype=torch.float32, device=device)
        ctx = torch.tensor(np.tile([0.0, ls, 0.0], (n, 1)), dtype=torch.float32, device=device)
        if fft_init is not None:
            ctx[:, 2] = torch.tensor(np.asarray(fft_init) / B_HI, dtype=torch.float32,
                                     device=device)
        logits = net(yt, ctx)
    p = F.softmax(logits, -1).cpu().numpy()
    mean = (p * _BINS).sum(axis=1)
    var = (p * (_BINS[None, :] - mean[:, None]) ** 2).sum(axis=1)
    return mean, np.sqrt(np.clip(var, 0, None)), p
