import os
import json

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

print("GOOGLE_SERVICE_ACCOUNT_JSON exists:",
      os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") is not None)

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

def get_calendar_service():

    credentials_info = json.loads(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    )

    creds = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES
    )

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    return service


COACH_CALENDAR_ID = os.getenv("COACH_CALENDAR_ID")


def create_event(
    title: str,
    date: str,
    start_time: str,
    end_time: str,
    description: str = ""
):

    service = get_calendar_service()

    event = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": f"{date}T{start_time}:00",
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": f"{date}T{end_time}:00",
            "timeZone": "Asia/Kolkata"
        }
    }

    return (
        service.events()
        .insert(
            calendarId=COACH_CALENDAR_ID,
            body=event
        )
        .execute()
    )