# Rejected pre-benchmark direction — transactional-flow + visual inventory sensor fusion

## Decision

**Reject as a technological-discovery candidate. Keep only as a possible product direction.**

## Motivation

Real restaurant inventory systems can suffer from noisy or incorrect physical counts, including visual confusion between similar SKUs. A candidate idea was to use transactional consumption flow (POS + recipes + deliveries + waste/transfers) as a second sensor to correct visual SKU counts/identity.

## Competition / prior art

The broad ingredients are already established:

- inventory-record inaccuracy and Bayesian belief over physical inventory have long-standing operations-research prior art;
- sensor fusion for inventory/perception already combines multiple noisy measurement channels;
- restaurant platforms already reconcile POS, recipes, deliveries, transfers, waste and physical stock.

No reviewed public source clearly described the exact product configuration of SKU-level Bayesian disambiguation where transactional consumption serves as a second sensor for visually similar restaurant SKUs, so this may remain a narrow product gap. That is not enough to support a research-novelty claim.

## Synthetic kill test

A simple two-SKU synthetic model used:

- visually similar SKUs;
- noisy/confused visual counts;
- an independent transactional-flow estimate;
- ordinary linear Bayesian/Kalman fusion.

Representative regime over 2,000 random seeds:

- vision-only mean MAE: ~2.053
- flow-only mean MAE: ~1.743
- fused mean MAE: ~1.353

This is ~22.4% better than the stronger single sensor in that representative regime.

Across a broader 36-regime sweep, median improvement over the better single sensor was ~9.25%, with a maximum around 28.7%; fusion could be worse when noise assumptions were unfavorable/misspecified.

## Interpretation

The motivating problem is real, but most of the benefit is already explained by ordinary state estimation / sensor fusion. The current formulation therefore does not justify a new AI mechanism.

Do not promote this to Candidate 014 unless a future, separately researched mechanism introduces a genuinely new identification or decision problem that ordinary Bayesian/state-space methods do not already solve.
