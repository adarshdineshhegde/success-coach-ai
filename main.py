import streamlit as st
from dotenv import load_dotenv
from data.student_data import get_all_students

load_dotenv()

students = get_all_students()

student_options = {
    f"{student['name']} ({student['student_id']})":
    student["student_id"]
    for student in students
}

selected_student = st.sidebar.selectbox(
    "Select Student",
    list(student_options.keys())
)

selected_student_id = student_options[selected_student]

from agent.coach import get_response

st.set_page_config(
    page_title="Success Coach",
    layout="centered"
)

st.title("Success Coach AI")

# Store separate chat histories for each student
if "student_chats" not in st.session_state:
    st.session_state.student_chats = {}

if selected_student_id not in st.session_state.student_chats:
    st.session_state.student_chats[selected_student_id] = []

messages = st.session_state.student_chats[selected_student_id]

# Render chat history for currently selected student
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# New user message
if prompt := st.chat_input("Ask your coach anything..."):

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    response = get_response(
        prompt,
        selected_student_id
    )

    messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    with st.chat_message("assistant"):
        st.markdown(response)