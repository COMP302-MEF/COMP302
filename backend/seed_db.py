from database import SessionLocal
from models import User, Course, Activity, UserRole
from passlib.context import CryptContext

# Şifreleme ayarı (main.py ile aynı olmalı)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_data():
    db = SessionLocal()
    print("Veritabanı yeni sisteme göre tohumlanıyor...")
    
    try:
        # 1. Tabloları temizlemek istersen (Opsiyonel ama temiz başlangıç sağlar)
        # db.query(Activity).delete()
        # db.query(Course).delete()
        # db.query(User).delete()

        # 2. Eğitmen Oluştur (Berke)
        instructor_pwd = pwd_context.hash("berke123") # Örnek şifre
        me = User(
            email="berke@uni.edu.tr", 
            full_name="Berke", 
            role="instructor",
            hashed_password=instructor_pwd
        )
        db.add(me)
        db.commit()
        db.refresh(me)

        # 3. Öğrenci Oluştur (Test için)
        student_pwd = pwd_context.hash("ogrenci123")
        student = User(
            email="ogrenci@uni.edu.tr",
            full_name="Ali Ogrenci",
            role="student",
            hashed_password=student_pwd
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # 4. Kurs Oluştur (Berke Hoca'ya bağlı)
        new_course = Course(
            course_code="COMP302", 
            instructor_id=me.id
        )
        db.add(new_course)
        db.commit()
        db.refresh(new_course)

        # 5. Örnek Aktivite Ekle (Ali Ogrenci için)
        sample_act = Activity(
            user_id=student.id,
            course_id=new_course.id,
            activity_type="Coding",
            description="First setup and login test",
            duration_minutes=60
        )
        db.add(sample_act)
        db.commit()
        
        print("BAŞARILI: Güvenli kullanıcılar, kurs ve örnek aktivite oluşturuldu.")
        print(f"Eğitmen Giriş: berke@uni.edu.tr / berke123")
        print(f"Öğrenci Giriş: ogrenci@uni.edu.tr / ogrenci123")
        
    except Exception as e:
        print(f"HATA: Veri eklenemedi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()