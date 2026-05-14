from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
# Float ve Boolean gibi eksik olabilecek tipleri ekledik
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean

SQLALCHEMY_DATABASE_URL = "sqlite:///./inclass.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(String)
    activity_type = Column(String)
    duration_minutes = Column(Integer)
    description = Column(String)
    status = Column(String, default="Pending")

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.get("email")).first()
    if not user or user.password != data.get("password"):
        raise HTTPException(status_code=401, detail="Hatalı giriş")
    return {"id": user.id, "name": user.name, "role": user.role}

@app.post("/activities")
def create_activity(data: dict, db: Session = Depends(get_db)):
    new_act = Activity(user_id=data.get("user_id"), course_id=data.get("course_id"),
                       activity_type=data.get("activity_type"), duration_minutes=data.get("duration_minutes"),
                       description=data.get("description"), status="Pending")
    db.add(new_act); db.commit(); return {"msg": "OK"}

@app.get("/users/{user_id}/activities")
def get_user_activities(user_id: int, db: Session = Depends(get_db)):
    return db.query(Activity).filter(Activity.user_id == user_id).all()

@app.put("/activities/{id}")
def update_activity(id: int, data: dict, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == id).first()
    if act and act.status.lower() == "pending":
        act.duration_minutes = data.get("duration_minutes", act.duration_minutes)
        act.description = data.get("description", act.description)
        db.commit(); return {"msg": "OK"}
    raise HTTPException(status_code=400, detail="Hata")

@app.get("/activities/pending")
def get_pending(db: Session = Depends(get_db)):
    return db.query(Activity).filter(Activity.status.ilike("pending")).all()

@app.put("/activities/{id}/status")
def update_status(id: int, status: str, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == id).first()
    if act: act.status = status; db.commit(); return {"msg": "OK"}
    raise HTTPException(status_code=404)

@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role == "student").all()
    res = []
    for u in users:
        score = sum(a.duration_minutes * (2.0 if a.activity_type=="Coding" else 1.0) 
                    for a in db.query(Activity).filter(Activity.user_id==u.id, Activity.status=="Approved").all())
        res.append({"name": u.name, "score": score})
    return sorted(res, key=lambda x: x["score"], reverse=True)

@app.delete("/reset-system")
def reset(db: Session = Depends(get_db)):
    db.query(Activity).delete(); db.commit(); return {"msg": "OK"}

# --- ENDPOINT'LER ---

# --- YENİ MODEL: Aktivite Türleri (US-F) ---
class ActivityType(Base):
    __tablename__ = "activity_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True) # Örn: 'Bug Fixing'
    multiplier = Column(Float)         # Örn: 1.5

Base.metadata.create_all(bind=engine)

# Mevcut kategorileri listele (Öğrenci seçim kutusu için)
@app.get("/activity-types")
def get_types(db: Session = Depends(get_db)):
    return db.query(ActivityType).all()

# Yeni kategori ekle (Hoca paneli için)
@app.post("/activity-types")
def create_type(data: dict, db: Session = Depends(get_db)):
    # Hata önleme: Aynı isimde kategori varsa ekleme
    existing = db.query(ActivityType).filter(ActivityType.name == data['name']).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu kategori zaten var.")
    
    new_type = ActivityType(name=data['name'], multiplier=float(data['multiplier']))
    db.add(new_type)
    db.commit()
    return {"msg": "Kategori başarıyla eklendi!"}

class Activity(Base):