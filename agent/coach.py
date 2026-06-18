from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(
    model="gpt-5.4-mini-2026-03-17",
    temperature=0.7
)

SYSTEM_PROMPT = """
You are a Success Coach for students.

Be encouraging, helpful, and actionable.
"""

def get_response(user_message: str) -> str:

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)

    return response.content