from database import engine, Base
import models # models.py dosyasının aynı klasörde olduğundan emin ol

print("Veritabanı bağlantısı kuruluyor ve tablolar oluşturuluyor...")

try:
    # database.py içindeki engine'i kullanarak tabloları oluşturur
    Base.metadata.create_all(bind=engine)
    print("TEBRİKLER: Tablolar PostgreSQL içinde başarıyla oluşturuldu!")
except Exception as e:
    print(f"HATA: Veritabanına bağlanılamadı. Şifreni veya veritabanı adını kontrol et.")
    print(f"Hata mesajı: {e}")