# Diagnostic 009 — Multi-seed result

## Decision

**Negative. Do not promote the prospective scaffold to a research mechanism.**

A five-stream reconstructed diagnostic on `gpt-5.4-mini` with `reasoning.effort=none` compared direct R2-like construction, a generic think-carefully instruction, and an explicit prospective recurrence/opportunity-cost checklist.

## Aggregate results

| Condition | Mean competitive score | Mean first-sight commitment | Mean hot capture | Total trap builds | Mean construction success |
|---|---:|---:|---:|---:|---:|
| direct | 0.503 | 1.000 | 0.467 | 8 | 1.000 |
| generic_think | 0.503 | 1.000 | 0.467 | 8 | 1.000 |
| prospective | 0.376 | 0.167 | 0.533 | 5 | 0.933 |

## Per-stream score

| Seed | Direct | Generic think | Prospective |
|---:|---:|---:|---:|
| 2000 | 0.420 | 0.420 | 0.820 |
| 2001 | 0.686 | 0.686 | 0.333 |
| 2002 | 0.731 | 0.731 | 0.288 |
| 2003 | 0.460 | 0.460 | 0.300 |
| 2004 | 0.216 | 0.216 | 0.137 |

The striking improvement on seed 2000 did not generalize. It was a one-stream false lead.

## Behavioral interpretation

The prospective checklist changed *when* the model committed but did not reliably improve *what* it committed to:

- It reduced first-sight commitment from 100% to 16.7% on average.
- It improved hot-class capture only slightly (0.467 -> 0.533).
- On seed 2001 it committed only twice, leaving scarce build capacity unused while realizing only 17/51 utility.
- On seeds 2002–2004 it delayed commitment but still allocated some slots to trap families.
- Generic `think carefully` produced the same allocation outcomes as direct on all five reconstructed streams.

Thus, reducing the process-level symptom of first-sight eagerness is not sufficient to recover end-to-end online allocation capability. A prompt can make the agent more selective while making its realized allocation score worse.

## Methodological conclusion

This result reinforces the benchmark designers' decision to pair first-sight commitment with an outcome score. It does not establish a novel mechanism.

The reconstructed streams are not the authors' canonical artifacts, so this is not an exact AllocBench replication. Nevertheless, it is sufficient to reject the current prompt-scaffold direction because the proposed intervention fails even on our own predeclared five-stream diagnostic.

## Next step

Do not tune this prompt on these streams. Move to a different research gap rather than optimizing against observed failures.
