# Referee review block: neural

I evaluate only the learned estimator and claim–evidence fidelity.

**1. Budget-dependent sharing or undertraining?**  
The pattern is suggestive but not conclusive. Strictly, the network is worse than pooling at 5–20k reps (504/387/289 vs 439/344/272 nT) and only statistically unresolved at 40k (172 vs 176); it also trails *partial* through 40k (465/343/261/146 vs 504/387/289/172). Pooling then stagnates (80k: 215; 160k: 175; 320k: 174), while the network continues to improve and is best at 80–320k (139, 113, 88). That resembles noise-adaptive sharing.

But only five-seed medians are reported; no seed spreads or confidence intervals are given. The apparent crossover could be within seed variation, and the low-budget deficit is exactly where undertraining or insufficient capacity would appear. Required evidence:

- per-budget learning curves (RMSE and negative log-likelihood vs epochs); continued low-\(r\) improvement would indicate undertraining;
- seed-level RMSE/IQR and larger/longer-trained models; a stable crossover would support genuine behaviour;
- ablation removing the 40-column attention; loss of the high-\(r\) advantage would implicate learned sharing;
- per-\(r\) oracle/Bayes bounds; a converged model near the bound at high \(r\) but not low \(r\) would support meaningful adaptation.

**2. Is “structure-free” supported?**  
No. Conditioning on \(\log\sigma\) is not the same as learning structure. The estimator is heavily structured: rFFT spectral inputs, correction around a blind FFT+Rife estimate, a \(\pm 8~\mu\text{T}\) 512-bin posterior grid, permutation-invariant attention over exactly 40 traces, and synthetic sessions with one shared phase frame, per-column \(T_2^*\), measured envelope population and measured shot-noise law. The numbers support only “budget-adaptive within the trained session/simulator”: the network beats pooling when pooled bias dominates (80k: 139 vs 215; 160k: 113 vs 175; 320k: 88 vs 174). They do not show that it can discover unknown sharing structure under model mismatch.

**3. Synthetic training adequacy and sim-to-reality gap**  
The synthetic set is anchored but not sufficient for strong claims. It omits real low-budget traces, so it may miss low-count readout artifacts, drift, correlated noise, digitization effects, or phase glitches. The real-data evaluation may not expose this because the same session is used for all methods and only point RMSE is shown.

I would demand at least one of:

- train/validate with held-out real low-\(r\) traces;
- inject synthetic signals into real background/residual traces;
- fine-tune or domain-adapt on unlabeled real low-\(r\) data;
- test additional sessions/instruments.

Then compare 5–40k performance (currently 504/387/289/172 vs pooling 439/344/272/176). Also require posterior calibration/coverage using high-\(r\) pseudo-labels or downsampling. If real-noise training does not change performance or calibration, the gap is likely small; if low-\(r\) RMSE improves materially, the original synthetic set was inadequate.

**4. Overstatement and rewrite**  
Yes. Weakest claim: **“structure-free budget-adaptive inference.”**

Supported rewrite:

> “In one instrument session and within the synthetic training distribution, the network exhibits repetition-dependent sharing: it is worse than pooling at 5–20k reps (504/387/289 vs 439/344/272 nT), statistically indistinguishable from pooling at 40k (172 vs 176), and lower-RMSE than pooling and partial pooling at 80–320k (139/113/88 vs 215/175/174 and 151/123/123). It is not best at 640k (66 vs lm 59), and the data do not establish structure-free inference or generalization beyond this setting.”
