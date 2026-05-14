from database import Base, engine, SessionLocal
from models import Activity, Course, Enrollment, ScoreLog, StudentProgress, User
import json


def to_json(value):
    return json.dumps(value, ensure_ascii=False)


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        instructor_a = User(name="Instructor A", email="hoca_a@test.com", password="123", role="instructor")
        instructor_b = User(name="Instructor B", email="hoca_b@test.com", password="123", role="instructor")
        student_1 = User(name="Student 1", email="ogr_1@test.com", password="123", role="student")
        student_2 = User(name="Student 2", email="ogr_2@test.com", password="123", role="student")
        db.add_all([instructor_a, instructor_b, student_1, student_2])
        db.commit()

        course_1 = Course(course_code="COMP302", course_name="Software Engineering", instructor_id=instructor_a.id)
        course_2 = Course(course_code="COMP400", course_name="Independent Study", instructor_id=instructor_b.id)
        db.add_all([course_1, course_2])
        db.commit()

        db.add(Enrollment(student_id=student_1.id, course_id=course_1.id))

        activity_text = (
            "A student studies for an exam by rereading the textbook many times. "
            "Another student studies by closing the book and trying to explain the ideas from memory, "
            "then checking mistakes. Which strategy is likely to support better long-term learning, and why?"
        )
        objectives = [
            "Explain that active retrieval practice improves long-term learning more than passive rereading.",
            "Explain that feedback after retrieval helps identify and correct misunderstandings.",
        ]
        db.add_all([
            Activity(
                course_id=course_1.id,
                activity_no=1,
                title="Retrieval Practice Demo",
                activity_text=activity_text,
                objectives=to_json(objectives),
                status="NOT_STARTED",
            ),
            Activity(
                course_id=course_1.id,
                activity_no=2,
                title="Spacing Effect Activity",
                activity_text="Compare studying in one long session with studying in shorter sessions across several days.",
                objectives=to_json(["Explain why spaced practice improves retention.", "Give an example of a spacing schedule."]),
                status="NOT_STARTED",
            ),
        ])
        db.commit()
        print("Demo database loaded successfully.")
        print("Instructor A: hoca_a@test.com / 123")
        print("Instructor B: hoca_b@test.com / 123")
        print("Student 1: ogr_1@test.com / 123")
        print("Student 2: ogr_2@test.com / 123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
