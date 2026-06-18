from dotenv import load_dotenv

load_dotenv()

from data.sheets_client import get_spreadsheet

sheet = get_spreadsheet()

for sheet_name in [
    "exam_scores",
    "attendance",
    "exam_schedule",
    "signal_sheet"
]:
    print(f"\n===== {sheet_name} =====")

    ws = sheet.worksheet(sheet_name)

    rows = ws.get_all_records()

    print(f"Rows: {len(rows)}")

    if rows:
        print(rows[0])