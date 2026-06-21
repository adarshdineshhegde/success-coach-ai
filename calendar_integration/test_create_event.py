from calendar_integration.google_calendar import create_event

event = create_event(
    title="Success Coach Test Session",
    date="2026-06-22",
    start_time="10:00",
    end_time="10:45",
    description="Testing calendar integration"
)

print(event["htmlLink"])