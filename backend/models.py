from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime  # <-- DateTime ekledik
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime  # <-- Bunu da eklemelisin (utcnow için)
import enum
from sqlalchemy import Enum as SQLEnum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String, default=UserRole.STUDENT)
    hashed_password = Column(String) # Şifreleri güvenli saklamak için

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True)
    instructor_id = Column(Integer, ForeignKey("users.id"))

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    # Hata aldığın yer burasıydı, 'user_id' olarak netleştirdik
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    activity_type = Column(String) # Örn: Coding, Reading
    description = Column(String)
    duration_minutes = Column(Integer)

class ScoreLog(Base):
    __tablename__ = "score_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_score = Column(Integer, default=0)
    
class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler (Opsiyonel ama rapor için iyi durur)
    user = relationship("User")
    course = relationship("Course")    