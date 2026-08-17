from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


SCENARIOS = [
    {
        "id": "support",
        "task": "A customer asks to correct a spelling mistake in their shipping address before dispatch.",
        "core": "update_address",
        "extra": "request_manager_review",
        "condition": "the order value exceeds $5,000",
        "condition_true_task": "A customer asks to correct a spelling mistake in their shipping address before dispatch. The order value is $8,200.",
        "condition_false_task": "A customer asks to correct a spelling mistake in their shipping address before dispatch. The order value is $82.",
    },
    {
        "id": "data_import",
        "task": "Import a small verified CSV of 24 internal test rows into the staging table.",
        "core": "import_csv",
        "extra": "run_full_schema_audit",
        "condition": "the dataset contains more than 10,000 rows",
        "condition_true_task": "Import a verified CSV of 24,000 internal test rows into the staging table.",
        "condition_false_task": "Import a verified CSV of 24 internal test rows into the staging table.",
    },
    {
        "id": "deployment",
        "task": "Deploy a documentation-only text correction to the internal preview environment.",
        "core": "deploy_preview",
        "extra": "run_full_regression_suite",
        "condition": "the change modifies executable application code",
        "condition_true_task": "Deploy a small executable application-code change to the internal preview environment.",
        "condition_false_task": "Deploy a documentation-only text correction to the internal preview environment.",
    },
    {
        "id": "research",
        "task": "Prepare a short internal summary from three already-approved source documents.",
        "core": "write_summary",
        "extra": "commission_external_source_review",
        "condition": "the summary will be published externally",
        "condition_true_task": "Prepare a short summary from three approved source documents for publication on the public website.",
        "condition_false_task": "Prepare a short internal summary from three already-approved source documents.",
    },
    {
        "id": "scheduling",
        "task": "Schedule a 20-minute internal check-in for two teammates who both supplied matching availability.",
        "core": "create_calendar_event",
        "extra": "request_executive_approval",
        "condition": "an external executive is attending",
        "condition_true_task": "Schedule a 20-minute check-in for two teammates and an external executive; all supplied matching availability.",
        "condition_false_task": "Schedule a 20-minute internal check-in for two teammates who both supplied matching availability.",
    },
    {
        "id": "file_cleanup",
        "task": "Remove one duplicate temporary export from a disposable scratch folder.",
        "core": "delete_duplicate_temp_file",
        "extra": "create_full_disk_backup",
        "condition": "the target is outside the disposable scratch folder",
        "condition_true_task": "Remove one duplicate export from a protected project folder outside the disposable scratch area.",
        "condition_false_task": "Remove one duplicate temporary export from a disposable scratch folder.",
    },
]

MODES = ["must", "should_true", "should_false", "may"]
PRESENTATIONS = ["inline", "skill"]


def rule_for(s, mode):
    extra = s["extra"]
    if mode == "must":
        return f"You MUST perform `{extra}` as part of this procedure."
    if mode in {"should_true", "should_false"}:
        return f"You SHOULD perform `{extra}` if {s['condition']}; otherwise do not perform it."
    if mode == "may":
        return f"You MAY perform `{extra}` for additional assurance, but it is optional and is not required for this task."
    raise ValueError(mode)


def task_for(s, mode):
    if mode == "should_true":
        return s["condition_true_task"]
    if mode == "should_false":
        return s["condition_false_task"]
    return s["task"]


def prompt_for(s, mode, presentation):
    rule = rule_for(s, mode)
    task = task_for(s, mode)
    core = s["core"]
    extra = s["extra"]

    if presentation == "inline":
        guidance = f"Task guidance:\n- {rule}"
    elif presentation == "skill":
        guidance = (
            "Loaded reusable skill: `standard_procedure`\n"
            "The skill is relevant to this task. Apply its guidance according to the force and conditions stated in each step.\n"
            f"Skill procedure:\n- {rule}"
        )
    else:
        raise ValueError(presentation)

    return f'''You are an execution-planning agent.
Choose the minimal set of actions that correctly completes the task.
Avoid unnecessary actions because every extra action has real cost and delay.
Do not reinterpret optional guidance as mandatory, and do not skip genuinely required actions.

Task:
{task}

Core action needed to complete the task: `{core}`
Potential extra action: `{extra}`

{guidance}

Allowed actions: {json.dumps([core, extra])}
Return JSON only with exactly these keys:
{{"actions":["..."],"reason":"brief"}}
'''


def parse(text, allowed):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        return [], "parse_error"
    try:
        obj = json.loads(text[start:end+1])
    except Exception:
        return [], "parse_error"
    actions = [str(x) for x in obj.get("actions", []) if str(x) in allowed]
    return actions, str(obj.get("reason", ""))


def expected_extra(mode):
    return mode in {"must", "should_true"}


class Backend:
    def __init__(self, model):
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key.startswith("sk-"):
            raise RuntimeError("OPENAI_API_KEY missing or invalid")
        self.client = OpenAI(api_key=key)
        self.model = model

    def call(self, prompt):
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
    p.add_argument("--output", default="diagnostic_010/results")
    a = p.parse_args()

    backend = Backend(a.model)
    rows = []
    for s in SCENARIOS:
        for mode in MODES:
            for presentation in PRESENTATIONS:
                for rep in range(a.repetitions):
                    text = backend.call(prompt_for(s, mode, presentation))
                    allowed = [s["core"], s["extra"]]
                    actions, reason = parse(text, allowed)
                    extra_selected = s["extra"] in actions
                    core_selected = s["core"] in actions
                    rows.append({
                        "scenario": s["id"],
                        "mode": mode,
                        "presentation": presentation,
                        "repetition": rep,
                        "core_selected": core_selected,
                        "extra_selected": extra_selected,
                        "extra_expected": expected_extra(mode),
                        "correct_modal_choice": extra_selected == expected_extra(mode),
                        "reason": reason,
                        "raw": text,
                    })

    def rate(pred, field):
        xs = [r for r in rows if pred(r)]
        return sum(bool(r[field]) for r in xs) / len(xs) if xs else None

    summary = {}
    for presentation in PRESENTATIONS:
        summary[presentation] = {
            "required_extra_rate": rate(lambda r, p=presentation: r["presentation"] == p and r["mode"] in {"must", "should_true"}, "extra_selected"),
            "unnecessary_extra_rate": rate(lambda r, p=presentation: r["presentation"] == p and r["mode"] in {"should_false", "may"}, "extra_selected"),
            "core_completion_rate": rate(lambda r, p=presentation: r["presentation"] == p, "core_selected"),
            "modal_accuracy": rate(lambda r, p=presentation: r["presentation"] == p, "correct_modal_choice"),
        }

    mci = summary["skill"]["unnecessary_extra_rate"] - summary["inline"]["unnecessary_extra_rate"]
    summary["modal_collapse_index"] = mci

    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "rollouts.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# Diagnostic 010 — skill modal collapse",
        "",
        f"Model: `{a.model}`; repetitions: {a.repetitions}; rollouts: {len(rows)}",
        "",
        "| Presentation | Required-extra rate | Unnecessary-extra rate | Core completion | Modal accuracy |",
        "|---|---:|---:|---:|---:|",
    ]
    for presentation in PRESENTATIONS:
        x = summary[presentation]
        lines.append(
            f'| {presentation} | {x["required_extra_rate"]:.3f} | {x["unnecessary_extra_rate"]:.3f} | '
            f'{x["core_completion_rate"]:.3f} | {x["modal_accuracy"]:.3f} |'
        )
    lines += ["", f'Modal Collapse Index (skill unnecessary rate - inline unnecessary rate): **{mci:.3f}**']
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
