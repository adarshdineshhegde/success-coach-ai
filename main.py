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

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your coach anything..."):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    response = get_response(
    prompt,
    selected_student_id)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    with st.chat_message("assistant"):
        st.markdown(response)