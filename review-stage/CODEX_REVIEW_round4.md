**Round-4 referee report**

**1. Discharge of round-3 conditions**

Yes. Both round-3 conditions have now been discharged.

For **Item 1**, the active-parameter accounting removes the earlier structural failure mode: the pooled model now has 39 active parameters at every budget, with relaxation-time slots allocated correctly depending on whether the parameter is shared or column-free. The independent L-BFGS-B cross-check returning fields identical to the TRF solution to 0.0 nT at all eight budgets is a strong practical test that the solution is not optimizer-specific. Convergence from both FFT-based and per-trace MLE initialisations further supports basin stability. The authors’ explicit statement that the synthetic-recovery test is partly a test of the initialisation, not a validation of the real-data numbers, is the correct level of caution.

For **Item 2**, the session-definition issue is now resolved in substance. The “individually identifiable” criterion is objective: single-trace free-envelope CRLB below one field step at the lowest measured budget. The resulting 33-setting session gives a law within 1% of the earlier 34-setting result, which is more than adequate. The add-back test is particularly persuasive: degradation is continuous as weak but informative settings are included, and collapse occurs only when essentially uninformative settings are forced into the pool. The reframing of the abstract and conclusions is appropriate and removes the earlier overclaim of general pooled-estimator superiority.

**2. Remaining risk**

I do not regard the remaining risks as blocking, but they should be acknowledged.

First, the pipeline remains conditional on successful blind FFT/Rife initialisation. The reported median real-data initialisation error is inside the refinement window, but the synthetic tails show that when the initial estimate is far outside the window, all estimators degrade together. Therefore the reported law is reliable only within the regime where the initialiser succeeds. This is now stated, but it must remain visible in the main text, not only in an appendix.

Second, the reported condition number, \(\kappa(J^T J) \sim 10^{11}\), is still large enough that I would not simply assert it is a units artifact without qualification. The stability across optimisers, initialisations, budgets, and session definitions mitigates the concern, and the add-back test argues against a hidden flat direction controlling the final law. Still, a scaled or dimensionless conditioning diagnostic would make the argument cleaner. I am not making this a blocker at this stage because the empirical stability checks are sufficient for the claims now being made.

**3. Final recommendation and final item**

**Recommendation: accept.** There is no longer a scientific blocker to publication. The authors have addressed the identifiability and session-definition concerns in a quantitatively defensible way.

The one remaining item I would require is a **prominent caveat in the abstract or main conclusion**, not buried only in the appendix, stating that the reported scaling law is conditional on the identifiability-aware pooling rule and on successful FFT/Rife initialisation within the stated refinement window. The sentence should make clear that the synthetic recovery tests validate the estimator/initialisation pipeline under the assumed model, but do not by themselves certify the absolute real-data field values.

With that wording in place, the paper is acceptable.