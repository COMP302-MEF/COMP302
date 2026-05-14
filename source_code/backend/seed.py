from sqlalchemy import text

from database import Base, engine, SessionLocal
from models import User, Course, Enrollment, Activity


def reset_database():
    print("Eski tablolar temizleniyor...")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Yeni tablolar oluşturuldu.")


def seed_demo_data():
    db = SessionLocal()

    try:
        print("Demo verileri ekleniyor...")

        # -------------------------
        # 1. Instructors
        # -------------------------
        instructor_a = User(
            name="Instructor A",
            email="hoca_a@test.com",
            password="123",
            role="instructor",
        )

        instructor_b = User(
            name="Instructor B",
            email="hoca_b@test.com",
            password="123",
            role="instructor",
        )

        db.add_all([instructor_a, instructor_b])
        db.commit()
        db.refresh(instructor_a)
        db.refresh(instructor_b)

        # -------------------------
        # 2. Students
        # -------------------------
        student_1 = User(
            name="Student 1",
            email="ogr_1@test.com",
            password="123",
            role="student",
        )

        student_2 = User(
            name="Student 2",
            email="ogr_2@test.com",
            password="123",
            role="student",
        )

        db.add_all([student_1, student_2])
        db.commit()
        db.refresh(student_1)
        db.refresh(student_2)

        # -------------------------
        # 3. Courses
        # -------------------------
        course_1 = Course(
            course_code="COMP302",
            course_name="Software Engineering",
            instructor_id=instructor_a.id,
        )

        course_2 = Course(
            course_code="COMP400",
            course_name="Senior Project",
            instructor_id=instructor_b.id,
        )

        db.add_all([course_1, course_2])
        db.commit()
        db.refresh(course_1)
        db.refresh(course_2)

        # -------------------------
        # 4. Enrollment
        # Student 1 Course 1'e kayıtlı.
        # Student 2 Course 1'e kayıtlı değil.
        # -------------------------
        enrollment_1 = Enrollment(
            student_id=student_1.id,
            course_id=course_1.id,
        )

        db.add(enrollment_1)
        db.commit()

        # -------------------------
        # 5. Activities for Course 1
        # -------------------------
        activity_1_text = (
            "A student studies for an exam by rereading the textbook many times. "
            "Another student studies by closing the book and trying to explain "
            "the ideas from memory, then checking mistakes. Which strategy is "
            "likely to support better long-term learning, and why?"
        )

        activity_1_objectives = [
            "Explain that active retrieval practice improves long-term learning more than passive rereading.",
            "Explain that feedback after retrieval helps identify and correct misunderstandings.",
        ]

        activity_1 = Activity(
            course_id=course_1.id,
            activity_no=1,
            title="Retrieval Practice Demo",
            activity_text=activity_1_text,
            objectives=activity_1_objectives,
            status="NOT_STARTED",
        )

        activity_2 = Activity(
            course_id=course_1.id,
            activity_no=2,
            title="Spacing Effect Activity",
            activity_text=(
                "A student studies all material in one long session the night before "
                "an exam. Another student studies the same material in shorter sessions "
                "spread across several days. Which approach is likely to improve long-term retention?"
            ),
            objectives=[
                "Explain that spaced practice supports long-term retention better than cramming.",
                "Explain that repeated review over time strengthens memory.",
            ],
            status="NOT_STARTED",
        )

        db.add_all([activity_1, activity_2])
        db.commit()

        print("Demo verileri başarıyla yüklendi.")
        print("")
        print("Demo hesapları:")
        print("Instructor A: hoca_a@test.com / 123")
        print("Instructor B: hoca_b@test.com / 123")
        print("Student 1: ogr_1@test.com / 123")
        print("Student 2: ogr_2@test.com / 123")
        print("")
        print("Course 1: COMP302 - Instructor A")
        print("Course 2: COMP400 - Instructor B")
        print("Student 1 COMP302'ye kayıtlı.")
        print("Student 2 COMP302'ye kayıtlı değil.")

    except Exception as e:
        db.rollback()
        print("Seed sırasında hata oluştu:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
    seed_demo_data()