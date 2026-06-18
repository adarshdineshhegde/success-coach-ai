from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from data.student_data import STUDENT, get_student_context
from knowledge_base.vectorstore import retrieve

llm = ChatOpenAI(
    model="gpt-5.4-mini-2026-03-17",
    temperature=0.7
)

SYSTEM_PROMPT = """
You are a Success Coach for students at NxtWave's CCBP program.

You have access to two sources of information:

1. STUDENT DATA
2. KNOWLEDGE BASE DOCUMENTATION

Rules:
- Use STUDENT DATA for personalized coaching.
- Use KNOWLEDGE BASE for platform-related questions.
- When prompted, identify attendance issues, low scores, and upcoming exams.
- Suggest actionable next steps.
- If the answer is not present in the KNOWLEDGE BASE, clearly say that the documentation does not contain that information.
- Do not invent platform features or processes.
"""

def get_response(user_message: str) -> str:

    student_context = get_student_context(STUDENT)

    kb_context = retrieve(user_message)

    full_system = f"""
{SYSTEM_PROMPT}

====================
STUDENT DATA
====================

{student_context}

====================
KNOWLEDGE BASE
====================

{kb_context}
"""

    messages = [
        SystemMessage(content=full_system),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)

    return response.content