"""Instrument-anchored synthetic Ramsey data.

Design rule (CLAUDE.md): synthetic data may be used for TRAINING only, never in
headline evaluation, and must be anchored to real instrument statistics:
  * envelope population from real per-column fits at high repetition (Sheet8)
  * noise law sigma(r) = 0.207*sqrt(5000/r)  (verified on all 8 real sheets)
  * B sampled uniformly in the estimation window  -> the induced prior is flat,
    matching the flat prior of the classical baselines (no prior advantage)
  * tau_off = 18.6 ns instrument convention (cited)
"""
from __future__ import annotations

import json
import os

import numpy as np

from .model import ramsey

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_JSON = os.path.join(ROOT, "results", "envelope_sheet8.json")

NOISE_AMP = 0.207          # sigma at 5000 reps
NOISE_R0 = 5000.0


def sigma_at(reps: float) -> float:
    return NOISE_AMP * np.sqrt(NOISE_R0 / reps)


def envelope_population(rng=None, n=None):
    """Empirical-bootstrap of real per-column envelope fits (A, C, T2, p, phi0)."""
    with open(ENV_JSON) as f:
        env = np.array(json.load(f)["env_sheet8"])
    if n is None:
        return env
    rng = rng or np.random.default_rng(0)
    idx = rng.integers(0, len(env), size=n)
    return env[idx]


def sample_envelope(rng, n, jitter=True):
    """Bootstrap real envelopes with mild multiplicative jitter (to cover the
    population between the 40 measured columns rather than only on them)."""
    env = envelope_population(rng, n).copy()
    if jitter:
        env[:, 0] *= 1 + 0.03 * rng.standard_normal(n)      # A
        env[:, 1] *= 1 + 0.005 * rng.standard_normal(n)     # C
        env[:, 2] *= 1 + 0.06 * rng.standard_normal(n)      # T2
        env[:, 3] = np.clip(env[:, 3] * (1 + 0.10 * rng.standard_normal(n)), 1.0, 4.0)
        env[:, 4] += 0.15 * rng.standard_normal(n)          # phi0
    return env


def gen_traces(tau_us, B_nT, env, sigma, rng, tau_off_us=0.0186):
    """Vectorized: B_nT (n,), env (n,5), sigma scalar or (n,). Returns (n, len(tau))."""
    A, C, T2, p, phi0 = env.T
    B_nT = np.asarray(B_nT, dtype=float).reshape(-1, 1)
    tau = tau_us.reshape(1, -1)
    A = A.reshape(-1, 1); C = C.reshape(-1, 1)
    T2 = T2.reshape(-1, 1); p = p.reshape(-1, 1); phi0 = phi0.reshape(-1, 1)
    env_f = np.exp(-((tau / T2) ** p))
    ph = np.pi * 2 * 28e-6 * B_nT * (tau + tau_off_us) + phi0
    s = C + A * env_f * np.cos(ph)
    sig = np.asarray(sigma).reshape(-1, 1) if np.ndim(sigma) else sigma
    return s + sig * rng.standard_normal(s.shape)


def gen_dataset(n, tau_us, B_center_nT, window_nT, reps, rng, jitter=True):
    B = B_center_nT + rng.uniform(-window_nT, window_nT, size=n)
    env = sample_envelope(rng, n, jitter=jitter)
    sigma = sigma_at(reps)
    Y = gen_traces(tau_us, B, env, sigma, rng)
    return Y, B, env
