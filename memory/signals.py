from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from memory.mem0_client import client
from datetime import date
import json

llm = ChatOpenAI(model="gpt-5.4-mini-2026-03-17", temperature=0)

SIGNAL_PROMPT = SIGNAL_PROMPT = """
You are a signal-classification engine.

Your job is NOT to coach, summarize, advise, infer intent, or explain reasoning.

Your ONLY task is to identify concerning signals in a coaching session summary and classify them according to the rules below.

========================
CLASSIFICATION RULES
====================

HIGH PRIORITY RULES
These rules override ALL other rules.

If the student mentions ANY of the following:

* depression
* anxiety
* panic attacks
* suicidal thoughts
* self-harm
* wanting to die
* feeling hopeless
* emotional breakdown
* mental health crisis

THEN classify as:
{
"severity": "high",
"urgency": "today"
}

If the student mentions:

* not sleeping for multiple days
* extreme exhaustion from lack of sleep

THEN classify as:
{
"severity": "high",
"urgency": "today"
}

If the student mentions:

* family crisis
* serious personal trauma
* major personal loss
* severe family conflict
* emotional breakdown caused by personal events

THEN classify as:
{
"severity": "high",
"urgency": "today"
}

ACADEMIC RULES

If:

* exam is tomorrow
  AND
* student says they have not studied or are unprepared

THEN:
{
"severity": "high",
"urgency": "today"
}

If:

* score is below 50%

THEN:
{
"severity": "medium",
"urgency": "tomorrow"
}

If:

* attendance is below 75%

THEN:
{
"severity": "medium",
"urgency": "this_week"
}

If:

* student is struggling with a topic
* student repeatedly mentions confusion
* student lacks confidence in a subject

THEN:
{
"severity": "low",
"urgency": "this_week"
}

========================
DECISION RULES
==============

1. Extract every concern that matches the rules.
2. Do not invent concerns.
3. Do not infer concerns that are not explicitly stated.
4. If multiple rules match, return multiple concern objects.
5. If a concern matches multiple severity levels, choose the highest severity.
6. Use the student's actual words whenever possible.
7. Ignore positive statements unless they indicate a concern.
8. Never provide explanations.

========================
OUTPUT FORMAT
========================

If concerns exist:

[
{
"concern": "...",
"severity": "low|medium|high",
"urgency": "today|tomorrow|this_week"
}
]

If only one concern exists:

{
"concern": "...",
"severity": "low|medium|high",
"urgency": "today|tomorrow|this_week"
}

If no concerns exist:

{
"no_signals": true
}

Return ONLY valid JSON.
Do not include markdown.
Do not include code fences.
Do not include explanations.

SESSION SUMMARY:
{session_summary}
"""


def extract_signals(session_summary: str) -> list[dict]:
    """Run the summary through the LLM and extract structured signals."""
    response = llm.invoke([
        SystemMessage(content=SIGNAL_PROMPT),
        HumanMessage(content=f"Session summary:\n{session_summary}")
    ])
    
    raw = response.content.strip()
    
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # if LLM adds backticks despite instructions, strip them
        clean = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean)
    
    # normalize — could be a single object or a list
    if isinstance(parsed, dict):
        if parsed.get("no_signals"):
            return []
        return [parsed]
    return parsed

def store_signal(student_id: str, student_name: str, signal: dict):
    """Store a single signal in Mem0 under the student's ID."""
    print(f"STORING SIGNAL: {signal}")  # add this
    content = (
        f"SIGNAL | severity={signal['severity']} urgency={signal['urgency']} | "
        f"{signal['concern']}"
    )
    content = (
        f"SIGNAL | severity={signal['severity']} urgency={signal['urgency']} | "
        f"{signal['concern']}"
    )
    client.add(
        [{"role": "user", "content": content}],
        user_id=student_id,
        metadata={
            "type":         "signal",
            "student_name": student_name,
            "severity":     signal["severity"],
            "urgency":      signal["urgency"],
            "session_date": str(date.today()),
            "acted_on":     False
        }
    )

def generate_and_store_signals(student_id: str, student_name: str, session_summary: str):
    """Full pipeline — extract signals from summary and store each one."""
    signals = extract_signals(session_summary)
    for signal in signals:
        store_signal(student_id, student_name, signal)
    return signals   # return so main.py can log or display count

def get_all_signals(students: list[dict]) -> list[dict]:
    all_signals = []
    seen = set()  # track duplicates

    for student in students:
        student_id   = student.get("student_id")
        student_name = student.get("name")

        if not student_id:
            continue

        try:
            results = client.search(
                query="concern issue struggling distressed failing",
                user_id=student_id,
                filters={"type": "signal"},
                limit=10
            )

            for r in results:
                metadata = r.get("metadata", {})

                if metadata.get("type") != "signal":
                    continue

                # deduplicate on student + concern text
                dedup_key = (student_id, r.get("memory", ""))
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                all_signals.append({
                    "student_id":   student_id,
                    "student_name": student_name,
                    "concern":      r.get("memory", ""),
                    "severity":     metadata.get("severity", "medium"),
                    "urgency":      metadata.get("urgency", "tomorrow"),
                    "session_date": metadata.get("session_date", ""),
                })

        except Exception:
            continue

    severity_order = {"high": 0, "medium": 1, "low": 2}
    urgency_order  = {"today": 0, "tomorrow": 1, "this_week": 2}

    all_signals.sort(key=lambda x: (
        severity_order.get(x["severity"], 1),
        urgency_order.get(x["urgency"], 1)
    ))

    return all_signals