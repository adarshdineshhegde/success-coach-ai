from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from data.student_data import STUDENT, get_student_context


llm = ChatOpenAI(
    model="gpt-5.4-mini-2026-03-17",
    temperature=0.7
)

SYSTEM_PROMPT = """You are a Success Coach for students at NxtWave's CCBP program.
You have access to the student's real data below. Use it to give specific, 
personalized advice. When prompted , flag issues like : low scores, attendance issues, or 
upcoming exams . Suggest actionable steps for improvement for these issues proactively . 
"""

def get_response(user_message: str) -> str:
    student_context = get_student_context(STUDENT)
    
    full_system = SYSTEM_PROMPT + "\n\n" + student_context
    
    messages = [
        SystemMessage(content=full_system),
        HumanMessage(content=user_message)
    ]
    response = llm.invoke(messages)

    return response.content