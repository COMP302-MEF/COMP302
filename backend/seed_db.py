from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# --- 1. ZORUNLU TEMİZLİK (HAYALET TABLOLARI SİL) ---
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS score_logs CASCADE;"))
    conn.commit()

# --- 2. NORMAL SIFIRLAMA VE KURULUM ---
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=True)
db = SessionLocal()

def seed():
    # 1. Kullanıcılar
    inst_pwd = pwd_context.hash("berke123")
    std_pwd = pwd_context.hash("ogrenci123")

    instructor = models.User(full_name="Berke Hoca", email="berke@uni.edu.tr", password=inst_pwd, role="instructor")
    student = models.User(full_name="Ali Ogrenci", email="ogrenci@uni.edu.tr", password=std_pwd, role="student")
    
    db.add(instructor)
    db.add(student)
    db.commit()

    # 2. Ders
    course = models.Course(course_code="COMP302", course_name="Software Engineering", instructor_id=instructor.id)
    db.add(course)
    db.commit()

    # 3. Kayıt (Enrollment)
    enroll = models.Enrollment(user_id=student.id, course_id=course.id)
    db.add(enroll)
    db.commit()

    print("BAŞARILI: Hayalet tablolar silindi ve veritabanı pırıl pırıl kuruldu!")

if __name__ == "__main__":
    seed()