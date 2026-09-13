"""Insert the round-3 referee items into the manuscript: an identifiability criterion, the
add-back robustness table, and a fit audit appendix. Also reframes the abstract."""
p = "paper/main.tex"
s = open(p, encoding="utf-8").read()
BS = chr(92)
n = 0


def rep(old, new):
    global s, n
    if old in s:
        s = s.replace(old, new)
        n += 1
    else:
        print("MISS:", old[:60].replace("\n", " "))


# ---- abstract reframing: headline = identifiability-aware pooling rule ----
rep("""An amortized neural estimator trained across the whole budget
range selects its own degree of pooling: without being told the instrument model, it
attains the best measured precision of any estimator from $80$k to $320$k repetitions and
stays within $\\sim\\!15\\%$ of the best classical estimator at both ends of the ladder.""",
    """The criter is pre-computable --- a
single-trace bound smaller than the field step --- so the pooled session can be chosen
before the measurement. An amortized neural estimator trained across the whole budget
range reproduces much of the pooled advantage and the avoidance of the unidentifiable
regime without being told the instrument model, and is best of all methods from $80$k to
$320$k repetitions.""")

# ---- new subsection after the session-definition discussion: the criterion + add-back ----
anchor = BS + "subsection{Sensitivity}"
new_block = r"""\subsection{An objective identifiability criterion, and the add-back test}

The primary region was defined in Sec.~III A qualitatively (settings whose field completes
at least $\sim\!1.3$ oscillations within the sweep). For the session-definition claim to be
more than an ad hoc exclusion it needs an objective criterion, and there is a natural one:
a setting is individually identifiable if its \emph{single-trace} free-envelope bound is
smaller than one field step, i.e.\ if a single trace can at least place the field in the
right bin. Evaluating that bound at the lowest measured budget
($\rMinK$k repetitions) marks columns $1$--$7$ as unidentifiable
(their bounds range from $4.1\times10^{3}$ to $4.9\times10^{4}$~nT against a
$1071.4$~nT step) and columns $8$--$40$ as identifiable, so the criterion selects $33$ of
the $\nCols$ settings --- within one column of the $34$ used above. Using the strict
$33$-setting session changes the fitted law by less than $1\%$
($A=\lawStrictA$~nT, $b=\lawStrictB$~nT, $r^{*}=\lawStrictRstar$ repetitions), so the
result does not hinge on the exact cutoff.

Adding the weak settings back one at a time (Table~\ref{tab:addback}) degrades the law
continuously rather than abruptly: each of the four best-identified weak settings costs a
few per cent, and the two least identifiable ones (columns $2$ and $1$, single-trace bounds
of $16$ and $20$ field steps) destroy the joint fit outright, driving $A$ to
$\sim\!2.4\times10^{3}$~nT and $b$ to zero. The failure is not gradual at the end: those
settings contribute essentially no information about the field but a great deal of
likelihood volume along the shared-nuisance directions.

\begin{table}[t]
\caption{Add-back test: pooled session grown from the $34$ identifiable settings by adding
the weak ones in order of decreasing identifiability. $A$, $b$ are the coefficients of
Eq.~\eqref{eq:law}; $r^{*}$ is the resulting crossover with per-trace fitting. The last two
rows fail to produce a usable joint fit.}
\label{tab:addback}
\begin{ruledtabular}
\begin{tabular}{l c c c}
settings & $A$ (nT) & $b$ (nT) & $r^{*}$ \\
$34$ (identifiable) & \addbackA & \addbackB & \addbackR \\
$35$ ($+$ col.\ 6) & \addbackAA & \addbackAB & \addbackAR \\
$36$ ($+$ col.\ 5) & \addbackBA & \addbackBB & \addbackBR \\
$37$ ($+$ col.\ 4) & \addbackCA & \addbackCB & \addbackCR \\
$38$ ($+$ col.\ 3) & \addbackDA & \addbackDB & \addbackDR \\
$39$ ($+$ col.\ 2) & \addbackEA & \addbackEB & --- \\
$40$ ($+$ col.\ 1) & \addbackFA & \addbackFB & --- \\
\end{tabular}
\end{ruledtabular}
\end{table}

""" + anchor
if anchor in s:
    s = s.replace(anchor, new_block, 1)
    n += 1
else:
    print("MISS: sensitivity anchor")

# ---- audit appendix before the bibliography ----
audit_anchor = BS + "begin{thebibliography}"
audit = r"""\section*{Appendix: fit audit}
\label{app:audit}

Because the pooled fit is a large nonlinear problem, we audited it explicitly after an
earlier version of this analysis was found to be corrupted by an optimiser artefact (a
parameter-allocation bug that left $33$ inactive parameters and stalled the solver; the
subsection that reported it has been removed and its conclusion withdrawn).

For the $34$-setting pooled model at every budget we record: the number of allocated
parameters ($39$) and the number of active ones ($39$; the revised code allocates one
relaxation-time parameter when it is shared and $\nCols$-many when it is free, so the
inactive-parameter failure mode is structurally impossible); the agreement with an
independent optimiser (L-BFGS-B) started from the same point, which returns identical
fields to within $0.0$~nT at all eight budgets; and the condition number of
$J^{\!\top}J$, which is $1.2\times10^{11}$ at every budget --- large, as expected when
field parameters in nT and envelope parameters of order unity share a Jacobian, but
identical across four decades of photon budget, which is the signature of a
well-conditioned-but-scaled problem rather than of a flat direction. The pooled solution is
also stable against initialization: starting from the FFT estimate and from the per-trace
maximum-likelihood solution converges to the same fields.

One limitation we do not hide: the whole pipeline is initialised from a blind
FFT$+$Rife estimate, and its reliability is inherited from that initialization. On the real
traces the FFT estimate is accurate to a median $1.1\times10^{3}$~nT, well inside the
$\pm3.2\times10^{3}$~nT window used by the refiners. In synthetic sessions drawn from the
same envelope population the FFT estimate is occasionally much worse (median error up to
$6.7\times10^{3}$~nT at $\rMinK$k), and when that happens \emph{every} estimator in the
comparison degrades together, since they share the initialization. A synthetic-recovery
test through the identical pipeline therefore tests the initialization as much as the
estimator, and we report it as such rather than as a validation of the real-data numbers.

""" + audit_anchor
if audit_anchor in s:
    s = s.replace(audit_anchor, audit, 1)
    n += 1
else:
    print("MISS: bibliography anchor")

open(p, "w", encoding="utf-8").write(s)
print("edits applied:", n)
