from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel

app = FastAPI()

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