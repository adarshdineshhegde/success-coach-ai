import os
from dotenv import load_dotenv
from calendar_integration.google_calendar import get_calendar_service

service = get_calendar_service()
load_dotenv()

calendar_id = os.getenv("COACH_CALENDAR_ID")

events = service.events().list(
    calendarId=calendar_id,
    maxResults=10
).execute()

print(events)