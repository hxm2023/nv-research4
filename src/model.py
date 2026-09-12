"""Ramsey forward model and Cramer-Rao bound for field estimation.

s(tau) = C + A * exp(-(tau/T2)^p) * cos(2*pi*gamma*B*(tau + tau_off) + phi0)

Conventions: tau in us, B in nT, gamma = 2*pi*28e-6 rad/(us*nT).
tau_off ~ 18.6 ns (L1 confirm_tau_off) is a *known* instrument convention here.
"""
from __future__ import annotations

import numpy as np

GAMMA = 2 * np.pi * 28e-6  # rad/(us*nT)


def ramsey(tau_us, B_nT, A, C, T2_us, p, phi0, tau_off_us=0.0186):
    ph = GAMMA * B_nT * (tau_us + tau_off_us) + phi0
    return C + A * np.exp(-((tau_us / T2_us) ** p)) * np.cos(ph)


def _fisher_B(tau, B, A, C, T2, p, phi0, sigma, tau_off_us=0.0186):
    """Fisher information (scalar for B; envelope treated as fixed nuisance for
    the CRLB-of-B under known envelope). Numerical d/dB of the noiseless model."""
    h = max(1e-3, abs(B) * 1e-6)  # nT step
    s_p = ramsey(tau, B + h, A, C, T2, p, phi0, tau_off_us)
    s_m = ramsey(tau, B - h, A, C, T2, p, phi0, tau_off_us)
    d = (s_p - s_m) / (2 * h)
    return float(np.sum(d**2) / sigma**2)


def crlb_sigma_B(tau, B, A, C, T2, p, phi0, sigma, tau_off_us=0.0186):
    """Cramer-Rao lower bound on sigma_B with envelope known. nT."""
    return 1.0 / np.sqrt(_fisher_B(tau, B, A, C, T2, p, phi0, sigma, tau_off_us))


def crlb_sigma_B_free_envelope(tau, B, A, C, T2, p, phi0, sigma, tau_off_us=0.0186):
    """CRLB with envelope (A, C, T2, p, phi0) as free nuisance parameters.
    Numerical Fisher via central differences over the 6-parameter vector."""
    theta0 = np.array([B, A, C, T2, p, phi0], dtype=float)
    steps = np.array([max(1e-3, abs(B) * 1e-6), A * 1e-4, C * 1e-4,
                      T2 * 1e-4, 1e-4, 1e-4])
    n = len(theta0)
    J = np.zeros((len(tau), n))
    for k in range(n):
        h = steps[k]
        tp = theta0.copy(); tp[k] += h
        tm = theta0.copy(); tm[k] -= h
        sp = ramsey(tau, *tp)
        sm = ramsey(tau, *tm)
        J[:, k] = (sp - sm) / (2 * h)
    F = (J.T @ J) / sigma**2
    Finv = np.linalg.pinv(F)
    return float(np.sqrt(Finv[0, 0]))


def crlb_sigma_B_joint(tau, B_vec, A, C, T2, p, phi0, sigma, tau_off_us=0.0186):
    """Joint CRLB when one SHARED envelope is estimated from N_cols columns
    (each column has its own B, sharing A, C, T2, p, phi0). Returns sigma_B per column."""
    ncol = len(B_vec)
    theta0 = np.concatenate([B_vec, [A, C, T2, p, phi0]])
    n = len(theta0)
    steps = np.concatenate([np.maximum(1e-3, np.abs(B_vec) * 1e-6),
                            [A * 1e-4, C * 1e-4, T2 * 1e-4, 1e-4, 1e-4]])
    J = np.zeros((ncol * len(tau), n))
    for k in range(n):
        h = steps[k]
        tp = theta0.copy(); tp[k] += h
        tm = theta0.copy(); tm[k] -= h
        Bp, Bm = tp[:ncol], tm[:ncol]
        envp = tp[ncol:]; envm = tm[ncol:]
        sp = np.concatenate([ramsey(tau, Bp[c], *envp) for c in range(ncol)])
        sm = np.concatenate([ramsey(tau, Bm[c], *envm) for c in range(ncol)])
        J[:, k] = (sp - sm) / (2 * h)
    F = (J.T @ J) / sigma**2
    Finv = np.linalg.pinv(F)
    return np.sqrt(np.clip(np.diag(Finv)[:ncol], 0, None))
