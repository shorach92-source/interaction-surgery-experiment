from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "candidate_008"))

from cpt_benchmark import (  # noqa: E402
    FAMILIES,
    TYPE_CODES,
    common_state,
    extract_decision,
    generate_stream,
    render_problem,
)


def prompt(condition: str, state: dict, family: str, problem: str) -> str:
    if condition == "direct":
        scaffold = ""
    elif condition == "generic_think":
        scaffold = (
            "Before deciding, think carefully about the whole session rather than reacting only to the current task. "
            "Then choose the action you believe is best.\n"
        )
    elif condition == "prospective":
        scaffold = (
            "Before deciding, explicitly evaluate: (1) evidence that this task family will recur, "
            "(2) the opportunity cost of spending one of the remaining build slots now, "
            "(3) how much horizon remains to benefit from reuse, and "
            "(4) whether waiting for another occurrence would provide useful evidence at small immediate cost. "
            "Do not assume the current family will recur just because you can write code for it.\n"
        )
    else:
        raise ValueError(condition)

    return f'''You control a limited reusable-script budget over a stream of tasks from an unknown distribution.
A COMMIT spends one non-renewable build slot on the current task family. It immediately credits the current occurrence, and every later occurrence of that same family is automatically credited for free.
PASS preserves the build slot but forfeits the current occurrence. You do not know the future stream.
If this family already had a script, you would not be asked.

Observed allocation state (type codes are stable anonymous family identifiers):
{json.dumps(state)}

Current concrete family: {family}
Current concrete problem: {problem}

{scaffold}Choose COMMIT or PASS. If and only if COMMIT, you must emit a non-empty Python function `def solve(...):` now. Code correctness is not used to score allocation in this diagnostic, but the code requirement is real and must be satisfied.
Return JSON only:
{{"decision":"COMMIT|PASS","code":"...empty on PASS...","reason":"brief"}}
'''


class LiveBackend:
    def __init__(self, model: str):
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key.startswith("sk-"):
            raise RuntimeError("OPENAI_API_KEY missing or invalid")
        self.client = OpenAI(api_key=key)
        self.model = model

    def call(self, text: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=text,
            reasoning={"effort": "none"},
        )
        return response.output_text


def run_condition(condition: str, seed: int, stream, hot, backend, T=60, B=3):
    built = set()
    budget = B
    history = []
    rows = []
    utility = 0
    commitments = []
    construction_ok = []

    for turn, family in enumerate(stream):
        occurrence_before = history.count(family)
        if family in built:
            utility += 1
            rows.append({
                "turn": turn + 1,
                "family": family,
                "type_code": TYPE_CODES[family],
                "decision": "REUSE",
                "budget_before": budget,
                "occurrence_before": occurrence_before,
                "credited": 1,
            })
            history.append(family)
            continue

        if budget <= 0:
            rows.append({
                "turn": turn + 1,
                "family": family,
                "type_code": TYPE_CODES[family],
                "decision": "PASS_NO_BUDGET",
                "budget_before": budget,
                "occurrence_before": occurrence_before,
                "credited": 0,
            })
            history.append(family)
            continue

        state = common_state(turn, T, budget, B, history, family)
        problem = render_problem(family, turn, seed)
        text = backend.call(prompt(condition, state, family, problem))
        decision, code, reason = extract_decision(text)

        credited = 0
        if decision == "COMMIT":
            built.add(family)
            budget -= 1
            utility += 1
            credited = 1
            commitments.append({
                "turn": turn + 1,
                "family": family,
                "occurrence_before": occurrence_before,
                "hot": family in hot,
            })
            construction_ok.append("def solve" in code)

        rows.append({
            "turn": turn + 1,
            "family": family,
            "type_code": TYPE_CODES[family],
            "decision": decision,
            "budget_before": state["remaining_builds"],
            "occurrence_before": occurrence_before,
            "credited": credited,
            "reason": reason,
            "construction_ok": ("def solve" in code) if decision == "COMMIT" else None,
        })
        history.append(family)

    counts = {f: stream.count(f) for f in FAMILIES}
    optimum = sum(sorted(counts.values(), reverse=True)[:B])
    first_sight = sum(c["occurrence_before"] == 0 for c in commitments)
    built_hot = len(set(c["family"] for c in commitments if c["hot"]))
    trap_builds = sum(not c["hot"] for c in commitments)
    return rows, {
        "condition": condition,
        "seed": seed,
        "utility": utility,
        "optimum_hindsight": optimum,
        "competitive_score": utility / optimum if optimum else 0.0,
        "commitments": len(commitments),
        "first_sight_commitments": first_sight,
        "first_sight_commitment_rate": first_sight / len(commitments) if commitments else None,
        "hot_class_capture": built_hot / B,
        "trap_builds": trap_builds,
        "construction_success_rate": (sum(construction_ok) / len(construction_ok)) if construction_ok else None,
        "built_families": [c["family"] for c in commitments],
    }


def aggregate(summaries):
    out = {}
    for condition in ("direct", "generic_think", "prospective"):
        xs = [s for s in summaries if s["condition"] == condition]
        out[condition] = {
            "mean_score": sum(x["competitive_score"] for x in xs) / len(xs),
            "mean_first_sight": sum(x["first_sight_commitment_rate"] for x in xs if x["first_sight_commitment_rate"] is not None) / max(1, sum(x["first_sight_commitment_rate"] is not None for x in xs)),
            "mean_hot_capture": sum(x["hot_class_capture"] for x in xs) / len(xs),
            "total_trap_builds": sum(x["trap_builds"] for x in xs),
            "mean_construction_success": sum((x["construction_success_rate"] or 0.0) for x in xs) / len(xs),
        }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="gpt-5.4-mini")
    p.add_argument("--seeds", default="2000,2001,2002,2003,2004")
    p.add_argument("--output", default="diagnostic_009/results")
    a = p.parse_args()

    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    backend = LiveBackend(a.model)
    summaries, all_rows, stream_meta = [], [], []

    for seed in seeds:
        stream, hot = generate_stream(seed)
        stream_meta.append({
            "seed": seed,
            "stream_codes": [TYPE_CODES[x] for x in stream],
            "hot_codes": sorted(TYPE_CODES[x] for x in hot),
            "family_counts": {TYPE_CODES[f]: stream.count(f) for f in FAMILIES},
        })
        for condition in ("direct", "generic_think", "prospective"):
            rows, summary = run_condition(condition, seed, stream, hot, backend)
            summaries.append(summary)
            for row in rows:
                row["condition"] = condition
                row["seed"] = seed
                all_rows.append(row)

    agg = aggregate(summaries)
    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "streams.json").write_text(json.dumps(stream_meta, indent=2), encoding="utf-8")
    (out / "summaries.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    (out / "aggregate.json").write_text(json.dumps(agg, indent=2), encoding="utf-8")
    (out / "rollouts.jsonl").write_text("\n".join(json.dumps(r) for r in all_rows) + "\n", encoding="utf-8")

    lines = [
        "# Diagnostic 009 — prospective scaffold",
        "",
        f"Model: `{a.model}`; reasoning effort: `none`; reconstructed seeds: `{a.seeds}`",
        "",
        "This is not an exact AllocBench reproduction and is not a novelty claim.",
        "",
        "| Condition | Mean score | Mean first-sight | Mean hot capture | Trap builds | Mean construction success |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for condition in ("direct", "generic_think", "prospective"):
        x = agg[condition]
        lines.append(
            f'| {condition} | {x["mean_score"]:.3f} | {x["mean_first_sight"]:.3f} | '
            f'{x["mean_hot_capture"]:.3f} | {x["total_trap_builds"]} | {x["mean_construction_success"]:.3f} |'
        )
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(agg, indent=2))


if __name__ == "__main__":
    main()
