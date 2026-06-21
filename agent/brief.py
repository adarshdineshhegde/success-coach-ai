from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from data.student_data import load_student, get_student_context
from memory.factual_memory import get_relevant_facts
from memory.session_memory import get_session_summaries

llm = ChatOpenAI(model="gpt-5.4-mini-2026-03-17", temperature=0.3)

BRIEF_PROMPT = """You are preparing a success coach for an upcoming session with a student.
Generate a pre-meeting brief from the context below.

Output exactly these sections:

CURRENT SITUATION
2-3 sentences on academic standing — scores, attendance, anything flagged.

OPEN CONCERNS
Bullet points of unresolved issues from past sessions or memory. If none, say "Nothing outstanding."

CONVERSATION STARTERS
2-3 specific, natural opening questions the coach could use, grounded in what this
student has actually shared before. Not generic ("how are you?") — specific
("Last time you mentioned recursion was clicking better, did that continue?").

Keep the whole brief readable in under 30 seconds. No filler."""


def generate_brief(student_id: str) -> str:
    """
    Build a pre-meeting brief for a single student, pulling from
    Sheets data, factual memory, and past session summaries.
    """
    student = load_student(student_id)
    student_context = get_student_context(student)
    facts = get_relevant_facts(student_id, "general history and patterns")
    sessions = get_session_summaries(student_id)

    context = (
        f"STUDENT DATA:\n{student_context}\n\n"
        f"FACTUAL MEMORY:\n{facts}\n\n"
        f"PAST SESSIONS:\n{sessions}"
    )

    response = llm.invoke([
        SystemMessage(content=BRIEF_PROMPT),
        HumanMessage(content=context)
    ])
    return response.content