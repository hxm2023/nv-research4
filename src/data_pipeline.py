"""Real-data pipeline for L5: DC Ramsey sheets (8 rep levels x 300 tau x 40 B columns).

Locked conventions (see CLAUDE.md):
  tau_i = 20*i ns, i=1..300  (0.02 .. 6.0 us)
  B_n   = 1071.4*n nT, n=1..40  (applied field = 0.010714285714286*n Gauss)
  reps r in {5k,10k,20k,40k,80k,160k,320k,640k} per sheet
  gamma = 2*pi*28e-6 rad/(us*nT)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

GAMMA = 2 * np.pi * 28e-6          # rad/(us*nT)
TAU_STEP_NS = 20.0
TAU_OFF_NS = 18.6                  # L1 confirm_tau_off (cite; not re-claimed here)
TAU_OFF_NS_SIGMA = 2.6
REP_LEVELS = [5_000, 10_000, 20_000, 40_000, 80_000, 160_000, 320_000, 640_000]
B_STEP_NT = 1071.4
N_TAU = 300
N_COLS = 40

DC_XLS = os.path.join(ROOT, "data_lab", "DC magnetic field sensing.xls")


@dataclass(frozen=True)
class DCDataset:
    """signal[sheet_idx, tau_idx, col_idx]; tau_us[300]; B_nT[40]; reps[8]."""
    signal: np.ndarray
    tau_us: np.ndarray
    B_nT: np.ndarray
    reps: np.ndarray

    def sheet(self, i: int) -> np.ndarray:
        return self.signal[i]


def tau_grid() -> np.ndarray:
    return TAU_STEP_NS * np.arange(1, N_TAU + 1) / 1000.0  # microseconds


def B_grid() -> np.ndarray:
    return B_STEP_NT * np.arange(1, N_COLS + 1)  # nT


NPZ = os.path.join(ROOT, "data", "dc_real.npz")


def load_dc(path: str = DC_XLS) -> DCDataset:
    """Real DC sheets. Reads the cached .npz when present (identical to the .xls
    export; see tools/export_npz.py), else parses the .xls directly."""
    if os.path.exists(NPZ):
        z = np.load(NPZ)
        sig = z["signal"].astype(np.float64)
    else:
        xl = pd.read_excel(path, sheet_name=None, header=None)
        sheets = [xl[f"Sheet{k+1}"].values.astype(np.float64) for k in range(8)]
        sig = np.stack(sheets, axis=0)
    assert sig.shape == (8, N_TAU, N_COLS), sig.shape
    assert np.isfinite(sig).all(), "non-finite values in real data"
    return DCDataset(sig, tau_grid(), B_grid(), np.asarray(REP_LEVELS, dtype=float))


def frozen_split(path: str | None = None) -> dict:
    """Audited split frozen at Phase 1. Train/dev on sheets 3-8 columns 1..40 minus
    holdout; test = sheets 1-2 (the low-photon sheets) - never used for training.
    Also hold out columns {7,14,21,28,35} in every sheet for off-grid-free dev.
    """
    if path is None:
        path = os.path.join(ROOT, "results", "frozen_split.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    cols = list(range(1, N_COLS + 1))
    dev_cols = [c for c in cols if c % 7 != 0]
    hold_cols = [c for c in cols if c % 7 == 0]
    split = {
        "version": 1,
        "frozen_at": "2026-09-12",
        "rule": "test sheets = {1,2} (5k,10k reps); train/dev sheets = {3..8}; "
                "dev columns = all except multiples of 7; holdout columns = multiples of 7",
        "test_sheets": [1, 2],
        "train_sheets": [3, 4, 5, 6, 7, 8],
        "dev_cols": dev_cols,
        "holdout_cols": hold_cols,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(split, f, indent=2)
    return split


def per_point_noise(signal: np.ndarray, tau_us: np.ndarray) -> dict:
    """Robust white-noise estimate per sheet using local 3-point quadratic detrend."""
    out = {}
    for i in range(signal.shape[0]):
        r = signal[i]
        # second difference over 3 consecutive tau points; for smooth trend + white noise
        d2 = r[2:, :] - 2 * r[1:-1, :] + r[:-2, :]
        # std of d2 ~ sqrt(6)*sigma for white noise; smooth trend contributes little
        sigma = np.std(d2) / np.sqrt(6.0)
        out[f"sheet{i+1}"] = float(sigma)
    return out


if __name__ == "__main__":
    ds = load_dc()
    print("signal", ds.signal.shape, "tau", ds.tau_us[[0, -1]], "B", ds.B_nT[[0, -1]])
    print("frozen split:", frozen_split())
    noise = per_point_noise(ds.signal, ds.tau_us)
    print("per-point noise (robust d2 estimator):")
    for k, v in noise.items():
        print(f"  {k}: {v:.5f}")
