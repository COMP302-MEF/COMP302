from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime
import enum

# US-C: Rol tanımlamaları
class UserRole(str, enum.Enum):
    INSTRUCTOR = "instructor"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String) # US-C: 'instructor' veya 'student'

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True)
    instructor_id = Column(Integer, ForeignKey("users.id"))

class ActivityStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    status = Column(String, default="NOT_STARTED") # US-H için kritik
    content = Column(Text) # Aktivite metni

class ScoreLog(Base):
    __tablename__ = "score_logs"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    activity_id = Column(Integer, ForeignKey("activities.id"))
    objective_description = Column(String) # US-K: Hangi kazanım
    score = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)