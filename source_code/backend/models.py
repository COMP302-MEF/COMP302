from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    JSON,
)

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # student / instructor

    created_at = Column(DateTime, default=datetime.utcnow)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, nullable=False)
    course_name = Column(String, nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    activity_no = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    activity_text = Column(Text, nullable=False)

    # Objectives JSON list olarak tutulacak:
    # [
    #   "Explain that active retrieval practice improves long-term learning...",
    #   "Explain that feedback after retrieval helps..."
    # ]
    objectives = Column(JSON, nullable=False)

    # NOT_STARTED / ACTIVE / ENDED
    status = Column(String, default="NOT_STARTED", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("course_id", "activity_no", name="uq_course_activity_no"),
    )


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)

    current_score = Column(Integer, default=0, nullable=False)

    # Kazanılmış objective indexleri:
    # örnek: [0, 1]
    achieved_objectives = Column(JSON, default=list, nullable=False)

    # Chat geçmişi:
    # [
    #   {"role": "user", "content": "..."},
    #   {"role": "assistant", "content": "..."}
    # ]
    chat_history = Column(JSON, default=list, nullable=False)

    is_complete = Column(Integer, default=0, nullable=False)  # 0 false, 1 true

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "activity_id",
            name="uq_student_activity_progress",
        ),
    )


class ScoreLog(Base):
    __tablename__ = "score_logs"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)

    objective_index = Column(Integer, nullable=True)

    # +1, 0, manual grade gibi değerler
    score_delta = Column(Integer, nullable=False)

    # Bu event sonrasında öğrencinin toplam skoru
    updated_score = Column(Integer, nullable=False)

    # AI_OBJECTIVE / MANUAL_GRADE / RESET
    event_type = Column(String, nullable=False)

    # SQLAlchemy'de "metadata" attribute adı özel olduğu için
    # Python tarafında event_metadata kullanıyoruz,
    # database kolon adı yine metadata olacak.
    event_metadata = Column("metadata", JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)