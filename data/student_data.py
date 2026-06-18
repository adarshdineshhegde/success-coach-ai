from data.sheets_client import get_spreadsheet

STUDENT_ID = "STU002"

def get_all_students():
    spreadsheet = get_spreadsheet()

    roster = spreadsheet.worksheet("roster")

    return roster.get_all_records()

def load_student(student_id: str):

    spreadsheet = get_spreadsheet()

    roster_ws = spreadsheet.worksheet("roster")
    scores_ws = spreadsheet.worksheet("exam_scores")
    attendance_ws = spreadsheet.worksheet("attendance")
    exams_ws = spreadsheet.worksheet("exam_schedule")

    roster_rows = roster_ws.get_all_records()
    score_rows = scores_ws.get_all_records()
    attendance_rows = attendance_ws.get_all_records()
    exam_rows = exams_ws.get_all_records()

    roster_record = next(
        row for row in roster_rows
        if row["student_id"] == student_id
    )

    student_scores = {
        row["subject"]: row["score"]
        for row in score_rows
        if row["student_id"] == student_id
    }

    student_attendance = [
        row["attendance_pct"]
        for row in attendance_rows
        if row["student_id"] == student_id
    ]

    avg_attendance = (
        sum(student_attendance) / len(student_attendance)
        if student_attendance else 0
    )

    upcoming_exams = [
        {
            "subject": row["subject"],
            "date": row["exam_date"]
        }
        for row in exam_rows
        if row["student_id"] == student_id
    ]

    return {
        "name": roster_record["name"],
        "student_id": student_id,
        "program": roster_record["program"],
        "cohort": roster_record["cohort"],
        "subjects": student_scores,
        "attendance": round(avg_attendance, 1),
        "upcoming_exams": upcoming_exams,
    }

def get_student_context(student: dict) -> str:

    low_scores = {
        subject: score
        for subject, score in student["subjects"].items()
        if score < 60
    }

    exams = ", ".join(
        f"{exam['subject']} on {exam['date']}"
        for exam in student["upcoming_exams"]
    )

    return f"""
STUDENT PROFILE:

- Name: {student['name']}
- Student ID: {student['student_id']}
- Program: {student['program']}
- Cohort: {student['cohort']}
- Attendance: {student['attendance']}%
- Subject Scores: {student['subjects']}
- Subjects Needing Attention: {low_scores if low_scores else 'None'}
- Upcoming Exams: {exams}
"""

STUDENT = load_student(STUDENT_ID)