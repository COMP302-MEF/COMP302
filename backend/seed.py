from main import SessionLocal, User, Base, engine
# Not: Eğer main.py içinde 'Course' modeli yoksa önce aşağıya bak!

db = SessionLocal()

try:
    # Veritabanını temizle
    db.query(User).delete()
    # db.query(Course).delete() # Eğer model varsa bunu da ekle
    
    # Kullanıcılar
    db.add(User(name="Berke Hoca", email="berke@uni.edu.tr", password="123", role="instructor"))
    db.add(User(name="Ali Öğrenci", email="ogrenci@uni.edu.tr", password="123", role="student"))
    
    # Buraya manuel ders ID'leri veya ders objeleri ekleyebiliriz
    # Şimdilik en hızlı çözüm frontend'e sabit dersler koymaktır 
    # ama backend'den gelsin istiyorsan devam edelim.
    
    db.commit()
    print("✅ Kullanıcılar hazır!")
finally:
    db.close()