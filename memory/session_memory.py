from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from memory.mem0_client import client


llm = ChatOpenAI(
    model="gpt-5.4-mini-2026-03-17",
    temperature=0
)

SUMMARY_PROMPT = """
You are summarizing a coaching session.

Produce a concise summary containing:

1. Student concerns
2. Key discussion points
3. Advice given
4. Student commitments/action items
5. Overall tone of the session

Keep it factual and concise.
"""


def summarize_session(messages):

    conversation = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in messages
    )

    response = llm.invoke([
        SystemMessage(content=SUMMARY_PROMPT),
        HumanMessage(content=conversation)
    ])

    return response.content


def store_session_summary(student_id, summary):

    result = client.add(
        messages=[
            {
                "role": "user",
                "content": f"Session Summary: {summary}"
            }
        ],
        user_id=student_id,
        metadata={
            "type": "session_summary"
        }
    )

    return result

def get_session_summaries(student_id: str) -> str:

    results = client.search(
        query="session summary",
        user_id=student_id,
        limit=3
    )

    if not results:
        return "No previous sessions."

    summaries = []

    for item in results:
        summaries.append(item["memory"])

    return "\n\n---\n\n".join(summaries)