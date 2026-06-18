import os
import json

from dotenv import load_dotenv

load_dotenv()

import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import os
import json

import gspread

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


def get_gspread_client():

    credentials_json = json.loads(
        os.getenv("CREDENTIALS")
    )

    token_file = "token.json"

    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(
            token_file,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_config(
                credentials_json,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return gspread.authorize(creds)

def get_spreadsheet():

    client = get_gspread_client()

    spreadsheet_id = os.getenv(
        "GOOGLE_SPREADSHEET_ID"
    )

    return client.open_by_key(
        spreadsheet_id
    )