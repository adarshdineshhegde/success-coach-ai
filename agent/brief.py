from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from data.student_data import load_student, get_student_context
from memory.factual_memory import get_relevant_facts
from memory.session_memory import get_session_summaries

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

BRIEF_PROMPT = """You are preparing a success coach for an upcoming session with a student.
Generate a pre-meeting brief from the context below.

CRITICAL: If the factual memory or past sessions mention anything related to the
student's emotional or mental wellbeing — depression, anxiety, stress, burnout,
feeling overwhelmed, family pressure, sleep issues, or similar — this MUST be
surfaced explicitly and prominently. Never omit it, never bury it under academic
details, and never let it get pushed out by routine concerns like a low score or
missed class. If such a concern was mentioned, lead the OPEN CONCERNS section with
it clearly, in the student's own context, even if it seems like it may have been
addressed already. The coach must never walk in unaware of a wellbeing concern this
student has previously raised.

Output exactly these sections:

CURRENT SITUATION
2-3 sentences on academic standing — scores, attendance, anything flagged.

OPEN CONCERNS
Wellbeing concerns (if any) come first, stated plainly. Then bullet points of other
unresolved issues from past sessions or memory. If there are truly no concerns of
any kind, say "Nothing outstanding."

CONVERSATION STARTERS
2-3 specific, natural opening questions the coach could use, grounded in what this
student has actually shared before. Not generic ("how are you?") — specific
("Last time you mentioned recursion was clicking better, did that continue?").
If a wellbeing concern was raised previously, at least one starter should give the
coach a natural, caring way to check in on it directly.

Keep the whole brief readable in under 30 seconds. No filler — except never compress
or skip a wellbeing concern for the sake of brevity."""


def generate_brief(student_id: str) -> str:
    """
    Build a pre-meeting brief for a single student, pulling from
    Sheets data, factual memory, and past session summaries.
    """
    student = load_student(student_id)
    student_context = get_student_context(student)
    facts = get_relevant_facts(
        student_id,
        "wellbeing emotional state stress anxiety mental health struggles concerns patterns preferences"
    )
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