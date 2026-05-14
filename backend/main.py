from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
import datetime
import requests
import json

# --- VERİTABANI VE AYARLAR ---
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/inclass_db"
OPENROUTER_API_KEY = "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"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
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

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True)
    instructor_id = Column(Integer, ForeignKey("users.id"))

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    activity_text = Column(Text)
    objectives = Column(Text)
    status = Column(String, default="NOT_STARTED") # NOT_STARTED, ACTIVE, ENDED

class ScoreLog(Base):
    __tablename__ = "score_logs"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    activity_id = Column(Integer, ForeignKey("activities.id"))
    objective_index = Column(Integer)
    score = Column(Integer, default=1)
    timestamp = Column(String, default=lambda: datetime.datetime.now().isoformat())

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/register")
def register(data: dict, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.get("email")).first():
        raise HTTPException(status_code=400, detail="E-posta kullanımda.")
    new_user = User(name=data.get("name"), email=data.get("email"), password=data.get("password"), role=data.get("role"))
    db.add(new_user); db.commit(); db.refresh(new_user)
    return {"msg": "Kayıt başarılı!"}

@app.get("/courses")
def get_courses(user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    if user.role == "instructor":
        return db.query(Course).filter(Course.instructor_id == user.id).all()
    else:
        enrolls = db.query(Enrollment).filter(Enrollment.student_id == user.id).all()
        return db.query(Course).filter(Course.id.in_([e.course_id for e in enrolls])).all()

@app.get("/courses/{course_id}/activities")
def get_course_activities(course_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    return db.query(Activity).filter(Activity.course_id == course_id).all()

@app.put("/activities/{activity_id}")
def update_activity(activity_id: int, data: dict, user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user.role != "instructor": raise HTTPException(status_code=403)
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if "status" in data: act.status = data["status"]
    db.commit()
    return {"msg": "Güncellendi"}

@app.get("/activities/{activity_id}")
def get_activity(activity_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if user.role == "student":
        if act.status != "ACTIVE": raise HTTPException(status_code=403, detail="Aktif değil")
        return {"id": act.id, "title": act.title, "text": act.activity_text}
    return act

# --- YAPAY ZEKA VE PUANLAMA AKIŞI ---
@app.post("/activities/{activity_id}/chat")
def chat_with_tutor(activity_id: int, data: dict, user_id: int = Query(...), db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    user_msg = data.get("message", "")
    history = data.get("history", [])

    system_prompt = f"""You are a university tutor. Activity: {act.activity_text}. Objectives: {act.objectives}.
    RULES: 1. Ask ONE question. 2. No direct answers. 3. If objective met, give mini-lesson.
    RESPONSE FORMAT (JSON ONLY): {{"tutor_response": "...", "achieved_objective_index": 1 or null, "is_complete": bool}}"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_msg})

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "deepseek/deepseek-chat", "messages": messages, "response_format": {"type": "json_object"}}

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        llm_json = json.loads(res.json()["choices"][0]["message"]["content"])
        
        obj_idx = llm_json.get("achieved_objective_index")
        if obj_idx:
            exists = db.query(ScoreLog).filter(ScoreLog.student_id==user_id, ScoreLog.activity_id==activity_id, ScoreLog.objective_index==obj_idx).first()
            if not exists:
                db.add(ScoreLog(student_id=user_id, activity_id=activity_id, objective_index=obj_idx)); db.commit()
        
        return {"reply": llm_json["tutor_response"], "is_complete": llm_json["is_complete"]}
    except:
        raise HTTPException(status_code=500, detail="AI Hatası")

# --- DEMO KURULUMU ---
@app.post("/setup-demo")
def setup_demo(db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.email == "hoca_a@test.com").first(): return {"msg": "Zaten yüklü"}
        h_a = User(name="Instructor A", email="hoca_a@test.com", password="123", role="instructor")
        h_b = User(name="Instructor B", email="hoca_b@test.com", password="123", role="instructor")
        db.add_all([h_a, h_b]); db.commit(); db.refresh(h_a)
        
        s1 = User(name="Student 1", email="ogr_1@test.com", password="123", role="student")
        s2 = User(name="Student 2", email="ogr_2@test.com", password="123", role="student")
        db.add_all([s1, s2]); db.commit(); db.refresh(s1)
        
        c1 = Course(course_code="COMP 302", instructor_id=h_a.id)
        c2 = Course(course_code="COMP 400", instructor_id=h_b.id)
        db.add_all([c1, c2]); db.commit(); db.refresh(c1)
        
        db.add(Enrollment(student_id=s1.id, course_id=c1.id)); db.commit()
        
        txt = "A student studies by rereading... Another studies by active retrieval... Which is better?"
        objs = "1. Active retrieval is better.\n2. Feedback corrects mistakes."
        db.add(Activity(course_id=c1.id, title="Demo Act", activity_text=txt, objectives=objs)); db.commit()
        return {"msg": "Demo hazır!"}
    except Exception as e:
        db.rollback(); raise HTTPException(status_code=500, detail=str(e))