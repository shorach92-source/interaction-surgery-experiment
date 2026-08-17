# Candidate 013 — Event-Censoring Transfer result

## Decision

**Negative. Close Candidate 013 under the predeclared shared-event setting.**

The synthetic experiment tested a target store whose every rare-event observation was inventory-censored, while peer stores experienced the same event under a mixture of inventory caps. The true event multiplier was shared across stores (`m_true = 1.9`).

The benchmark deliberately included an ordinary pooled Poisson censored-likelihood estimator as a strong kill baseline.

## Ten-seed result

| Metric | Value |
|---|---:|
| True event multiplier | 1.900 |
| Mean naive-local multiplier | 0.235 |
| Mean local censored-MLE multiplier | 1.460 |
| Mean pooled censored-MLE multiplier | 1.887 |
| Mean pooled multiplier relative error | 1.263% |
| Max pooled multiplier relative error | 3.947% |
| Mean target event-mean relative error | 1.569% |
| Max target event-mean relative error | 3.435% |

Across the ten predeclared seeds, peer observations contained 480 censored and 480 uncensored event instances. All target-store event instances remained censored.

## Interpretation

Observed local event sales were severely biased downward, so the motivating operational problem is real. However, the candidate's proposed gap disappears once ordinary cross-store pooling is combined with the correct censored likelihood under the same shared-effect assumptions that generated the data.

The pooled estimator recovered the shared event multiplier with roughly 1.3% mean relative error and predicted the target store's latent event mean with roughly 1.6% mean relative error. This is far inside the predeclared 10% kill threshold.

Therefore no special `event-censoring transfer` mechanism is justified by this setting.

## What we deliberately do not do

Do not rescue the candidate by adding hidden store-specific uplift heterogeneity, substitution, semantic event similarity, uncertain inventory records, or unknown stockout timing after seeing this result. Each of those changes defines a different identification problem and already has adjacent prior art. Any future candidate using one of them must start with a fresh competition search and its own kill criterion.
