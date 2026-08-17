from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modal_collapse as m  # noqa: E402


def prompt_for(s, mode, presentation):
    rule = m.rule_for(s, mode)
    task = m.task_for(s, mode)
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

Task:
{task}

Core action needed to complete the task: `{core}`
Potential extra action: `{extra}`

{guidance}

Allowed actions: {json.dumps([core, extra])}
Return JSON only with exactly these keys:
{{"actions":["..."],"reason":"brief"}}
'''


m.prompt_for = prompt_for

if __name__ == "__main__":
    m.main()
