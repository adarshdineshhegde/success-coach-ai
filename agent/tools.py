from langchain_core.tools import tool
from data.student_data import load_student, get_student_context
from knowledge_base.vectorstore import retrieve as kb_retrieve
from memory.factual_memory import get_relevant_facts
from memory.session_memory import get_session_summaries

# student_id needs to be available to tools at runtime
# we'll inject it via a closure — explained below
_current_student_id: str = ""

def set_student_id(student_id: str):
    """Called once per request to set which student the agent is working with."""
    global _current_student_id
    _current_student_id = student_id

@tool
def get_student_data(query: str) -> str:
    """
    Fetch the current student's academic data from Google Sheets.
    Use this when the student asks about their scores, attendance, 
    upcoming exams, cohort, or overall progress.
    Input: a short description of what you need (e.g. 'exam dates', 'attendance')
    """
    student = load_student(_current_student_id)
    return get_student_context(student)

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the platform knowledge base for documentation, policies, 
    features, processes, and program information.
    Use this when the student asks how something works on the platform,
    what a feature does, or about program rules and policies.
    Input: the student's question or key terms to search for.
    """
    return kb_retrieve(query)

@tool
def get_student_memory(query: str) -> str:
    """
    Retrieve facts remembered about this student from past sessions.
    Use this when the student references something from a previous session,
    or when their question requires knowing their history, preferences, 
    recurring challenges, or past decisions.
    Input: what aspect of their history is relevant to the current question.
    """
    return get_relevant_facts(
        student_id=_current_student_id,
        query=query
    )

@tool
def get_past_sessions(query: str) -> str:
    """
    Retrieve summaries of this student's previous coaching sessions.
    Use this when the student asks what was discussed before, 
    or when continuity with past conversations would improve your response.
    Input: what you're looking for in past sessions.
    """
    return get_session_summaries(_current_student_id)

from data.student_data import get_all_students
from memory.signals import get_all_signals as _get_all_signals

@tool
def get_all_signals_tool(query: str) -> str:
    """
    Retrieve all flagged concern signals across all students.
    Use this when the coach asks who needs attention today,
    which students have urgent concerns, or requests a daily plan.
    Input: what you're looking for (e.g. 'urgent concerns today')
    """
    students = get_all_students()
    signals  = _get_all_signals(students)

    if not signals:
        return "No signals flagged across any students."

    lines = []
    for s in signals:
        lines.append(
            f"[{s['severity'].upper()} / {s['urgency']}] "
            f"{s['student_name']} ({s['student_id']}): {s['concern']}"
        )
    return "\n".join(lines)