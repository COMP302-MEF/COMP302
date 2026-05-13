from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
<<<<<<< HEAD
from datetime import datetime # Import şeklini düzelttik
=======
import datetime
>>>>>>> f45e20e389fd93cee310afc42c9e54e33217dd54

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String) # "student" veya "instructor"

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True)
    course_name = Column(String)
    instructor_id = Column(Integer, ForeignKey("users.id"))

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    activity_type = Column(String) # Coding, Reading, Meeting
    duration_minutes = Column(Integer)
    description = Column(String)
<<<<<<< HEAD
    
    # datetime.datetime.utcnow yerine sadece datetime.utcnow yaptık
    timestamp = Column(DateTime, default=datetime.utcnow) 
    
    status = Column(String, default="pending") # Eğitmen onayı için yeni durum sütunu
=======
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
>>>>>>> f45e20e389fd93cee310afc42c9e54e33217dd54
