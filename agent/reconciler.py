from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

llm = ChatOpenAI(
    model="gpt-5.4-mini-2026-03-17",
    temperature=0
)

RECONCILE_PROMPT = """
You are updating an existing coaching plan.

Return ONLY JSON.

Possible actions:

{
    "action": "add"
}

{
    "action": "defer_new"
}

{
    "action": "conflict"
}

Rules:

1. If free slots exist -> add
2. If plan full and new signal lower priority -> defer_new
3. If plan full and new signal higher priority than someone scheduled -> conflict
"""

def reconcile_new_signal(
    existing_plan,
    new_signal,
    max_sessions=6
):

    context = {
        "plan": existing_plan,
        "new_signal": new_signal,
        "max_sessions": max_sessions
    }

    response = llm.invoke([
        SystemMessage(content=RECONCILE_PROMPT),
        HumanMessage(content=json.dumps(context))
    ])

    raw = (
        response.content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(raw)

def apply_reconciliation(plan, action):

    if action["action"] == "add":

        plan["today"].append({
            "student_name": action["student_name"],
            "time_slot": action["time_slot"],
            "session_type": action["session_type"],
            "reason": action["reason"]
        })

        summary = (
            f"Added {action['student_name']} "
            f"to today's plan"
        )

    elif action["action"] == "defer_new":

        plan.setdefault(
            "deferred",
            []
        ).append({

            "student_name":
            action["student_name"],

            "reason":
            action["reason"]
        })

        summary = (
            f"Deferred "
            f"{action['student_name']}"
        )

    else:

        summary = (
            "Conflict detected."
        )

    return plan, summary