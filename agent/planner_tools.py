from memory.mem0_client import client
from data.student_data import get_all_students
import json
from langchain_core.tools import tool


def get_pending_signals():

    students = get_all_students()

    all_signals = []

    for student in students:

        results = client.search(
            query="concern signal issue struggling",
            user_id=student["student_id"],
            limit=10
        )

        for r in results:

            metadata = r.get("metadata", {})

            if metadata.get("type") != "signal":
                continue

            all_signals.append({
                "student_id": student["student_id"],
                "student_name": student["name"],
                "concern": r["memory"],
                "severity": metadata.get("severity", "medium"),
                "urgency": metadata.get("urgency", "tomorrow")
            })

    return all_signals

from memory.signals import mark_signal_complete

@tool
def mark_signal_acted_on(memory_id: str) -> str:
    """
    Mark a specific signal as acted on so it doesn't appear in future plans.
    Input: the memory_id of the signal.
    Call this after successfully creating a calendar event for that student.
    """
    return mark_signal_complete(memory_id)