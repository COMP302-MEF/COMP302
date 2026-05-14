from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

SQLALCHEMY_DATABASE_URL = "sqlite:///./inclass.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELLER ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String) # 'student' veya 'instructor'

class ActivityType(Base):
    __tablename__ = "activity_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    multiplier = Column(Float, default=1.0)

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(String)
    activity_type = Column(String)
    duration_minutes = Column(Integer)
    description = Column(String)
    challenges = Column(String, nullable=True)     # US-J: Zorluklar
    learned_points = Column(String, nullable=True) # US-J: Öğrenilenler
    status = Column(String, default="Pending")

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- ENDPOINT'LER ---

@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.get("email")).first()
    if not user or user.password != data.get("password"):
        raise HTTPException(status_code=401, detail="Hatalı giriş")
    return {"id": user.id, "name": user.name, "role": user.role}

@app.get("/activity-types")
def get_types(db: Session = Depends(get_db)):
    return db.query(ActivityType).all()

@app.post("/activity-types")
def create_type(data: dict, db: Session = Depends(get_db)):
    new_type = ActivityType(name=data['name'], multiplier=float(data['multiplier']))
    db.add(new_type); db.commit()
    return {"msg": "OK"}

@app.post("/activities")
def create_activity(data: dict, db: Session = Depends(get_db)):
    new_act = Activity(
        user_id=data.get("user_id"),
        course_id=data.get("course_id"),
        activity_type=data.get("activity_type"),
        duration_minutes=data.get("duration_minutes"),
        description=data.get("description"),
        challenges=data.get("challenges"),
        learned_points=data.get("learned_points"),
        status="Pending"
    )
    db.add(new_act); db.commit(); return {"msg": "OK"}

@app.get("/users/{user_id}/activities")
def get_user_activities(user_id: int, db: Session = Depends(get_db)):
    return db.query(Activity).filter(Activity.user_id == user_id).all()

@app.get("/activities/pending")
def get_pending(db: Session = Depends(get_db)):
    return db.query(Activity).filter(Activity.status == "Pending").all()

@app.put("/activities/{id}/status")
def update_status(id: int, status: str, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == id).first()
    if act: act.status = status; db.commit(); return {"msg": "OK"}
    raise HTTPException(status_code=404)

@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role == "student").all()
    types = {t.name: t.multiplier for t in db.query(ActivityType).all()}
    res = []
    for u in users:
        acts = db.query(Activity).filter(Activity.user_id == u.id, Activity.status == "Approved").all()
        score = sum(a.duration_minutes * types.get(a.activity_type, 1.0) for a in acts)
        res.append({"name": u.name, "score": round(score, 1)})
    return sorted(res, key=lambda x: x["score"], reverse=True)

@app.delete("/reset-system")
def reset(db: Session = Depends(get_db)):
    db.query(Activity).delete(); db.commit(); return {"msg": "OK"}
    
    
# main.py içine ekle
@app.post("/register")
def register(data: dict, db: Session = Depends(get_db)):
    # Email kontrolü: Daha önce bu email alınmış mı?
    existing_user = db.query(User).filter(User.email == data.get("email")).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kullanımda.")
    
    new_user = User(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password"),
        role=data.get("role") # 'student' veya 'instructor'
    )
    db.add(new_user)
    db.commit()
    return {"msg": "Kayıt başarılı! Giriş yapabilirsiniz."}    