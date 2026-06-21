import streamlit as st
from dotenv import load_dotenv

from data.student_data import get_all_students
from agent.planner import generate_daily_plan
from memory.signals import (
    get_all_signals,
    mark_signal_complete
)

load_dotenv()

st.set_page_config(
    page_title="Coach Dashboard",
    page_icon="🎯",
    layout="wide"
)

st.title("Coach Dashboard")
st.caption(
    "Flagged signals across all students, sorted by severity and urgency."
)

SEVERITY_COLOR = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢"
}

URGENCY_LABEL = {
    "today": "Act today",
    "tomorrow": "Tomorrow",
    "this_week": "This week"
}

with st.spinner("Loading signals..."):
    students = get_all_students()
    all_signals = get_all_signals(students)

# filter out resolved signals before anything else uses all_signals
all_signals = [s for s in all_signals if not s.get("acted_on")]

# ---------------------------------------------------
# PLAN GENERATION SECTION
# ---------------------------------------------------

st.subheader("Today's Plan")

if st.button("Generate Today's Plan"):

    with st.spinner("Generating plan..."):
        plan = generate_daily_plan()

    st.session_state.daily_plan = plan

if "daily_plan" in st.session_state:

    plan = st.session_state.daily_plan

    st.markdown("### Scheduled Today")

    if plan["today"]:

        for item in plan["today"]:

            st.success(
                f"{item['time_slot']} | "
                f"{item['student_name']} | "
                f"{item['session_type']}"
            )

            st.caption(item["reason"])

    else:
        st.info("No students scheduled today.")

    st.markdown("### Deferred")

    if plan["deferred"]:

        for item in plan["deferred"]:

            st.warning(
                f"{item['student_name']} - {item['reason']}"
            )

    else:
        st.info("No deferred students.")

st.divider()

# ---------------------------------------------------
# SIGNAL SUMMARY METRICS
# ---------------------------------------------------

if not all_signals:
    st.info(
        "No signals flagged yet. Signals appear here after sessions end."
    )
    st.stop()

high = sum(
    1 for s in all_signals
    if s["severity"] == "high"
)

medium = sum(
    1 for s in all_signals
    if s["severity"] == "medium"
)

low = sum(
    1 for s in all_signals
    if s["severity"] == "low"
)

today = sum(
    1 for s in all_signals
    if s["urgency"] == "today"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Signals", len(all_signals))
col2.metric("🔴 High", high)
col3.metric("🟡 Medium", medium)
col4.metric("⚡ Act Today", today)

st.divider()

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

severity_filter = st.selectbox(
    "Filter by severity",
    ["All", "High", "Medium", "Low"],
    index=0
)

if severity_filter != "All":

    all_signals = [
        s for s in all_signals
        if s["severity"] == severity_filter.lower()
    ]

if not all_signals:

    st.info(
        f"No {severity_filter.lower()} severity signals."
    )

    st.stop()

# ---------------------------------------------------
# SIGNAL CARDS
# ---------------------------------------------------

for idx, sig in enumerate(all_signals):

    icon = SEVERITY_COLOR.get(
        sig["severity"],
        "🟡"
    )

    urgency = URGENCY_LABEL.get(
        sig["urgency"],
        sig["urgency"]
    )

    with st.expander(
        f"{icon} {sig['student_name']} · {urgency} · {sig['session_date']}"
    ):

        st.markdown(
            f"**Concern:** {sig['concern']}"
        )

        st.caption(
            f"Severity: **{sig['severity'].upper()}** | "
            f"Urgency: **{urgency}** | "
            f"Student ID: `{sig['student_id']}`"
        )

        if st.button(
            "Mark Complete",
            key=f"complete_{sig['memory_id']}"
        ):

            mark_signal_complete(
                sig["memory_id"]
            )

            st.success(
                "Signal marked complete."
            )

            st.rerun()