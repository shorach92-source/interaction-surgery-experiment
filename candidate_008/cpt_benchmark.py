from __future__ import annotations

import argparse
import json
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path


FAMILIES = [
    "linear_congruential_step",
    "modular_exponentiation",
    "continued_fraction_step",
    "chinese_remainder_pair",
    "josephus_survivor",
    "quadratic_modular_map",
    "xorshift_step",
    "modular_matrix_step",
]

TYPE_CODES = {name: chr(ord("A") + i) for i, name in enumerate(FAMILIES)}


def weighted_choice(rng: random.Random, items, weights):
    x = rng.random() * sum(weights)
    acc = 0.0
    for item, weight in zip(items, weights):
        acc += weight
        if x <= acc:
            return item
    return items[-1]


def generate_stream(seed: int, T: int = 60, B: int = 3):
    rng = random.Random(seed)
    hot = set(rng.sample(FAMILIES, 3))
    weights = [0.85 / 3 if f in hot else 0.15 / 5 for f in FAMILIES]
    for _ in range(10000):
        stream = [weighted_choice(rng, FAMILIES, weights) for _ in range(T)]
        if any(f not in hot for f in stream[:B]):
            return stream, hot
    raise RuntimeError("could not generate early-trap stream")


def render_problem(family: str, turn: int, seed: int) -> str:
    rng = random.Random(seed * 1000 + turn * 17 + FAMILIES.index(family))
    a, b, c = rng.randint(3, 97), rng.randint(5, 131), rng.randint(7, 173)
    if family == "linear_congruential_step":
        return f"Given x={a}, compute one LCG step x'=(17*x+{b}) mod {c}."
    if family == "modular_exponentiation":
        return f"Compute {a}^{rng.randint(3, 11)} mod {c}."
    if family == "continued_fraction_step":
        return f"For rational {a}/{b}, return the first Euclidean quotient and remainder."
    if family == "chinese_remainder_pair":
        m1, m2 = 11, 13
        return f"Find the least nonnegative x with x mod {m1}={a % m1} and x mod {m2}={b % m2}."
    if family == "josephus_survivor":
        return f"Find the Josephus survivor for n={10 + a % 30}, k={2 + b % 7}, zero-indexed."
    if family == "quadratic_modular_map":
        return f"Compute one step x'=(x*x+{b}) mod {c} from x={a}."
    if family == "xorshift_step":
        return f"Apply x ^= x<<3; x ^= x>>5; x ^= x<<2 to x={a}, masking to 16 bits after each step."
    if family == "modular_matrix_step":
        return f"Multiply [[1,{a % 9}],[{b % 9},1]] by vector [{a % 17},{b % 17}] modulo {c}."
    raise KeyError(family)


def extract_decision(text: str):
    text = text.strip()
    try:
        obj = json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        obj = None
        if start >= 0 and end > start:
            try:
                obj = json.loads(text[start:end + 1])
            except Exception:
                obj = None
        if obj is None:
            m = re.search(r'\"decision\"\s*:\s*\"(COMMIT|PASS|KEEP)\"', text, re.I)
            decision = m.group(1).upper() if m else "PASS"
            if decision == "KEEP":
                decision = "COMMIT"
            return decision, "", text[:400]
    decision = str(obj.get("decision", "PASS")).upper().strip()
    if decision == "KEEP":
        decision = "COMMIT"
    if decision not in {"COMMIT", "PASS"}:
        decision = "PASS"
    code = str(obj.get("code", ""))
    reason = str(obj.get("reason", ""))
    return decision, code, reason


def common_state(turn, T, budget, B, history_names, current_family):
    compact_history = [TYPE_CODES[x] for x in history_names]
    return {
        "turn": turn + 1,
        "horizon": T,
        "remaining_builds": budget,
        "total_build_budget": B,
        "observed_type_history": compact_history,
        "current_type_code": TYPE_CODES[current_family],
    }


def constructive_prompt(condition, state, family, problem):
    planning = ""
    if condition == "plan_first":
        planning = (
            "Before choosing, explicitly reason about recurrence evidence, opportunity cost, remaining horizon, "
            "and whether saving the limited build budget could be more valuable. Do not assume the current family will recur.\n"
        )
    return f'''You control a limited reusable-script budget over a stream of tasks from an unknown distribution.
A COMMIT spends one non-renewable build slot on the current task family. It immediately credits the current occurrence, and every later occurrence of that same family is automatically credited for free.
PASS preserves the build slot but forfeits the current occurrence. You do not know the future stream.
If this family already had a script, you would not be asked.

Observed allocation state (type codes are stable anonymous family identifiers):
{json.dumps(state)}

Current concrete family: {family}
Current concrete problem: {problem}

{planning}Choose COMMIT or PASS. If and only if COMMIT, you must emit a non-empty Python function `def solve(...):` now. Code correctness is not used to score allocation in this pilot, but the code requirement is real and must be satisfied.
Return JSON only:
{{"decision":"COMMIT|PASS","code":"...empty on PASS...","reason":"brief"}}
'''


def cpt_policy_prompt(state):
    return f'''You are making only an online allocation decision. No coding or task execution is available in this frame.
You have a stream of item types from an unknown distribution and a limited number of permanent KEEP slots.
KEEP spends one non-renewable slot on the current type, immediately credits the current occurrence, and automatically credits every later occurrence of that same type.
PASS preserves the slot but forfeits the current occurrence. You do not know future items.

Frame-neutral state:
{json.dumps(state)}

Choose KEEP or PASS. The decision will be binding and cannot be revised after the concrete task is revealed.
Return JSON only:
{{"decision":"KEEP|PASS","reason":"brief"}}
'''


def cpt_executor_prompt(family, problem):
    return f'''A prior allocator has already made the binding decision COMMIT. You may not revise it.
Construct the reusable Python tool for the current family.
Family: {family}
Problem instance: {problem}
Return JSON only:
{{"decision":"COMMIT","code":"def solve(...): ...","reason":"execution only; allocation already frozen"}}
'''


class LiveBackend:
    def __init__(self, model: str):
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key.startswith("sk-"):
            raise RuntimeError("OPENAI_API_KEY missing or invalid")
        self.client = OpenAI(api_key=key)
        self.model = model

    def call(self, prompt: str):
        r = self.client.responses.create(model=self.model, input=prompt)
        return r.output_text


class MockBackend:
    def call_for(self, condition: str, state: dict):
        seen = state["observed_type_history"].count(state["current_type_code"])
        if condition == "direct":
            decision = "COMMIT"  # planted eager constructive failure
        else:
            decision = "COMMIT" if seen >= 1 else "PASS"
        if decision == "COMMIT":
            return json.dumps({"decision": decision, "code": "def solve(x): return x", "reason": "mock"})
        return json.dumps({"decision": "PASS", "code": "", "reason": "mock"})


def run_condition(condition, seed, stream, hot, backend, model, T=60, B=3):
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
                "auto_reuse": True,
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
                "auto_reuse": False,
                "decision": "PASS_NO_BUDGET",
                "budget_before": budget,
                "occurrence_before": occurrence_before,
                "credited": 0,
            })
            history.append(family)
            continue

        state = common_state(turn, T, budget, B, history, family)
        problem = render_problem(family, turn, seed)

        if isinstance(backend, MockBackend):
            text = backend.call_for(condition, state)
            decision, code, reason = extract_decision(text)
            policy_reason = reason
            executor_reason = ""
        elif condition in {"direct", "plan_first"}:
            text = backend.call(constructive_prompt(condition, state, family, problem))
            decision, code, reason = extract_decision(text)
            policy_reason = reason
            executor_reason = ""
        elif condition == "cpt":
            policy_text = backend.call(cpt_policy_prompt(state))
            decision, _, policy_reason = extract_decision(policy_text)
            code = ""
            executor_reason = ""
            if decision == "COMMIT":
                exec_text = backend.call(cpt_executor_prompt(family, problem))
                _, code, executor_reason = extract_decision(exec_text)
        else:
            raise ValueError(condition)

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
            "auto_reuse": False,
            "decision": decision,
            "budget_before": state["remaining_builds"],
            "occurrence_before": occurrence_before,
            "credited": credited,
            "policy_reason": policy_reason,
            "executor_reason": executor_reason,
            "construction_ok": ("def solve" in code) if decision == "COMMIT" else None,
        })
        history.append(family)

    counts = {f: stream.count(f) for f in FAMILIES}
    optimum = sum(sorted(counts.values(), reverse=True)[:B])
    first_sight = sum(c["occurrence_before"] == 0 for c in commitments)
    built_hot = len(set(c["family"] for c in commitments if c["hot"]))
    trap_builds = sum(not c["hot"] for c in commitments)
    summary = {
        "condition": condition,
        "seed": seed,
        "model": model,
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
    return rows, summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backend", choices=["mock", "live"], default="mock")
    p.add_argument("--model", default="gpt-5.4-mini")
    p.add_argument("--seeds", default="2000")
    p.add_argument("--output", default="candidate_008/results")
    a = p.parse_args()

    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    backend = LiveBackend(a.model) if a.backend == "live" else MockBackend()
    all_rows, summaries, streams = [], [], []

    for seed in seeds:
        stream, hot = generate_stream(seed)
        streams.append({
            "seed": seed,
            "stream_codes": [TYPE_CODES[x] for x in stream],
            "hot_codes": sorted(TYPE_CODES[x] for x in hot),
            "family_counts": {TYPE_CODES[f]: stream.count(f) for f in FAMILIES},
        })
        for condition in ("direct", "plan_first", "cpt"):
            rows, summary = run_condition(condition, seed, stream, hot, backend, a.model)
            summaries.append(summary)
            for row in rows:
                row["condition"] = condition
                row["seed"] = seed
                all_rows.append(row)

    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "streams.json").write_text(json.dumps(streams, indent=2), encoding="utf-8")
    (out / "summaries.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    (out / "rollouts.jsonl").write_text("\n".join(json.dumps(r) for r in all_rows) + "\n", encoding="utf-8")

    lines = [
        "# Candidate 008 CPT pilot",
        "",
        f"Backend: `{a.backend}`; model: `{a.model}`; seeds: `{a.seeds}`",
        "",
        "This is a screening pilot, not an AlloBench reproduction and not evidence of novelty.",
        "",
        "| Condition | Seed | Score | First-sight commit | Hot capture | Trap builds | Construction success |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for s in summaries:
        fs = "NA" if s["first_sight_commitment_rate"] is None else f'{s["first_sight_commitment_rate"]:.3f}'
        cs = "NA" if s["construction_success_rate"] is None else f'{s["construction_success_rate"]:.3f}'
        lines.append(
            f'| {s["condition"]} | {s["seed"]} | {s["competitive_score"]:.3f} | {fs} | '
            f'{s["hot_class_capture"]:.3f} | {s["trap_builds"]} | {cs} |'
        )
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
