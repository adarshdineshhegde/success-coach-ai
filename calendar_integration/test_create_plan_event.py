from calendar_integration.google_calendar import create_event

event = create_event(
    title="Success Coach Session - Rahul Verma",
    date="2026-06-22",
    start_time="09:00",
    end_time="09:45",
    description="High severity signal detected."
)

print(event.get("htmlLink"))