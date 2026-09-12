"""Classical baselines for DC Ramsey field estimation (fair, generously tuned).

All baselines get the same real trace, the same tau/B grids, and are tuned on the
dev sheets (3-8), never on the test sheets (1-2).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares

from .model import GAMMA, ramsey

TAU_OFF_US = 0.0186


def _resid(th, tau, y, tau_off_us):
    B, A, C, T2, p, phi0 = th
    return ramsey(tau, B, A, C, T2, p, phi0, tau_off_us) - y


def _bounds(B_lo, B_hi):
    return ([B_lo, 0.005, 0.3, 0.5, 0.5, -20.0],
            [B_hi, 0.60, 1.4, 40.0, 6.0, 20.0])


def lm_multistart(tau, y, B_lo, B_hi, n_starts=49, tau_off_us=TAU_OFF_US,
                  A0=0.128, C0=0.89, T2_0=5.4, p0=1.8):
    """Multi-start Levenberg-Marquardt: grid over B and phi0, share A/C/T2/p inits."""
    Bs = np.linspace(B_lo, B_hi, int(np.ceil(np.sqrt(n_starts))))
    phis = np.linspace(-np.pi, np.pi, int(np.ceil(n_starts / len(Bs))), endpoint=False)
    lo, hi = _bounds(B_lo, B_hi)
    best = None
    for B0 in Bs:
        for ph0 in phis:
            x0 = [B0, A0, C0, T2_0, p0, ph0]
            try:
                r = least_squares(_resid, x0, args=(tau, y, tau_off_us),
                                  bounds=(lo, hi), max_nfev=1500)
            except Exception:
                continue
            if best is None or r.cost < best.cost:
                best = r
    if best is None:
        return None
    B, A, C, T2, p, phi0 = best.x
    return {"B": float(B), "A": float(A), "C": float(C), "T2": float(T2),
            "p": float(p), "phi0": float(phi0), "cost": float(best.cost)}


def fft_rife(tau, y, B_lo, B_hi, tau_off_us=TAU_OFF_US):
    """FFT peak + Rife-style interpolation of the fringe frequency."""
    yc = y - y.mean()
    n = len(yc)
    w = np.hanning(n)
    f = np.fft.rfftfreq(n, d=tau[1] - tau[0])
    sp = np.abs(np.fft.rfft(yc * w))
    # restrict to plausible fringe frequencies
    f_lo, f_hi = GAMMA * B_lo / (2 * np.pi), GAMMA * B_hi / (2 * np.pi)
    m = (f >= f_lo * 0.9) & (f <= f_hi * 1.1)
    if not m.any():
        return None
    idx = np.where(m)[0][np.argmax(sp[m])]
    k = idx
    # Rife interpolation using neighbors (on the raw periodogram)
    f_hat = f[k]
    if 0 < k < len(sp) - 1:
        a, b, c = sp[k - 1], sp[k], sp[k + 1]
        delta = 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
        delta = float(np.clip(delta, -0.5, 0.5))
        f_hat = f[k] + delta * (f[1] - f[0])
    B_hat = 2 * np.pi * f_hat / GAMMA
    return {"B": float(B_hat)}


def grid_bayes(tau, y, B_grid, sigma, T2_grid=None, p_fixed=1.8,
               A0=0.128, C0=0.89, tau_off_us=TAU_OFF_US, phi0_grid=None):
    """Marginal posterior over B on a grid, profiling A/C/T2 (concentrated likelihood)
    and marginalizing phi0 on a coarse grid. Returns posterior mean/std."""
    if T2_grid is None:
        T2_grid = np.linspace(3.0, 9.0, 13)
    if phi0_grid is None:
        phi0_grid = np.linspace(-np.pi, np.pi, 25, endpoint=False)
    logL = np.full(len(B_grid), -np.inf)
    for i, B in enumerate(B_grid):
        best = -np.inf
        for T2 in T2_grid:
            env = np.exp(-((tau / T2) ** p_fixed))
            for phi0 in phi0_grid:
                basis = np.cos(GAMMA * B * (tau + tau_off_us) + phi0) * env
                # linear least squares for [A, C]
                M = np.column_stack([basis, np.ones_like(tau)])
                try:
                    coef, res, *_ = np.linalg.lstsq(M, y, rcond=None)
                except np.linalg.LinAlgError:
                    continue
                r = y - M @ coef
                ll = -0.5 * np.sum(r**2) / sigma**2
                if ll > best:
                    best = ll
        logL[i] = best
    logL -= logL.max()
    w = np.exp(logL)
    S = w.sum()
    if not np.isfinite(S) or S <= 0:
        return None
    w = w / S
    mean = float(np.sum(w * B_grid))
    var = float(np.sum(w * (B_grid - mean) ** 2))
    return {"B": mean, "sd": float(np.sqrt(max(var, 0.0))), "post": w}


def joint_lm(tau, Y, B_init, shared_envelope=True, tau_off_us=TAU_OFF_US,
             A0=0.128, C0=0.89, T2_0=5.4, p0=1.8):
    """Joint fit across columns with one shared envelope (A,C,T2,p,phi0 shared, per-col B).

    Y: (n_tau, n_cols) real traces. Returns per-column B estimates.
    """
    ncol = Y.shape[1]
    B_init = np.asarray(B_init, dtype=float)

    def pack_resid(th):
        B = th[:ncol]
        A, C, T2, p, phi0 = th[ncol:ncol + 5]
        out = np.empty((len(tau), ncol))
        for c in range(ncol):
            out[:, c] = ramsey(tau, B[c], A, C, T2, p, phi0, tau_off_us) - Y[:, c]
        return out.ravel()

    x0 = np.concatenate([B_init, [A0, C0, T2_0, p0, 0.0]])
    lo = np.concatenate([B_init * 0.75, [0.02, 0.5, 3.0, 0.8, -np.pi]])
    hi = np.concatenate([B_init * 1.25, [0.45, 1.2, 12.0, 4.0, np.pi]])
    r = least_squares(pack_resid, x0, bounds=(lo, hi), max_nfev=200 * ncol)
    B = r.x[:ncol]
    return {"B": B, "env": r.x[ncol:], "cost": float(r.cost)}
