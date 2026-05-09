from database import SessionLocal
from models import User, Course, UserRole

def seed_data():
    db = SessionLocal()
    print("Örnek veriler ekleniyor...")
    
    try:
        # 1. Kendini Eğitmen olarak ekle
        me = User(
            email="berke@uni.edu.tr", 
            full_name="Berke", 
            role=UserRole.INSTRUCTOR
        )
        db.add(me)
        db.commit()
        db.refresh(me)

        # 2. Bir test kursu oluştur ve kendine bağla
        new_course = Course(
            course_code="COMP302", 
            instructor_id=me.id
        )
        db.add(new_course)
        db.commit()
        
        print(f"BAŞARILI: {me.full_name} eğitmen olarak eklendi ve COMP302 kursu oluşturuldu.")
        
    except Exception as e:
        print(f"HATA: Veri eklenemedi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()