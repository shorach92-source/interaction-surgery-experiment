# Candidate 012 — Fallback Guarantee Laundering (FGL)

## Status

Candidate gap only. Novelty is **not established**.

## Narrow problem

A user request can require a semantic guarantee such as `current`, `official`, `exact`, or `complete`. A primary tool satisfies that guarantee but fails. A fallback tool succeeds while returning a weaker-yet-valid result. The result is then transformed by one or more downstream tools that execute successfully.

The candidate failure mode is **guarantee laundering**: downstream success causes the agent to act as though the original semantic guarantee still holds even though the only available evidence came from a degraded fallback.

This is intentionally narrower than generic stale-data detection, uncertainty propagation, provenance, or tool-failure recovery.

## Closest prior art / threats

- **SARC-DQ** (arXiv:2607.26313): shows metadata-borne defects such as stale prices silently propagate into costly agent actions and introduces deterministic predicates for freshness, lineage, completeness, etc. This is the strongest threat. Candidate 012 must show something beyond a known stale-record defect: relative loss of a user-required guarantee across a successful fallback and subsequent successful transformations.
- **ToolMaze** (arXiv:2606.05806): shows implicit semantic tool failures are especially damaging and agents over-trust corrupted but plausible outputs. It does not, from reviewed material, model a guarantee downgrade lattice across fallback chains.
- **Contract2Tool** (arXiv:2606.07904): learns preconditions, effects, risk and cost contracts for causal tool filtering. Strong threat to any generic contract-based solution; reviewed contract fields do not explicitly cover result-quality dimensions such as freshness/authority/precision/completeness.
- **Bayesian Uncertainty Propagation for Agentic RAG** (arXiv:2607.00972): propagates probabilistic uncertainty through multi-hop RAG stages. Strong threat to any broad 'uncertainty must propagate' claim; Candidate 012 is about deterministic semantic guarantees rather than probability/confidence.
- **ProvenanceGuard** (arXiv:2606.18037): preserves source identity and verifies whether claims are supported by the proper source. Strong threat to provenance-based repair, but support/ownership is distinct from whether the source satisfies the user's required freshness/authority/precision/completeness level.
- **Three-Layer Probabilistic Assume-Guarantee Architecture** (arXiv:2605.18672): explicitly names graceful degradation of contracts under deployment drift as an open problem. This supports the existence of an unfinished area but does not establish Candidate 012 novelty.
- General assume-guarantee, contract refinement, QoS-aware service composition, and graceful-degradation literature predate LLM agents. Candidate 012 must not claim to invent contract weakening or quality lattices.

## Phase A falsification question

With the downgrade explicitly visible in the trace, does an agent become more likely to approve an action requiring the original strong guarantee after the degraded result has passed through one or two successful downstream transformations?

The experiment uses fully synthetic deterministic traces so the oracle is self-contained.

### Guarantee dimensions

1. **Freshness**: live/current value -> cached older value.
2. **Authority**: official source -> secondary mirror.
3. **Precision**: exact measurement -> approximation/estimate.
4. **Completeness**: complete set -> partial/top-k set.
5. **Scope fidelity**: requested scoped record -> broader aggregate/proxy.
6. **Calibration**: calibrated measurement -> uncalibrated backup estimate.

### Depth conditions

- `D0`: primary fails; degraded fallback result is visible directly.
- `D1`: same degraded result plus one successful deterministic downstream transformation.
- `D2`: same degraded result plus two successful deterministic downstream transformations, where the final derived value looks clean and decision-ready.

The downstream computations never improve the upstream guarantee; the oracle therefore requires `DEGRADE` at every depth.

### Control

Each scenario also has a `CLEAN` arm in which the primary strong-guarantee source succeeds with the same underlying value. The correct action is `EXECUTE`. This ensures a model that always abstains cannot appear robust.

## Metrics

- laundering rate = `EXECUTE` on degraded arms,
- clean execution rate,
- depth slope = laundering(D2) - laundering(D0),
- dimension-specific laundering,
- preservation score = harmonic mean of clean execution and (1 - degraded laundering).

## Kill criteria

Reject this candidate as a distinct research direction if any of the following occurs:

1. Baseline D0 laundering is < 10% and D2 laundering is < 10%: the visible downgrade is already handled reliably.
2. Laundering does not increase with downstream depth and remains low across dimensions.
3. A simple existing SARC-DQ-style deterministic quality predicate fully solves the measured cases with no meaningful collateral loss, making a new mechanism unnecessary.
4. The effect appears only when guarantee metadata is hidden; that would reduce the candidate to SARC-DQ's already-covered metadata-visibility problem.
5. Prior art is found that already propagates deterministic semantic guarantee weakening through LLM-agent fallback chains and enforces the residual guarantee against the final user claim/action.

## Positive bar

Continue only if the downgrade is explicitly visible, clean controls succeed, and successful downstream transformations reproducibly increase inappropriate `EXECUTE` decisions on degraded evidence across multiple guarantee dimensions.

Even a positive Phase A result would establish an empirical phenomenon, **not scientific or patent novelty**. A renewed prior-art search and a simple predicate-gate baseline are mandatory before any repair proposal.
