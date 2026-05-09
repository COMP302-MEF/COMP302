from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel
app = FastAPI()

# US-C: Kullanıcının Rolünü ve Yetkisini Kontrol Etme
@app.get("/user/verify/{email}")
def verify_user_access(email: str, db: Session = Depends(get_db)):
    # Veritabanında kullanıcıyı bul
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # Rol kontrolü ve kurs eşleştirme
    response = {
        "full_name": user.full_name,
        "role": user.role,
        "is_instructor": user.role == "instructor"
    }

    # Eğer eğitmense, yönettiği kursları getir
    if user.role == "instructor":
        courses = db.query(models.Course).filter(models.Course.instructor_id == user.id).all()
        response["managed_courses"] = [c.course_code for c in courses]
        response["access_level"] = "Full (Course Management)"
    else:
        response["access_level"] = "Limited (Student View)"
        
    return response
# Aktivite eklemek için gerekli veri yapısı
class ActivityCreate(BaseModel):
    user_id: int
    course_id: int
    activity_type: str  # Örn: "Coding", "Watching", "Reading"
    description: str
    duration_minutes: int

# US-B: Yeni Aktivite Kaydetme API'ı
@app.post("/activities/add")
def add_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
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

# US-B: Bir kullanıcının tüm aktivitelerini listeleme
@app.get("/activities/user/{user_id}")
def get_user_activities(user_id: int, db: Session = Depends(get_db)):
    activities = db.query(models.Activity).filter(models.Activity.user_id == user_id).all()
    return activities