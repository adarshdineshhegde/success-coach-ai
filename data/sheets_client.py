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

    creds = Credentials.from_service_account_file(
    "service_account.json",
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