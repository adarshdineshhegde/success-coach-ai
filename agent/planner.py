from agent.planner_tools import get_pending_signals
from calendar_integration.google_calendar import create_event
from datetime import date

TIME_SLOTS = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "14:00",
    "15:00"
]

END_TIMES = [
    "09:45",
    "10:45",
    "11:45",
    "12:45",
    "14:45",
    "15:45"
]

MAX_SESSIONS = 6

def generate_reason(signal):

    if signal["severity"] == "high":
        return "Student reported severe emotional distress and requires urgent support."

    elif signal["severity"] == "medium":
        return "Student is showing academic risk indicators and should be contacted soon."

    else:
        return "Student may benefit from a proactive coaching check-in."

def generate_daily_plan():

    signals = get_pending_signals()

    severity_order = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    urgency_order = {
        "today": 0,
        "tomorrow": 1,
        "this_week": 2
    }

    signals.sort(
        key=lambda s: (
            severity_order.get(s["severity"], 99),
            urgency_order.get(s["urgency"], 99)
        )
    )

    today = []
    deferred = []

    unique_signals = {}
    for signal in signals:
        student_id = signal["student_id"]

        if student_id not in unique_signals:
            unique_signals[student_id] = signal

    signals = list(unique_signals.values())

    for i, signal in enumerate(signals):

        if i >= MAX_SESSIONS:
            deferred.append({
                "student_name": signal["student_name"],
                "reason": "No slots available today"
            })
            continue
        if i < len(TIME_SLOTS):

            if signal["severity"] == "high":
                session_type = "Crisis Session"

            elif signal["severity"] == "medium":
                session_type = "Academic Support"

            else:
                session_type = "Check-in"

            reason = generate_reason(signal)

            today.append({
                "student_name": signal["student_name"],
                "time_slot": TIME_SLOTS[i],
                "session_type": session_type,
                "severity": signal["severity"],
                "reason": reason
            })

            slot = TIME_SLOTS[i]

            create_event(
                title=f"Success Coach Session - {signal['student_name']}",
                date=str(date.today()),
                start_time=TIME_SLOTS[i],
                end_time=END_TIMES[i],
                description=reason
            )

        else:

            deferred.append({
                "student_name": signal["student_name"],
                "reason": "No slots available today"
            })

    return {
        "today": today,
        "deferred": deferred
    }