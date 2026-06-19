import json
from pathlib import Path


SESSIONS_FILE = Path(
    "storage/sessions.json"
)


def save_session(
    student_id,
    messages
):

    if SESSIONS_FILE.exists():

        with open(SESSIONS_FILE, "r") as f:
            data = json.load(f)

    else:
        data = {}

    data.setdefault(
        student_id,
        []
    )

    data[student_id].append(messages)

    with open(SESSIONS_FILE, "w") as f:
        json.dump(
            data,
            f,
            indent=2
        )


def get_sessions(student_id):

    if not SESSIONS_FILE.exists():
        return []

    with open(SESSIONS_FILE, "r") as f:
        data = json.load(f)

    return data.get(
        student_id,
        []
    )