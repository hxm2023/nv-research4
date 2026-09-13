"""Rewrite the manuscript for the consistent primary-region (34-setting) session
definition, and report the session-definition sensitivity the referee asked for."""
import re

p = "paper/main.tex"
s = open(p, encoding="utf-8").read()
n_ok = 0


def rep(old, new):
    global s, n_ok
    if old in s:
        s = s.replace(old, new)
        n_ok += 1
    else:
        print("MISS:", old[:70].replace("\n", " "))


# ---------------- abstract ----------------
rep(r"""Pooling is not free: it carries a
\emph{bias floor} set by the measured inhomogeneity of the relaxation envelope
($T_2^{*}=\envTstarMean\pm\envTstarStd\mus$ across the $\nCols$ columns), which is invisible
while photons are scarce and dominant once they are not. Both estimators obey a two-term
law $\dB(r)=\sqrt{A^{2}(5000/r)+b^{2}}$ with $A=\lawALm$~nT, $b=\lawBLm$~nT for per-trace
fitting and $A=\lawAPool$~nT, $b=\lawBPool$~nT for pooled fitting, crossing at
$r^{*}\approx\crossoverRepsRounded\times10^{4}$ repetitions. A synthetic control with
exact ground truth reproduces the crossover, confirming that it is a property of the
estimator structure and of the instrument's envelope inhomogeneity rather than of the
data-analysis pipeline.""",
r"""Both estimators obey a two-term law
$\dB(r)=\sqrt{A^{2}(5000/r)+b^{2}}$ with $A=\lawALm$~nT, $b=\lawBLm$~nT for per-trace
fitting and $A=\lawAPool$~nT, $b=\lawBPool$~nT when the pooling is restricted to field
settings that are individually constrainable, so that pooling is the better strategy
essentially throughout the measured ladder. Pooling the full sweep instead --- including
$\tau$ records too short for the field to be identifiable from a single trace --- degrades
the shared nuisance and produces an apparent $\sim\!150$~nT floor that advances the
crossover to $r^{*}\approx1\times10^{5}$ repetitions. The choice of \emph{which} settings
enter the pooled session is therefore as important as the choice of pooling itself, and it
is what a synthetic control with exact ground truth isolates.""")

rep(r"""The floor is attributable: at the
highest budget, releasing the relaxation time per field setting removes it entirely
(RMSE $371\to73$~nT), whereas releasing the contrast or the stretch exponent changes nothing,
so the practical rule is to share only what is genuinely common --- the phase frame and the
contrast --- and to leave the relaxation time free once photons stop being the limit.""",
r"""The practical rule that follows is not
"pool then stop sharing" but "pool over settings you can also constrain individually": an
instrument's sweep often contains records that a single trace cannot identify, and those
records corrupt the very shared nuisance the pooling is meant to estimate.""")

# ---------------- results: ladder ----------------
rep(r"""Session pooling attains $\rmsePoolFiveK$~nT against a joint bound of
$\crlbJointFiveK$~nT, also efficient. The pooled estimator is better by a factor
$\ratioLmPoolFiveK$ at $\rMinK$k repetitions ($\ratioLmPoolTenK$ at $10$k), and that factor is
the same one by which pooling lowers the bound.""",
r"""Session pooling attains $\rmsePoolFiveK$~nT against a joint bound of
$\crlbJointFiveK$~nT, also efficient, and is better than per-trace fitting by a factor
$\ratioLmPoolFiveK$ at $\rMinK$k repetitions ($\ratioLmPoolTenK$ at $10$k).""")

# ---------------- results: the law ----------------
rep(r"""Table~\ref{tab:ladder} also shows the reversal: above $\sim\!80$k repetitions the pooled
estimator stops improving and is overtaken by per-trace fitting. The reason is visible in
the estimator bias (lower panel of Fig.~\ref{fig:ladder}). The per-trace bias stays within
$\pm\biasLmEightyK$~nT of zero across the whole ladder, whereas the pooled estimator carries
a positive bias of order $100$~nT from $80$k repetitions upward
($\biasPoolEightyK$~nT at $80$k, $\biasPoolSixFortyK$~nT at $\rMaxK$k): once the statistical
error falls below the shared-model error, the latter dominates the total.""",
r"""Table~\ref{tab:ladder} shows that with the primary-region session the pooled estimator
remains ahead of per-trace fitting at every budget up to $320$k repetitions and is
essentially tied at $\rMaxK$k ($\rmsePoolSixFortyK$ against $\rmseLmSixFortyK$~nT); the two
bias curves in the lower panel of Fig.~\ref{fig:ladder} stay comparable over the whole
ladder.""")

rep(r"""Fitting
the measured ladders gives $A=\lawALm$~nT and $b=\lawBLm$~nT for per-trace fitting (fit rms
$\lawFitLm$~nT) and $A=\lawAPool$~nT and $b=\lawBPool$~nT for pooled fitting (fit rms
$\lawFitPool$~nT). The photon-limited coefficients differ by the bound ratio,
$(A_{\rm lm}/A_{\rm pool})^{2}=\photonGainFactor$: pooling is worth a factor
$\sqrt{\photonGainFactor}$ in precision while photons are scarce, while its floor
$b_{\rm pool}=\lawBPool$~nT eventually costs more than it buys. Equating the two curves
gives the crossover $r^{*}\approx\crossoverReps$ repetitions, with a $95\%$ confidence
interval of $[\crossoverCIlow$--$\crossoverCIhigh]\times10^{4}$ repetitions obtained by
bootstrapping the $\nCols$ columns (200 draws; the interval reflects the column-to-column
scatter of the fitted ladder, not session-to-session reproducibility). Expressed
operationally: to
reach the precision that pooled inference achieves at $\rMinK\times10^{3}$ repetitions,
per-trace fitting needs $\photonGainFactor$ times more repetitions; above
$\crossoverRepsRounded\times10^{4}$ repetitions the ordering reverses and per-trace fitting
is the better choice.""",
r"""Fitting the measured
ladders gives $A=\lawALm$~nT and $b=\lawBLm$~nT for per-trace fitting (fit rms
$\lawFitLm$~nT) and $A=\lawAPool$~nT and $b=\lawBPool$~nT for pooled fitting (fit rms
$\lawFitPool$~nT). The photon-limited coefficients differ by
$(A_{\rm lm}/A_{\rm pool})^{2}=\photonGainFactor$: pooling is worth a factor
$\sqrt{\photonGainFactor}$ in precision while photons are scarce, and with
$b_{\rm pool}=\lawBPool$~nT the two curves cross only at
$r^{*}\approx\crossoverReps$ repetitions. Expressed operationally: to reach the precision
that pooled inference achieves at $\rMinK\times10^{3}$ repetitions, per-trace fitting needs
$\photonGainFactor$ times more repetitions, and throughout the measured range up to
$\rMaxK$k the pooled estimator is never the worse choice by more than the $\sim\!50$~nT
per-column systematic discussed above.""")

# ---------------- mechanism section ----------------
start = s.index(r"\subsection{Mechanism: a bias floor set by envelope inhomogeneity}")
end = s.index(r"\subsection{Sensitivity}")
new_mech = r"""\subsection{What sets the floor: the session definition}
\label{sec:control}

The two-term law above was fitted to a pooled session built from the $34$ field settings of
the primary region. That choice is not innocent, and it is the one place where our earlier
analysis changed its mind: an equally natural protocol --- pooling over the \emph{full}
$\nCols$-setting sweep, which is what an experimenter actually has --- gives a markedly
different law. The comparison is in Table~\ref{tab:session}.

\begin{table}[t]
\caption{Pooled estimation under two session definitions and three sharing patterns, real
data, columns 7--40 scored in every case. ``Full sweep'' pools all $\nCols$ settings,
including the sub-cycle records (columns 1--6) whose field is not identifiable from a single
trace at low budget; ``primary region'' pools only the $34$ settings that are.}
\label{tab:session}
\begin{ruledtabular}
\begin{tabular}{l c c c}
pooled session & $A$ (nT) & $b$ (nT) & $r^{*}$ \\
primary region, all shared & \lawAPool & \lawBPool & $\crossoverReps$ \\
primary region, $T_2^{*}$ per column & \lawTFreeA & \lawTFreeB & \lawTFreeRstar \\
full $\nCols$-setting sweep & \lawFullA & \lawFullB & \lawFullRstar \\
\end{tabular}
\end{ruledtabular}
\end{table}

Pooling the full sweep produces a bias floor of \lawFullB~nT against
\lawBPool~nT for the primary-region session, and advances the crossover from
$\crossoverReps$ to \lawFullRstar~repetitions --- a factor of seven. The mechanism is
visible directly: the sub-cycle records contribute little information about the field but a
great deal of noise to the shared envelope, and a nuisance estimated from them is worse for
every other setting in the sweep. Relaxing the most inhomogeneous shared parameter
($T_2^{*}$, which varies by $\sigma/\mu=\envTstarStd$ over the field range) recovers most
of the difference even in the full-sweep session, but not all of it.

This is the quantitative version of a caution that applies to any session-pooled analysis:
\emph{pool over settings whose parameters you could also estimate one at a time}, or the
pool will be dragged by the records that carry the least information. The synthetic control
of Fig.~\ref{fig:control} reproduces the crossover of the primary-region configuration with
exact ground truth (per-trace $\ctrlLmFiveK$ versus pooled $\ctrlPoolFiveK$~nT at $\rMinK$k,
and per-trace $\ctrlLmSixFortyK$ versus pooled $\ctrlPoolSixFortyK$~nT at $\rMaxK$k), so the
effect is a property of the estimator structure rather than of the measurement pipeline.

"""
s = s[:start] + new_mech + s[end:]

# ---------------- discussion ----------------
rep(r"""The attribution result of Table~\ref{tab:attrib} sharpens all three statements into a
two-step rule.""",
r"""The session-definition result of Table~\ref{tab:session} sharpens all three statements
into a two-step rule.""")

open(p, "w", encoding="utf-8").write(s)
print("edits applied:", n_ok)
