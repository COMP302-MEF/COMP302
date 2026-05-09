from database import engine, Base
import models

def create_tables():
    print("Veritabanı tabloları oluşturuluyor...")
    try:
        # models.py içindeki her şeyi veritabanına fiziksel tablo olarak basar
        Base.metadata.create_all(bind=engine)
        print("BAŞARILI: Tablolar veritabanında oluşturuldu!")
    except Exception as e:
        print(f"HATA OLUŞTU: {e}")

if __name__ == "__main__":
    create_tables()