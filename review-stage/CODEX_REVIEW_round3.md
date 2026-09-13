**Round-3 referee report**

The authors’ response to item 1 has changed the paper substantially, and in a scientifically useful way. The discovery of the dead-parameter bug, the reconciliation of the two pooled implementations, and the realization that the previous “bias floor” was largely a session-definition/identifiability effect are exactly the kind of checks that should come out of a revision. I would not treat this as a fatal problem. It is potentially the strongest part of the paper, provided the claims are now stated at the correct level of generality and the fitting pipeline is audited against similar optimisation/pathology issues.

My assessment is therefore conditional: the paper is publishable in principle, but not as presently framed.

---

## 1. Is the session-definition result sound, useful, and publishable, or a dataset artefact?

It is a **sound and useful methodological result**, but it must be presented as an estimator/identifiability finding, not as a new physical bias floor.

The mechanism is plausible. In a pooled fit, shared nuisance parameters are estimated from the joint likelihood over all settings. If some settings contain little or no independent information about the field, they can still contribute likelihood volume along weakly constrained directions. Those weak settings can then pull or broaden the shared nuisance estimate, degrading the fitted field parameters for every setting in the pool. In that sense, “pooling over settings you cannot also constrain individually” can indeed poison the shared nuisance. That is a general statistical phenomenon, not specific to this apparatus in principle.

However, the **numerical values** — the change from \(A=416.8\ \mathrm{nT}\), \(b=156.2\ \mathrm{nT}\) for the 40-setting pooled sweep to \(A=456.0\ \mathrm{nT}\), \(b=57.6\ \mathrm{nT}\) for the 34-session pooled sweep, and the corresponding shift of \(r^*\) from \(9.1\times 10^4\) to \(6.2\times 10^5\) — are likely dataset-dependent in magnitude. The paper should not claim that the six excluded settings universally dominate the bias floor in all pooled magnetometry fits. It should say, more carefully, that in this measurement model and data set, inclusion of individually unidentifiable settings produces a large apparent floor, and that the practical rule is to restrict pooling to settings that are individually identifiable under the same model.

For this to be a publishable contribution rather than a post hoc data-selection artefact, the authors must do three things:

1. **Define “individually identifiable” quantitatively.**  
   It cannot be merely “the six records we removed.” They should give an objective criterion: for example, a per-setting Fisher-information threshold, finite single-setting confidence interval/profile likelihood for the field parameter, a Cramér–Rao bound relative to the measurement budget, or an equivalent diagnostic computed before the pooled comparison.

2. **Show robustness to the boundary between identifiable and unidentifiable settings.**  
   If the conclusion depends sharply on excluding exactly six settings, that is worrying. They should show, for example, that the result is stable under reasonable threshold variations, or demonstrate the effect by adding the weak settings back one at a time and showing the degradation continuously.

3. **Demonstrate the effect in a synthetic control with known truth.**  
   The existing synthetic control reproducing the crossover is helpful, but it is not sufficient if it only uses well-identified settings. They should include a synthetic version of the 40-setting sweep in which some settings are deliberately made weakly identifiable, with known ground-truth field and nuisance parameters. The pooled fit over all settings should then reproduce the spurious floor or biased nuisance, while pooling over the identifiable subset should recover the correct parameters. That would show that the effect is not merely an accident of this particular sample.

With those qualifications, the result is not only publishable; it is probably the most valuable contribution of the revised manuscript.

---

## 2. Does the discovery-and-fix process raise or lower confidence? What is needed to rule out similar optimisation artefacts?

My reaction is mixed.

It **raises confidence in the authors’ scientific integrity and in the revision process**. They used the requested check to uncover a real bug, fixed it, reconciled two implementations, deleted a subsection whose numbers came from a stalled optimizer, and rewrote the interpretation honestly. That is good science.

But it **lowers confidence in the previous pipeline**, because a model with 33 dead parameters was able to produce numbers that entered Table I and survived until this stage. That means the previous fitting workflow did not have sufficient automatic guards against underdetermined or degenerate parameterisations. The fact that the bug was in the ablation fitter does not automatically guarantee that other fits were immune, especially if the same parameter-allocation logic or optimizer infrastructure was reused elsewhere.

Therefore, before acceptance, I would require a documented **optimizer and identifiability audit** for all fits that enter the paper. A single sentence saying “we added a convergence check” is not enough.

At minimum, the authors should provide, preferably in an appendix or supplement:

1. **Active-parameter accounting.**  
   For every fit, report the number of allocated parameters, the number of active/free parameters, and whether any parameter had zero or near-zero gradient contribution. The 33-dead-parameter failure mode should be impossible in the revised code, and the paper should say how that is enforced.

2. **Convergence diagnostics.**  
   Report optimizer return status, maximum gradient norm, parameter-step tolerance, and objective-function tolerance for each reported fit. If fits are discarded for non-convergence, state how many and why.

3. **Multi-start stability.**  
   For the main pooled and per-trace fits, rerun the optimizer from multiple reasonable initialisations and show that the reported optimum is stable. If the objective is multimodal, this must be acknowledged.

4. **Independent optimizer cross-check.**  
   Re-fit the main Table II models with a different optimizer or algorithm and confirm that \(A\), \(b\), and \(r^*\) agree within numerical tolerance. Agreement between two implementations of the same algorithm is helpful, but agreement across optimizers is stronger.

5. **Local curvature / identifiability check.**  
   Report Hessian eigenvalue spectra, condition numbers, or profile-likelihood intervals for the shared nuisance parameters. The point is to show that the fitted 34-session model does not contain hidden flat directions analogous to the dead-parameter bug.

6. **Synthetic recovery through the same pipeline.**  
   Generate synthetic data using the fitted 34-session model, plus realistic noise, and pass it through the exact same fitting pipeline. The pipeline should recover the known parameters and \(r^*\) without bias. This is the strongest practical guard against a residual optimisation artefact.

If these checks are added and passed, I would consider the remaining numerical results credible. If they cannot be provided, my recommendation would move toward Major Revision.

---

## 3. Does the crossover at the top of the measured ladder destroy the headline?

It destroys one possible headline, but not the paper.

If the headline is “the pooled estimator gives a large practical sensitivity advantage,” then no: \(r^* = 6.2\times 10^5\) sitting just below the highest measured budget \(6.4\times 10^5\) is too weak to support a broad claim of practical superiority. The advantage is at the very edge of the measured range, and if the bootstrap confidence interval on \(r^*\) is wide, even that edge may not be statistically secure.

But the paper no longer needs that headline.

The defensible headline is now:

> Pooling over field settings that are not individually identifiable can create a large apparent bias floor and qualitatively change the inferred scaling law. The safe practical rule is to pool only over settings that can also be constrained individually.

That is still a meaningful result, especially because the session-definition change moves the inferred crossover from \(9.1\times 10^4\) to \(6.2\times 10^5\), nearly a factor of seven. The important physical/methodological point is not that the pooled 34-session model is dramatically superior over the full measured range; the point is that the apparent law is highly sensitive to which settings are included in the pooled session.

The manuscript must therefore be carefully calibrated:

- It should state explicitly that the 34-session pooled crossover lies at the top of the measured budget ladder.
- It should quote the bootstrap confidence interval for \(r^*\) relative to the maximum measured budget.
- If the confidence interval extends beyond \(6.4\times 10^5\), the paper should not claim that the crossover has been directly observed. It should say that the data are consistent with a crossover at or beyond the upper end of the measured range.
- It should avoid extrapolating the pooled model to budgets much higher than the largest measured budget.
- It should not frame the result as a general demonstration that pooled fitting is better. The correct framing is that pooled fitting is safe only under an identifiability constraint.

With that reframing, the effect is not too weak to publish. It becomes a cautionary methodological result with a concrete practical rule. If the authors insist on the old “large crossover advantage” framing, then the effect is now too weak.

---

## 4. Final recommendation

**Recommendation: Minor Revision**, conditional on the two items below.

I would be prepared to recommend publication after these revisions, provided the new checks do not uncover another optimisation pathology. If the authors cannot supply the audit or the session-definition robustness tests without substantial new work, then the appropriate decision would become Major Revision rather than Minor.

### Top remaining item 1 — mandatory optimizer/identifiability audit

Add a concise but explicit audit of the fitting procedure for all reported laws. This should include active-parameter counts, convergence criteria, multi-start stability, Hessian or profile-likelihood identifiability diagnostics, independent-optimizer cross-check, and synthetic recovery through the final pipeline. The paper must show that the dead-parameter failure mode responsible for the previous stalled ablation fitter cannot affect the reported Table II fits.

### Top remaining item 2 — validate and calibrate the session-definition claim

Define “individually identifiable” by an objective criterion and show that the 34-versus-40 result is not an artefact of an ad hoc exclusion. Include a sensitivity analysis — for example, threshold variation, leave-one-out or add-back of the six weak settings, and a synthetic control with deliberately unidentifiable settings. Rewrite the abstract and conclusions so that the headline is the identifiability-aware pooling rule, not a broad claim of pooled-estimator superiority, and state clearly that the crossover lies at the top of the measured budget range.