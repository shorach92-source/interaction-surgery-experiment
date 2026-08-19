# Candidate 014 — Active Inventory Identifiability Control

## Decision

**Rejected on prior art before benchmark.**

The candidate explored whether a restaurant/retail system with both inaccurate inventory records and censored lost-sales demand needs a special mechanism that jointly chooses diagnostic inventory audits/recounts and replenishment actions in order to disambiguate hidden stock from hidden demand.

## Why it was rejected

The motivating feedback loop is real, but the core technical structure is already substantially covered by prior operations-research work:

- *Information-Sensitive Replenishment when Inventory Records Are Inaccurate* models imperfect inventory records, unobserved lost sales, a Bayesian belief over physical inventory, and forward-looking replenishment.
- Prior work also studies joint audit and replenishment decisions for inventory systems with unrecorded demands.
- Separate recent work covers censored-demand learning, lost-sales inventory control, non-stationarity and lead times.

A small synthetic sanity check also did not provide a reason to invent a special active-identification mechanism: under one pre-tuning four-state setup, a passive Bayesian belief baseline had lower combined estimation-error-plus-action-cost than simple audit or exploratory-order probes. We deliberately did not tune the simulator after observing that result.

## Research-process conclusion

Do not pursue this as a technological novelty claim. It can still inform a practical restaurant inventory product, but the underlying belief/audit/replenishment problem has strong classical prior art.

Future operations candidates must distinguish themselves from Bayesian inventory-state estimation, information-sensitive replenishment, censored-demand control, cycle-count optimization, and standard POMDP/active-sensing formulations before receiving a benchmark.
