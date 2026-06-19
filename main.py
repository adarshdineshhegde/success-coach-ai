import streamlit as st
from dotenv import load_dotenv
from memory.factual_memory import store_facts_from_conversation

from data.student_data import (
    get_all_students,
    load_student
)

from memory.session_memory import (
    summarize_session,
    store_session_summary,
    get_session_summaries
)

st.set_page_config(
    page_title="Success Coach",
    layout="centered"
)

load_dotenv()

st.markdown("""
<style>

html, body, [class*="css"] {
    font-size: 18px;
}

[data-testid="stChatMessageContent"] {
    font-size: 1.1rem;
    line-height: 1.7;
}

textarea {
    font-size: 18px !important;
}

button {
    font-size: 16px !important;
}

</style>
""", unsafe_allow_html=True)


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
student = load_student(selected_student_id)

st.sidebar.divider()

st.sidebar.subheader("Previous Sessions")

try:

    previous_sessions = get_session_summaries(
        selected_student_id
    )

    st.sidebar.text_area(
        label="Recent Session Summaries",
        value=previous_sessions,
        height=250,
        disabled=True
    )

except Exception:

    st.sidebar.info(
        "No previous sessions found."
    )

if "last_student" not in st.session_state:
    st.session_state.last_student = selected_student_id

elif st.session_state.last_student != selected_student_id:

    st.toast(
        f"Loaded {student['name']} 👋"
    )

    st.session_state.last_student = selected_student_id

from agent.coach import get_response


st.title("Success Coach AI")

# Store separate chat histories for each student
if "student_chats" not in st.session_state:
    st.session_state.student_chats = {}

if selected_student_id not in st.session_state.student_chats:
    st.session_state.student_chats[selected_student_id] = []

messages = st.session_state.student_chats[selected_student_id]
if len(messages) == 0:

    st.markdown(
        f"""
## Hey {student["name"]} 👋

Welcome back!

**Program:** {student["program"]}

**Cohort:** {student["cohort"]}

Ask me anything about:

- Your progress
- Upcoming exams
- Study planning
- Platform features
- Career preparation
"""
    )

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

if messages:

    if st.button("End Session & Save"):

        with st.spinner("Saving session..."):

            store_facts_from_conversation(
                student_id=selected_student_id,
                messages=messages
            )

            summary = summarize_session(messages)

            store_session_summary(
                student_id=selected_student_id,
                summary=summary
            )

        st.success("Session saved successfully!")

        # Clear only this student's chat history
        st.session_state.student_chats[selected_student_id] = []

        st.rerun()
    