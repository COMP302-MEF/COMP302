import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # student / instructor
    auth_token = Column(String, unique=True, index=True, nullable=True)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, nullable=False)
    course_name = Column(String, nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_student_course"),)


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    activity_no = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    activity_text = Column(Text, nullable=False)
    objectives = Column(Text, nullable=False)  # JSON list string
    status = Column(String, default="NOT_STARTED", nullable=False)  # NOT_STARTED / ACTIVE / ENDED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (UniqueConstraint("course_id", "activity_no", name="uq_course_activity_no"),)


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    covered_objectives = Column(Text, default="[]", nullable=False)  # JSON list of 1-based objective numbers
    total_score = Column(Integer, default=0, nullable=False)
    chat_history = Column(Text, default="[]", nullable=False)  # JSON list
    is_complete = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (UniqueConstraint("student_id", "activity_id", name="uq_student_activity_progress"),)


class ScoreLog(Base):
    __tablename__ = "score_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    objective_index = Column(Integer, nullable=True)  # 1-based, null for manual/reset events
    score_delta = Column(Integer, nullable=False)
    total_score_after = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)  # objective_earned / duplicate_objective / manual_grade / reset
    metadata_json = Column(Text, default="{}", nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
