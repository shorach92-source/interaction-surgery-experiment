# Candidate 013 — Event-Censoring Transfer Gap (ECTG)

## Status

Candidate phenomenon only. Novelty is **not established**.

## Motivation

Retail demand forecasting has two well-developed but usually separate concerns:

1. exogenous events/promotions can cause short-lived uplift;
2. stockouts censor observed sales below latent demand.

The narrow question is whether a **rare event whose local examples are all stockout-censored** creates an additional event-specific learning failure that requires a mechanism beyond ordinary censor-aware pooling across stores/series.

This candidate deliberately starts with a strong kill baseline. If a generic pooled censored-likelihood estimator recovers the event uplift, there is no reason to invent a separate event-censoring transfer method.

## Closest prior art / threats

- FreshRetailNet-50K provides stockout annotations plus promotion, holiday/activity, weather and product/store hierarchy covariates and demonstrates latent-demand recovery before forecasting.
- Exact censored-newsvendor theory shows passive sales fundamentally limit what can be learned, while targeted exploration can recover guarantees.
- Tobit/Kalman and censored-likelihood demand models explicitly estimate latent demand under lost sales.
- Structural retail-demand models estimate primary demand and stockout substitution, including hierarchical consumer-choice structures.
- A EURO 2025 abstract, `A Hierarchical Approach to Forecasting Censored Demand in Lost-Sales Systems`, combines censored demand forecasting with temporal hierarchies.

Therefore Candidate 013 must **not** claim that event covariates, censor-aware demand recovery, hierarchy/pooling, or substitution modeling are new.

## Phase A kill question

Suppose one target store has only censored observations of a rare event, but peer stores have the same event type under varying inventory caps. Can an ordinary pooled Poisson censored-likelihood estimator recover the shared event multiplier well enough to predict the target store's latent event demand?

The synthetic oracle is fully known.

### Data-generating process

- multiple stores with heterogeneous baseline Poisson demand;
- a shared event multiplier `m_true`;
- ordinary non-event days estimate each store's baseline;
- target-store event days are all inventory-censored;
- peer-store event days include a mixture of censored and uncensored observations;
- observed sales are `min(latent_demand, inventory_cap)` and the censor flag is known.

### Baselines

1. `naive_local_sales`: target event observed-sales mean / target baseline mean.
2. `local_censored_mle`: censored Poisson likelihood using only the target's event observations.
3. `pooled_censored_mle`: same likelihood pooled across all stores, with each store's non-event baseline rate treated separately and one shared event multiplier.
4. Oracle multiplier (reporting only).

## Kill criterion

Close this candidate if pooled censored MLE recovers the shared event multiplier with <=10% relative error and predicts target latent event mean with <=10% relative error across the predeclared simulation seeds.

That outcome means the apparent 'event-censoring transfer gap' is already handled by ordinary pooling + censor-aware likelihood under the shared-effect assumptions.

## Continue criterion

Only continue if the pooled censor-aware estimator fails materially **despite its model assumptions matching the data-generating process**. If it fails only after introducing store-specific hidden heterogeneity, substitution, unknown stockout timing, or semantic event similarity, those are separate problems and require renewed prior-art checks rather than post-hoc expansion of this candidate.
