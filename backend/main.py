from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
import models
from models import User, Course, Activity, Enrollment
from pydantic import BaseModel
from passlib.context import CryptContext

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS AYARLARI (Frontend bağlantısı için şart)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Şifreleme ayarı (Yeni bcrypt uyumlu)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Modelleri
class LoginRequest(BaseModel):
    email: str
    password: str

class ActivityCreate(BaseModel):
    user_id: int
    course_id: int
    activity_type: str
    duration_minutes: int
    description: str

<<<<<<< HEAD
# --- 1. GİRİŞ VE KULLANICI İŞLEMLERİ ---
=======
# --- ENDPOINTS ---
>>>>>>> f45e20e389fd93cee310afc42c9e54e33217dd54

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=400, detail="E-posta veya şifre hatalı")
    
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role
    }

@app.get("/users/{user_id}/courses")
def get_user_courses(user_id: int, db: Session = Depends(get_db)):
    courses = db.query(Course).join(Enrollment).filter(Enrollment.user_id == user_id).all()
    return courses

<<<<<<< HEAD

# --- 2. ÖĞRENCİ İŞLEMLERİ (AKTİVİTE VE LİDERLİK) ---

@app.post("/activities/add")
def add_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    # Modeli oluştururken varsayılan olarak status="pending" (beklemede) atanacak
    new_act = Activity(**activity.dict())
    db.add(new_act)
    db.commit()
    return {"message": "Aktivite başarıyla eklendi, onay bekliyor."}

@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    # Sadece ONAYLANMIŞ (approved) aktivitelerin dakikalarını topla
    results = db.query(
        User.full_name,
        func.sum(Activity.duration_minutes).label("total_minutes")
    ).join(Activity).filter(Activity.status == 'approved').group_by(User.id).order_by(func.sum(Activity.duration_minutes).desc()).all()
    
    return [{"name": r[0], "score": r[1]} for r in results]


# --- 3. EĞİTMEN İŞLEMLERİ (DASHBOARD VE ONAYLAMA) ---

=======
@app.post("/activities/add")
def add_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    new_act = Activity(**activity.dict())
    db.add(new_act)
    db.commit()
    return {"message": "Aktivite başarıyla eklendi"}

@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    results = db.query(
        User.full_name,
        func.sum(Activity.duration_minutes).label("total_minutes")
    ).join(Activity).group_by(User.id).order_by(func.sum(Activity.duration_minutes).desc()).all()
    return [{"name": r[0], "score": r[1]} for r in results]

>>>>>>> f45e20e389fd93cee310afc42c9e54e33217dd54
@app.get("/instructor/{instructor_id}/dashboard")
def get_instructor_dashboard(instructor_id: int, db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.instructor_id == instructor_id).all()
    course_ids = [c.id for c in courses]

    if not course_ids: return []

<<<<<<< HEAD
    # Eğitmenin derslerindeki öğrencileri listele ve SADECE ONAYLI aktivitelerin katsayılı puanlarını topla
=======
>>>>>>> f45e20e389fd93cee310afc42c9e54e33217dd54
    stats = db.query(
        User.id,
        User.full_name,
        User.email,
        func.coalesce(func.sum(
            case(
                (Activity.activity_type == 'Coding', Activity.duration_minutes * 2.0),
                (Activity.activity_type == 'Meeting', Activity.duration_minutes * 1.5),
                (Activity.activity_type == 'Reading', Activity.duration_minutes * 1.0),
                else_=Activity.duration_minutes * 0.5
            )
        ), 0).label("total_score")
    ).join(Enrollment, User.id == Enrollment.user_id)\
<<<<<<< HEAD
     .outerjoin(Activity, (User.id == Activity.user_id) & (Activity.course_id == Enrollment.course_id) & (Activity.status == 'approved'))\
     .filter(Enrollment.course_id.in_(course_ids))\
     .group_by(User.id).all()

    return [{"id": s.id, "name": s.full_name, "email": s.email, "score": s.total_score} for s in stats]

@app.get("/instructor/{instructor_id}/pending_activities")
def get_pending_activities(instructor_id: int, db: Session = Depends(get_db)):
    # Eğitmenin derslerindeki onay bekleyen (pending) aktiviteleri getir
    courses = db.query(Course).filter(Course.instructor_id == instructor_id).all()
    course_ids = [c.id for c in courses]
    
    if not course_ids: return []

    pending = db.query(Activity, User.full_name, Course.course_code)\
                .join(User, Activity.user_id == User.id)\
                .join(Course, Activity.course_id == Course.id)\
                .filter(Activity.course_id.in_(course_ids), Activity.status == 'pending').all()
    
    return [
        {
            "activity_id": act.Activity.id,
            "student_name": act.full_name,
            "course": act.course_code,
            "type": act.Activity.activity_type,
            "duration": act.Activity.duration_minutes,
            "description": act.Activity.description
        } for act in pending
    ]

@app.post("/activities/{activity_id}/approve")
def approve_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if activity:
        activity.status = 'approved'
        db.commit()
        return {"message": "Aktivite onaylandı"}
    raise HTTPException(status_code=404, detail="Aktivite bulunamadı")

@app.post("/activities/{activity_id}/reject")
def reject_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if activity:
        activity.status = 'rejected'
        db.commit()
        return {"message": "Aktivite reddedildi"}
    raise HTTPException(status_code=404, detail="Aktivite bulunamadı")
=======
     .outerjoin(Activity, (User.id == Activity.user_id) & (Activity.course_id == Enrollment.course_id))\
     .filter(Enrollment.course_id.in_(course_ids))\
     .group_by(User.id).all()

    return [{"id": s.id, "name": s.full_name, "email": s.email, "score": s.total_score} for s in stats]
>>>>>>> f45e20e389fd93cee310afc42c9e54e33217dd54
