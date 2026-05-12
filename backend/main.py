from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel
from passlib.context import CryptContext
from models import User, Course, Activity, Enrollment  # <-- Enrollment ekle
from datetime import datetime # <-- Eğer kullanıyorsan ekle
from sqlalchemy import Column, Integer, String, Float, ForeignKey, func ,CASE# func eklendi
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Ayarları: Frontend'in Backend'e erişebilmesi için şart
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme aşamasında her şeye izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Pydantic Modeli (Frontend'den gelecek verinin kalıbı)
class ActivityCreate(BaseModel):
    user_id: int
    course_id: int
    activity_type: str
    description: str
    duration_minutes: int

@app.get("/")
def read_root():
    return {"message": "InClass Gamification API is Running!"}

# US-C: Kullanıcı Yetki Kontrolü
@app.get("/user/verify/{email}")
def verify_user_access(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return {
        "full_name": user.full_name,
        "role": user.role,
        "is_instructor": user.role == "instructor"
    }

# US-B: Aktivite Ekleme
@app.post("/activities/add")
def add_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    try:
        new_act = models.Activity(
            user_id=activity.user_id,
            course_id=activity.course_id,
            activity_type=activity.activity_type,
            description=activity.description,
            duration_minutes=activity.duration_minutes
        )
        db.add(new_act)
        db.commit()
        db.refresh(new_act)
        return {"message": "Aktivite başarıyla kaydedildi!", "activity_id": new_act.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# US-B: Aktiviteleri Listeleme
@app.get("/activities/user/{user_id}")
def get_user_activities(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Activity).filter(models.Activity.user_id == user_id).all()
# US-L: Puan Hesaplama Fonksiyonu
def calculate_score(activity_type: str, duration: int):
    multipliers = {
        "Coding": 2.0,
        "Reading": 1.0,
        "Meeting": 1.5,
        "Other": 0.5
    }
    # Eğer listede olmayan bir tip girilirse 'Other' katsayısını kullan
    multiplier = multipliers.get(activity_type, 0.5)
    return int(duration * multiplier)

# US-L: Liderlik Tablosu (Leaderboard) Endpoint'i
@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    # Kullanıcıları ve toplam puanlarını getir (Büyükten küçüğe sırala)
    # Şimdilik basitlik adına aktivitelerden anlık hesaplayalım
    users = db.query(models.User).all()
    leaderboard = []
    
    for user in users:
        # Bu kullanıcının tüm aktivitelerini bul
        activities = db.query(models.Activity).filter(models.Activity.user_id == user.id).all()
        # Aktiviteleri puanla ve topla
        total_p = sum(calculate_score(a.activity_type, a.duration_minutes) for a in activities)
        
        leaderboard.append({
            "full_name": user.full_name,
            "total_score": total_p
        })
    
    # Puanlara göre azalan sırada diz
    return sorted(leaderboard, key=lambda x: x["total_score"], reverse=True)

# Şifreleme ayarları
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    role: str

# US-A: Kayıt Olma Endpoint'i
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Email daha önce alınmış mı kontrol et
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu email zaten kayitli.")
    
    # Şifreyi hash'le ve kaydet
    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_pw,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "Kullanici basariyla olusturuldu!"}

class LoginRequest(BaseModel):
    email: str
    password: str

# US-A: Giriş Yapma Endpoint'i
@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1. Kullanıcıyı mail adresinden bul
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    
    # 2. Şifreyi doğrula (Gelen şifre vs Hashlenmiş şifre)
    if not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Hatalı şifre.")
    
    # 3. Başarılıysa kullanıcı bilgilerini dön
    return {
        "message": "Giriş başarılı!",
        "user_id": user.id,
        "full_name": user.full_name,
        "role": user.role
    }

# Enrollment Şeması (Pydantic)
class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int

@app.post("/enrollments/add")
def enroll_student(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    # Daha önce kayıt olmuş mu kontrolü
    db_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == enrollment.user_id,
        Enrollment.course_id == enrollment.course_id
    ).first()
    
    if db_enrollment:
        raise HTTPException(status_code=400, detail="Öğrenci bu derse zaten kayıtlı.")

    new_enrollment = Enrollment(user_id=enrollment.user_id, course_id=enrollment.course_id)
    db.add(new_enrollment)
    db.commit()
    return {"message": "Derse kayıt başarıyla tamamlandı!"}

@app.get("/users/{user_id}/courses")
def get_user_courses(user_id: int, db: Session = Depends(get_db)):
    # Enrollment tablosu üzerinden kullanıcının kayıtlı olduğu kursları çekiyoruz
    courses = db.query(Course).join(Enrollment).filter(Enrollment.user_id == user_id).all()
    return courses

@app.get("/instructor/{instructor_id}/dashboard")
def get_instructor_dashboard(instructor_id: int, db: Session = Depends(get_db)):
    # 1. Eğitmenin derslerini bul
    courses = db.query(Course).filter(Course.instructor_id == instructor_id).all()
    course_ids = [c.id for c in courses]

    if not course_ids:
        return []

    # 2. Bu derslerdeki öğrencileri ve toplam puanlarını getir
    # Aktivite puanlarını katsayılarıyla (Coding=2, Reading=1 vb.) hesaplayan gelişmiş sorgu
    stats = db.query(
        User.id,
        User.full_name,
        User.email,
        func.coalesce(func.sum(
            CASE(
                (Activity.activity_type == 'Coding', Activity.duration_minutes * 2.0),
                (Activity.activity_type == 'Meeting', Activity.duration_minutes * 1.5),
                (Activity.activity_type == 'Reading', Activity.duration_minutes * 1.0),
                else_=Activity.duration_minutes * 0.5
            )
        ), 0).label("total_score")
    ).join(Enrollment, User.id == Enrollment.user_id)\
     .outerjoin(Activity, (User.id == Activity.user_id) & (Activity.course_id == Enrollment.course_id))\
     .filter(Enrollment.course_id.in_(course_ids))\
     .group_by(User.id).all()

    # Veriyi frontend'in kolay okuyacağı bir listeye çeviriyoruz
    return [
        {"id": s.id, "name": s.full_name, "email": s.email, "score": s.total_score} 
        for s in stats
    ]