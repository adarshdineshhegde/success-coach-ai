# Mock student record — in later phases this comes from Google Sheets
STUDENT = {
    "name": "Ravi Kumar",
    "student_id": "S1042",
    "subjects": {
        "Python": 72,
        "Web Dev": 58,       # flagged — below 60
        "DSA": 65,
        "SQL": 80,
    },
    "attendance": 67,        # flagged — below 75%
    "upcoming_exams": [
        {"subject": "Web Dev", "date": "2025-06-25"},
        {"subject": "DSA",     "date": "2025-07-02"},
    ],
    "growth_cycle": "GC-4",
    "growth_cycle_progress": 45,
}

def get_student_context(student: dict) -> str:
    """Convert student dict to a clean string for injection into the prompt."""
    low_scores = {s: v for s, v in student["subjects"].items() if v < 60}
    exams = ", ".join(
        f"{e['subject']} on {e['date']}" for e in student["upcoming_exams"]
    )
    context = f"""
STUDENT PROFILE:
- Name: {student['name']}
- Current Growth Cycle: {student['growth_cycle']} ({student['growth_cycle_progress']}% complete)
- Attendance: {student['attendance']}% {"⚠ BELOW 75%" if student['attendance'] < 75 else ""}
- Subject scores: {student['subjects']}
- Subjects needing attention (below 60): {low_scores if low_scores else "None"}
- Upcoming exams: {exams}
"""
    return context

#Here , thhis function converts the dict data of a student into a string format that can be easily injected into the prompt for the AI model. It highlights key information such as low scores, attendance, and upcoming exams, which can help the AI provide more personalized and actionable advice to the student.