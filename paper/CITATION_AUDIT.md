# Citation Audit Report

**Date**: 2026-09-13 · **Manuscript**: `paper/main.tex` · **Entries**: 14
**Method**: each entry checked against external sources (publisher/DOI records, journal
listing pages, arXiv abstract pages fetched live), and each `\cite` checked against the
sentence it supports.

## Verdict: **WARN** — all 14 entries exist and every citation context is appropriate;

5 entries had metadata errors, all now fixed and recompiled.

## Corrections applied

| Entry | Was | Now | Why |
|---|---|---|---|
| `Rife1970` | `D. Rife and R. Boorstyn, Bell Syst. Tech. J. 49, 197 (1970)` | `D. C. Rife and G. A. Vincent, Bell Syst. Tech. J. 49, 197 (1970)` | Vol. 49, p. 197 (1970) is **"Use of the DFT in the Measurement of Frequencies and Levels of Tones"** by Rife & **Vincent**. Rife & Boorstyn is a different, later paper (BSTJ 55, 1389 (1976)) and the wrong attribution here. |
| `NVRNet2026` | `Y. Shang and G. D. Fuchs, arXiv:2603.14144` | `C. Shang and G. D. Fuchs, arXiv:2603.14144` | arXiv page lists the author as **Chao** Shang. |
| `Guo2025` | `J. Guo et al., arXiv:2506.13469` | `S. Guo et al., arXiv:2506.13469` | arXiv page lists the first author as **Shiqian** Guo. |
| `Haim2025` | `A. Haim et al., arXiv:2409.12820 (2025)` | `G. Haim et al., Mach. Learn.: Sci. Technol. 6, 025074 (2025)` | First author is **Galya** Haim; the paper is now published (DOI 10.1088/2632-2153/ade51c), so the published venue replaces the preprint. |
| `Daniel2026` | `D. Daniel et al., arXiv:2608.19582` | `J. Daniel et al., arXiv:2608.19582` | arXiv page lists the first author as **Jonathan** Daniel. |

## Verified without change

| Entry | Check | Result |
|---|---|---|
| `Taylor2008` | Nat. Phys. **4**, 810 (2008), "High-sensitivity diamond magnetometer with nanoscale resolution" | correct (DOI 10.1038/nphys1075) |
| `Maze2008` | Nature **455**, 644 (2008) | correct |
| `Balasubramanian2008` | Nature **455**, 648 (2008) | correct |
| `Degen2017` | Rev. Mod. Phys. **89**, 035002 (2017) | correct |
| `Barry2020` | Rev. Mod. Phys. **92**, 015004 (2020) | correct |
| `Rondin2014` | Rep. Prog. Phys. **77**, 056503 (2014) | correct |
| `Santagati2019` | Phys. Rev. X **9**, 021019 (2019) | correct — and the cited claim ("the strongest low-photon result... one photon per step, 60 nT s^(1/2)") matches the paper's actual content |
| `Youssry2026` | arXiv:2601.17465, "Bayesian quantum sensing using graybox machine learning" | correct |

## Citation-context check

- `\cite{Guo2025,NVRNet2026,Haim2025,Daniel2026,Youssry2026}` → *"Learned estimators for NV
  data have appeared recently"*: all five are learned/ML estimators for NV magnetic sensing.
  SUPPORTS.
- `\cite{NVRNet2026,Daniel2026}` → *"the simulation-to-reality gap is repeatedly identified as
  the central difficulty"*: Shang & Fuchs train on simulated Ramsey data; Daniel et al. is
  explicitly a *sim-to-real calibration* paper. SUPPORTS.
- `\cite{Rife1970}` → *"initialised identically from a blind FFT+Rife estimate"*: the cited
  paper is the DFT-frequency-estimation-with-interpolation method the estimator uses.
  SUPPORTS (with the corrected authorship).
- `\cite{Taylor2008,Maze2008,Balasubramanian2008,Degen2017,Barry2020}` (intro) and
  `\cite{Barry2020,Rondin2014}` (sensitivity discussion), `\cite{Santagati2019}` (delay-time
  choice): all standard and appropriate. SUPPORTS.

## Open item flagged to the authors

`L1companion` is cited for the timing-offset convention
(`τ_off = 18.6 ± 2.6 ns`) but is an **unpublished companion manuscript**. This is legitimate
as a convention citation, but a referee may object to a load-bearing instrument parameter
resting on an unpublished work. Options before submission:
(i) ensure the companion has an arXiv ID by submission time and cite that;
(ii) state the offset as measured in this work and cite the companion only for the
phase-frame convention;
(iii) keep as-is and accept the referee risk.
The numerical claims of this paper do not depend on which option is chosen.
