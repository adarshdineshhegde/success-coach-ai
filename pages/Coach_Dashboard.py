import streamlit as st
from dotenv import load_dotenv

from data.student_data import get_all_students
from agent.planner import generate_daily_plan
from agent.brief import generate_brief
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
# M9 - PLAN CHANGES
# ---------------------------------------------------

if st.session_state.get("plan_changes"):

    with st.expander(
        "📋 What changed in today's plan",
        expanded=True
    ):

        for change in st.session_state.plan_changes:

            st.markdown(
                f"- {change}"
            )

    st.divider()

# ---------------------------------------------------
# M9 - CONFLICTS REQUIRING COACH DECISION
# ---------------------------------------------------

if st.session_state.get("pending_conflicts"):

    st.error(
        "⚠️ Scheduling conflict detected. Coach decision required."
    )

    for idx, conflict in enumerate(
        st.session_state.pending_conflicts
    ):

        with st.container(border=True):

            st.markdown(
                f"**{conflict['tradeoff_explanation']}**"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    f"### New Student\n"
                    f"**{conflict['new_student']['name']}**"
                )

                st.caption(
                    f"{conflict['new_student']['severity']} | "
                    f"{conflict['new_student']['urgency']}"
                )

                st.write(
                    conflict['new_student']['concern']
                )

                if st.button(
                    f"Give slot to {conflict['new_student']['name']}",
                    key=f"new_{idx}"
                ):

                    plan = st.session_state.daily_plan

                    existing = conflict["existing_student"]
                    new_student = conflict["new_student"]

                    plan["today"] = [
                        s
                        for s in plan["today"]
                        if not (
                            s["student_name"] == existing["name"]
                            and
                            s["time_slot"] == existing["time_slot"]
                        )
                    ]

                    plan.setdefault(
                        "deferred",
                        []
                    ).append({
                        "student_name": existing["name"],
                        "reason": "Replaced by higher-priority student"
                    })

                    plan["today"].append({
                        "student_name": new_student["name"],
                        "time_slot": existing["time_slot"],
                        "session_type": "Crisis Session",
                        "severity": new_student["severity"],
                        "reason": new_student["concern"]
                    })

                    st.session_state.setdefault(
                        "plan_changes",
                        []
                    ).append(
                        f"{new_student['name']} replaced "
                        f"{existing['name']} at "
                        f"{existing['time_slot']} due to higher-priority signal."
                    )

                    st.session_state.pending_conflicts.pop(idx)

                    st.session_state.daily_plan = plan

                    st.rerun()

            with col2:

                st.markdown(
                    f"### Existing Student\n"
                    f"**{conflict['existing_student']['name']}**"
                )

                st.caption(
                    f"Scheduled at "
                    f"{conflict['existing_student']['time_slot']}"
                )

                st.write(
                    conflict['existing_student']['concern']
                )

                if st.button(
                    f"Keep {conflict['existing_student']['name']}",
                    key=f"keep_{idx}"
                ):

                    plan = st.session_state.daily_plan

                    plan.setdefault(
                        "deferred",
                        []
                    ).append({
                        "student_name":
                            conflict["new_student"]["name"],
                        "reason":
                            "Coach chose to keep existing scheduled student"
                    })

                    st.session_state.setdefault(
                        "plan_changes",
                        []
                    ).append(
                        f"{conflict['new_student']['name']} "
                        f"was deferred after coach decision."
                    )

                    st.session_state.pending_conflicts.pop(idx)

                    st.session_state.daily_plan = plan

                    st.rerun()

    st.divider()

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
# PRE-MEETING BRIEF SECTION
# ---------------------------------------------------

st.subheader("Pre-Meeting Brief")

if students:

    student_options = {s["name"]: s["student_id"] for s in students}

    selected_name = st.selectbox(
        "Select a student",
        student_options.keys(),
        key="brief_student_select"
    )

    if st.button("Generate Brief"):

        with st.spinner("Preparing brief..."):
            brief = generate_brief(student_options[selected_name])

        st.session_state.current_brief = brief
        st.session_state.current_brief_student = selected_name

    if "current_brief" in st.session_state:

        st.markdown(f"**Brief for {st.session_state.current_brief_student}**")
        st.markdown(st.session_state.current_brief)

else:
    st.info("No students found.")

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