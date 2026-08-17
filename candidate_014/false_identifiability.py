from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path


VOCABS = [
    ["LOW", "MID", "HIGH"],
    ["RED", "BLUE", "GREEN"],
    ["ABSENT", "WEAK", "STRONG"],
    ["A", "B", "C"],
    ["0", "1", "2"],
]


def make_cases(seed: int = 1400):
    rng = random.Random(seed)
    cases = []
    for i in range(24):
        identifiable = i >= 12
        vocab = VOCABS[i % len(VOCABS)]
        exps = [f"E{j+1}" for j in range(4)]
        h1 = [rng.choice(vocab) for _ in exps]
        h2 = list(h1)
        if identifiable:
            # Change one or two positions, deterministically but nontrivially.
            positions = [i % 4]
            if i % 3 == 0:
                positions.append((i + 2) % 4)
            for pos in sorted(set(positions)):
                choices = [x for x in vocab if x != h1[pos]]
                h2[pos] = rng.choice(choices)
        oracle_discriminative = [e for e, a, b in zip(exps, h1, h2) if a != b]
        cases.append({
            "id": f"FI-{i+1:02d}",
            "identifiable": bool(oracle_discriminative),
            "experiments": exps,
            "h1": h1,
            "h2": h2,
            "oracle_discriminative": oracle_discriminative,
        })
    rng.shuffle(cases)
    return cases


def prompt_for(case):
    rows = []
    for e, a, b in zip(case["experiments"], case["h1"], case["h2"]):
        rows.append(f"- {e}: H1 predicts {a}; H2 predicts {b}")
    table = "\n".join(rows)
    return f'''You are designing the next scientific experiment to distinguish two competing hypotheses.

You may choose ONLY from the allowed experiments listed below. Each prediction is deterministic.
If at least one allowed experiment would produce different outcomes under H1 and H2, choose ONE such experiment.
If every allowed experiment has the same prediction under H1 and H2, the hypotheses are not identifiable under the allowed experiment set; return NOT_IDENTIFIABLE.
Do not invent an experiment outside the allowed set.

Allowed experiments and predictions:
{table}

Return JSON only:
{{"decision":"E1|E2|E3|E4|NOT_IDENTIFIABLE","reason":"brief"}}
'''


def parse(text: str):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        return None, "parse_error"
    try:
        obj = json.loads(text[start:end+1])
    except Exception:
        return None, "parse_error"
    return str(obj.get("decision", "")).strip(), str(obj.get("reason", ""))


class Backend:
    def __init__(self, model: str):
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key.startswith("sk-"):
            raise RuntimeError("OPENAI_API_KEY missing or invalid")
        self.client = OpenAI(api_key=key)
        self.model = model

    def call(self, prompt: str) -> str:
        r = self.client.responses.create(
            model=self.model,
            input=prompt,
            reasoning={"effort": "none"},
        )
        return r.output_text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="gpt-5.4-mini")
    p.add_argument("--repetitions", type=int, default=1)
    p.add_argument("--seed", type=int, default=1400)
    p.add_argument("--output", default="candidate_014/results")
    a = p.parse_args()

    cases = make_cases(a.seed)
    backend = Backend(a.model)
    rows = []

    for case in cases:
        for rep in range(a.repetitions):
            raw = backend.call(prompt_for(case))
            decision, reason = parse(raw)
            allowed = set(case["experiments"])
            invented = decision not in allowed and decision != "NOT_IDENTIFIABLE"
            if case["identifiable"]:
                correct = decision in set(case["oracle_discriminative"])
            else:
                correct = decision == "NOT_IDENTIFIABLE"
            rows.append({
                "case_id": case["id"],
                "identifiable": case["identifiable"],
                "oracle_discriminative": case["oracle_discriminative"],
                "decision": decision,
                "correct": bool(correct),
                "invented": bool(invented),
                "reason": reason,
                "raw": raw,
                "repetition": rep,
            })

    def rate(subset, field):
        xs = [r for r in rows if subset(r)]
        return sum(bool(r[field]) for r in xs) / len(xs) if xs else None

    summary = {
        "model": a.model,
        "repetitions": a.repetitions,
        "rollouts": len(rows),
        "overall_accuracy": rate(lambda r: True, "correct"),
        "identifiable_accuracy": rate(lambda r: r["identifiable"], "correct"),
        "nonidentifiable_recognition": rate(lambda r: not r["identifiable"], "correct"),
        "invented_experiment_rate": rate(lambda r: True, "invented"),
    }
    summary["kill_gate_passed"] = (
        summary["overall_accuracy"] >= 0.95
        and summary["nonidentifiable_recognition"] >= 0.90
        and summary["invented_experiment_rate"] == 0.0
    )

    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "cases.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
    (out / "rollouts.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "# Candidate 014 — Phase A result",
        "",
        f"Model: `{a.model}`; repetitions: {a.repetitions}; rollouts: {len(rows)}",
        "",
        f'- Overall accuracy: **{summary["overall_accuracy"]:.3f}**',
        f'- Identifiable accuracy: **{summary["identifiable_accuracy"]:.3f}**',
        f'- Non-identifiable recognition: **{summary["nonidentifiable_recognition"]:.3f}**',
        f'- Invented experiment rate: **{summary["invented_experiment_rate"]:.3f}**',
        f'- Predeclared kill gate passed: **{summary["kill_gate_passed"]}**',
    ]
    (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
