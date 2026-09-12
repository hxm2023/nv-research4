"""Diagnose the ~100 nT systematic offset of the amortized networks.

Runs the trained network on SYNTHETIC sessions with exact ground truth (both the
training distribution and a uniform-grid session) to separate a model artefact from a
train/test distribution mismatch.
"""
import json
import sys

import numpy as np
import torch

sys.path.insert(0, ".")
from src.data_pipeline import load_dc
from src.estimators.blind import (B_HI, B_LO, BlindSetNet, blind_session_batch,
                                  fft_init_batch, predict_blind)

ds = load_dc()
tau = ds.tau_us
dev = "cuda" if torch.cuda.is_available() else "cpu"
net = BlindSetNet(arch="spec")
ck = torch.load("checkpoints/blind_set_seed0.pt", map_location=dev)
net.load_state_dict(ck["state"])

for tag, mode in [("sorted-uniform (training dist)", "train"),
                  ("uniform grid (real protocol)", "grid")]:
    rng = np.random.default_rng(7)
    Y, B, sigma = blind_session_batch(3, 40, tau, rng, (5000.0, 5000.0),
                                      env_mode="percol_shared_phase")
    if mode == "grid":
        step = 1071.4
        off = rng.uniform(500, 3000, size=Y.shape[0])
        B = off[:, None] + step * np.arange(40)[None, :]
        from src.synth import gen_traces, sample_envelope
        Y = np.empty_like(Y)
        for s in range(Y.shape[0]):
            env = sample_envelope(rng, 40, jitter=True)
            env[:, 4] = env[:, 4].mean()
            Y[s] = gen_traces(tau, B[s], env, 0.207, rng)
    for s in range(Y.shape[0]):
        fi = fft_init_batch(Y[s][None])[0]
        m, sd, _ = predict_blind(net, Y[s], 0.207, which="set", device=dev, fft_init=fi)
        e = m - B[s]
        print(f"  [{tag}] session{s}: mean_err={np.mean(e):+8.1f} nT  "
              f"median|e|={np.median(np.abs(e)):7.1f}  rmse={np.sqrt(np.mean(e**2)):7.1f}  "
              f"post_sd={np.mean(sd):6.0f}")
