import numpy as np
import sys

sys.path.insert(0, '.')
from src.estimators.blind import BlindSetNet, train_blind, predict_blind
from src.data_pipeline import load_dc

ds = load_dc()
tau = ds.tau_us
arch = sys.argv[1] if len(sys.argv) > 1 else 'spec'
steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
net = BlindSetNet(arch=arch)
print('arch', arch, 'params', sum(p.numel() for p in net.parameters()), flush=True)
l = train_blind(net, tau, which='set', steps=steps, n_sessions=6, n_cols=40, seed=0,
                device='cuda', arch=arch, log_every=max(100, steps // 8))
print('final loss:', float(np.mean(l[-100:])), flush=True)
for si in [0, 1, 2, 7]:
    m, s, _ = predict_blind(net, ds.signal[si], 0.207 * np.sqrt(5000 / ds.reps[si]),
                            which='set', device='cuda')
    e = np.abs(m - ds.B_nT)
    print(f'  sheet{si+1} r={int(ds.reps[si]):>6}: med={np.median(e):7.0f} '
          f'mean={e.mean():7.0f} <500={np.mean(e < 500) * 100:3.0f}%', flush=True)
