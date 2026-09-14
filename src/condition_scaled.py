"""Regenerate results/condition_scaled.json: the dimensionless conditioning diagnostic for
the pooled fit (appendix of the manuscript).

The raw cond(J^T J) is dominated by the units of the parameters (fields in nT against
envelope parameters of order unity). Rescaling every Jacobian column to unit norm removes
that, and the resulting condition number is the meaningful flat-direction test.

Usage: python -m src.condition_scaled
"""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, ".")
from src.audit_fits import pooled_objective
from src.blind_eval import fft_blind
from src.data_pipeline import REP_LEVELS, load_dc
from src.robustness_checks import pooled_fit

OUT = "results/condition_scaled.json"


def main():
    ds = load_dc()
    tau = ds.tau_us
    cols = list(range(6, 40))
    out = {}
    for si, r in enumerate(REP_LEVELS):
        Y = ds.signal[si][:, cols]
        Bf = np.array([fft_blind(tau, Y[:, c]) for c in range(len(cols))])
        B = pooled_fit(tau, Y, Bf)
        x0, bounds, resid = pooled_objective(tau, Y, Bf)
        x = np.concatenate([B, x0[len(B):]])
        J = np.zeros((Y.size, len(x)))
        for k in range(len(x)):
            h = 1e-4 * max(1.0, abs(x[k]))
            xp, xm = x.copy(), x.copy()
            xp[k] += h; xm[k] -= h
            J[:, k] = (resid(xp) - resid(xm)) / (2 * h)
        nrm = np.linalg.norm(J, axis=0)
        nrm[nrm == 0] = 1.0
        sv = np.linalg.svd(J / nrm, compute_uv=False)
        out[int(r)] = {"cond_scaled": float(sv[0] / sv[-1]),
                       "smallest_sv_scaled": float(sv[-1])}
        print(f"r={int(r):>7}: cond(J_scaled)={out[int(r)]['cond_scaled']:.2f}", flush=True)
    json.dump(out, open(OUT, "w"), indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
