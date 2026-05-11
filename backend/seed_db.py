from database import SessionLocal, engine, Base
from models import User, Course, Activity, Enrollment # Enrollment eklendi
from passlib.context import CryptContext

# Şifreleme ayarı
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_data():
    # 1. Önce Tabloları Sıfırla (Temiz başlangıç ve yeni tabloların oluşması için)
    print("Eski tablolar siliniyor...")
    Base.metadata.drop_all(bind=engine)
    
    print("Tablolar yeniden oluşturuluyor (Enrollment dahil)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    print("Veritabanı yeni sisteme göre tohumlanıyor...")
    
    try:
        # 2. Eğitmen Oluştur (Berke)
        instructor_pwd = pwd_context.hash("berke123")
        me = User(
            email="berke@uni.edu.tr", 
            full_name="Berke", 
            role="instructor",
            hashed_password=instructor_pwd
        )
        db.add(me)
        db.commit()
        db.refresh(me)

        # 3. Öğrenci Oluştur
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

        # 5. YENİ: Öğrenciyi Derse Kaydet (Enrollment - US-E)
        enrollment = Enrollment(
            user_id=student.id,
            course_id=new_course.id
        )
        db.add(enrollment)
        db.commit()

        # 6. Örnek Aktivite Ekle
        sample_act = Activity(
            user_id=student.id,
            course_id=new_course.id,
            activity_type="Coding",
            description="System integration test",
            duration_minutes=60
        )
        db.add(sample_act)
        db.commit()
        
        print("-" * 30)
        print("BAŞARILI: Veritabanı sıfırlandı ve US-E (Enrollment) dahil edildi.")
        print(f"Eğitmen: berke@uni.edu.tr / berke123")
        print(f"Öğrenci: ogrenci@uni.edu.tr / ogrenci123")
        print("-" * 30)
        
    except Exception as e:
        print(f"HATA: Veri eklenemedi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()