import os
import json

from dotenv import load_dotenv

load_dotenv()

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


def get_gspread_client():

    credentials_info = json.loads(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    )

    creds = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES
    )

    return gspread.authorize(creds)


def get_spreadsheet():

    client = get_gspread_client()

    spreadsheet_id = os.getenv(
        "GOOGLE_SPREADSHEET_ID"
    )

    return client.open_by_key(
        spreadsheet_id
    )