import os
import json
import time
import hmac
import base64
import hashlib
from pathlib import Path
from typing import Optional, Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db
from models import (
    User,
    Course,
    Enrollment,
    Activity,
    StudentProgress,
    ScoreLog,
)


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
AUTH_SECRET = os.getenv("AUTH_SECRET", "change-this-secret")
TOKEN_EXPIRE_SECONDS = 60 * 60 * 8


app = FastAPI(title="InClass Platform API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBearer()


# ---------------------------------------------------------
# TOKEN HELPERS
# ---------------------------------------------------------

def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }

    payload_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = _b64_encode(payload_json)

    signature = hmac.new(
        AUTH_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return f"{payload_b64}.{_b64_encode(signature)}"


def decode_token(token: str) -> dict:
    try:
        payload_b64, signature_b64 = token.split(".", 1)

        expected_signature = hmac.new(
            AUTH_SECRET.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        actual_signature = _b64_decode(signature_b64)

        if not hmac.compare_digest(expected_signature, actual_signature):
            raise ValueError("Invalid signature")

        payload = json.loads(_b64_decode(payload_b64).decode("utf-8"))

        if payload.get("exp", 0) < int(time.time()):
            raise ValueError("Token expired")

        return payload

    except Exception:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token.")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    user = db.query(User).filter(User.id == payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı.")

    return user


# ---------------------------------------------------------
# GENERAL HELPERS
# ---------------------------------------------------------

def require_role(user: User, role: str):
    if user.role != role:
        raise HTTPException(status_code=403, detail=f"Bu işlem sadece {role} rolü içindir.")


def get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Ders bulunamadı.")
    return course


def get_activity_or_404(db: Session, activity_id: int) -> Activity:
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Aktivite bulunamadı.")
    return activity


def ensure_instructor_owns_course(db: Session, instructor: User, course_id: int) -> Course:
    require_role(instructor, "instructor")

    course = get_course_or_404(db, course_id)

    if course.instructor_id != instructor.id:
        raise HTTPException(
            status_code=403,
            detail="Bu ders için instructor yetkiniz yok.",
        )

    return course


def ensure_instructor_owns_activity(db: Session, instructor: User, activity: Activity) -> Course:
    return ensure_instructor_owns_course(db, instructor, activity.course_id)


def ensure_student_enrolled(db: Session, student: User, course_id: int):
    require_role(student, "student")

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student.id,
            Enrollment.course_id == course_id,
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="Bu derse kayıtlı değilsiniz.",
        )


def normalize_objectives(value: Any) -> list[str]:
    if isinstance(value, list):
        objectives = [str(item).strip() for item in value if str(item).strip()]
    elif isinstance(value, str):
        objectives = []
        for line in value.splitlines():
            clean = line.strip()
            if not clean:
                continue

            if ". " in clean:
                clean = clean.split(". ", 1)[1].strip()

            objectives.append(clean)
    else:
        objectives = []

    if not objectives:
        raise HTTPException(
            status_code=400,
            detail="En az bir learning objective girilmelidir.",
        )

    return objectives


def serialize_activity_for_instructor(activity: Activity) -> dict:
    return {
        "id": activity.id,
        "course_id": activity.course_id,
        "activity_no": activity.activity_no,
        "title": activity.title,
        "activity_text": activity.activity_text,
        "objectives": activity.objectives,
        "status": activity.status,
    }


def serialize_activity_for_student_list(activity: Activity) -> dict:
    return {
        "id": activity.id,
        "course_id": activity.course_id,
        "activity_no": activity.activity_no,
        "title": activity.title,
        "status": activity.status,
    }


def get_or_create_progress(
    db: Session,
    student: User,
    activity: Activity,
) -> StudentProgress:
    progress = (
        db.query(StudentProgress)
        .filter(
            StudentProgress.student_id == student.id,
            StudentProgress.activity_id == activity.id,
        )
        .first()
    )

    if progress:
        return progress

    progress = StudentProgress(
        student_id=student.id,
        course_id=activity.course_id,
        activity_id=activity.id,
        current_score=0,
        achieved_objectives=[],
        chat_history=[],
        is_complete=0,
    )

    db.add(progress)
    db.commit()
    db.refresh(progress)

    return progress


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "app": "InClass Platform API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ---------------------------------------------------------
# AUTH
# ---------------------------------------------------------

@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="E-posta ve şifre zorunludur.")

    user = db.query(User).filter(User.email == email).first()

    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Hatalı e-posta veya şifre.")

    token = create_token(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "token": token,
    }


@app.post("/register")
def register(data: dict, db: Session = Depends(get_db)):
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not name or not email or not password or not role:
        raise HTTPException(status_code=400, detail="Tüm alanlar zorunludur.")

    if role not in ["student", "instructor"]:
        raise HTTPException(status_code=400, detail="Role student veya instructor olmalıdır.")

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kullanımda.")

    new_user = User(
        name=name,
        email=email,
        password=password,
        role=role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "Kayıt başarılı."}


@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }


# ---------------------------------------------------------
# COURSES
# ---------------------------------------------------------

@app.get("/courses")
def get_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "instructor":
        courses = (
            db.query(Course)
            .filter(Course.instructor_id == current_user.id)
            .order_by(Course.id.asc())
            .all()
        )

    elif current_user.role == "student":
        enrollments = (
            db.query(Enrollment)
            .filter(Enrollment.student_id == current_user.id)
            .all()
        )

        course_ids = [e.course_id for e in enrollments]

        if not course_ids:
            return []

        courses = (
            db.query(Course)
            .filter(Course.id.in_(course_ids))
            .order_by(Course.id.asc())
            .all()
        )

    else:
        raise HTTPException(status_code=403, detail="Geçersiz rol.")

    return [
        {
            "id": c.id,
            "course_code": c.course_code,
            "course_name": c.course_name,
            "instructor_id": c.instructor_id,
        }
        for c in courses
    ]


# ---------------------------------------------------------
# ACTIVITIES
# ---------------------------------------------------------

@app.get("/courses/{course_id}/activities")
def list_course_activities(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "instructor":
        ensure_instructor_owns_course(db, current_user, course_id)
        include_full = True

    elif current_user.role == "student":
        ensure_student_enrolled(db, current_user, course_id)
        include_full = False

    else:
        raise HTTPException(status_code=403, detail="Geçersiz rol.")

    activities = (
        db.query(Activity)
        .filter(Activity.course_id == course_id)
        .order_by(Activity.activity_no.asc())
        .all()
    )

    if include_full:
        return [serialize_activity_for_instructor(a) for a in activities]

    return [serialize_activity_for_student_list(a) for a in activities]


@app.post("/courses/{course_id}/activities")
def create_activity(
    course_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_instructor_owns_course(db, current_user, course_id)

    activity_no = data.get("activity_no")
    title = data.get("title")
    activity_text = data.get("activity_text")
    objectives = normalize_objectives(data.get("objectives"))

    if activity_no is None or not title or not activity_text:
        raise HTTPException(
            status_code=400,
            detail="activity_no, title, activity_text ve objectives zorunludur.",
        )

    duplicate = (
        db.query(Activity)
        .filter(
            Activity.course_id == course_id,
            Activity.activity_no == activity_no,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Bu course içinde aynı activity_no zaten var.",
        )

    activity = Activity(
        course_id=course_id,
        activity_no=activity_no,
        title=title,
        activity_text=activity_text,
        objectives=objectives,
        status="NOT_STARTED",
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return serialize_activity_for_instructor(activity)


@app.get("/activities/{activity_id}")
def get_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)

    if current_user.role == "instructor":
        ensure_instructor_owns_activity(db, current_user, activity)
        return serialize_activity_for_instructor(activity)

    if current_user.role == "student":
        ensure_student_enrolled(db, current_user, activity.course_id)

        if activity.status != "ACTIVE":
            raise HTTPException(
                status_code=403,
                detail="Aktivite şu anda ACTIVE değil.",
            )

        return {
            "id": activity.id,
            "course_id": activity.course_id,
            "activity_no": activity.activity_no,
            "title": activity.title,
            "text": activity.activity_text,
            "status": activity.status,
        }

    raise HTTPException(status_code=403, detail="Geçersiz rol.")


@app.patch("/activities/{activity_id}")
def update_activity(
    activity_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    ensure_instructor_owns_activity(db, current_user, activity)

    allowed_fields = {"activity_no", "title", "activity_text", "objectives"}
    requested_fields = set(data.keys())

    if not requested_fields:
        raise HTTPException(status_code=400, detail="Boş update isteği gönderilemez.")

    invalid_fields = requested_fields - allowed_fields

    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Bu alanlar güncellenemez: {list(invalid_fields)}",
        )

    if activity.status == "ENDED":
        raise HTTPException(
            status_code=403,
            detail="ENDED aktivite güncellenemez.",
        )

    if "activity_no" in data:
        new_no = data["activity_no"]

        duplicate = (
            db.query(Activity)
            .filter(
                Activity.course_id == activity.course_id,
                Activity.activity_no == new_no,
                Activity.id != activity.id,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Bu course içinde aynı activity_no zaten var.",
            )

        activity.activity_no = new_no

    if "title" in data:
        if not data["title"]:
            raise HTTPException(status_code=400, detail="Title boş olamaz.")
        activity.title = data["title"]

    if "activity_text" in data:
        if not data["activity_text"]:
            raise HTTPException(status_code=400, detail="Activity text boş olamaz.")
        activity.activity_text = data["activity_text"]

    if "objectives" in data:
        activity.objectives = normalize_objectives(data["objectives"])

    db.commit()
    db.refresh(activity)

    return serialize_activity_for_instructor(activity)


@app.post("/activities/{activity_id}/start")
def start_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    ensure_instructor_owns_activity(db, current_user, activity)

    activity.status = "ACTIVE"
    db.commit()
    db.refresh(activity)

    return {"msg": "Aktivite ACTIVE yapıldı.", "activity": serialize_activity_for_instructor(activity)}


@app.post("/activities/{activity_id}/end")
def end_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    ensure_instructor_owns_activity(db, current_user, activity)

    activity.status = "ENDED"
    db.commit()
    db.refresh(activity)

    return {"msg": "Aktivite ENDED yapıldı.", "activity": serialize_activity_for_instructor(activity)}


@app.post("/activities/{activity_id}/reset")
def reset_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    ensure_instructor_owns_activity(db, current_user, activity)

    deleted_logs = (
        db.query(ScoreLog)
        .filter(ScoreLog.activity_id == activity.id)
        .delete()
    )

    deleted_progress = (
        db.query(StudentProgress)
        .filter(StudentProgress.activity_id == activity.id)
        .delete()
    )

    activity.status = "ENDED"

    db.commit()

    return {
        "msg": "Aktivite resetlendi ve ENDED durumuna alındı.",
        "deleted_score_logs": deleted_logs,
        "deleted_student_progress": deleted_progress,
        "status": activity.status,
    }


# ---------------------------------------------------------
# AI CHAT AND SCORING
# ---------------------------------------------------------

def parse_ai_json(content: str) -> dict:
    try:
        return json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end <= start:
            raise ValueError(f"AI JSON döndürmedi: {content}")

        return json.loads(content[start:end])


def call_ai_tutor(
    activity: Activity,
    progress: StudentProgress,
    student_message: str,
) -> dict:
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY .env dosyasında bulunamadı.",
        )

    objective_lines = "\n".join(
        [f"{i}. {obj}" for i, obj in enumerate(activity.objectives)]
    )

    system_prompt = f"""
You are an academic tutor for an InClass activity.

Activity text:
{activity.activity_text}

Learning objectives, using 0-based indexes:
{objective_lines}

Already achieved objective indexes:
{progress.achieved_objectives}

Current score:
{progress.current_score}

Rules:
1. Always respond in English.
2. Ask exactly one guiding question at a time.
3. Do not directly reveal the full answer before the student reasons.
4. Use the activity terminology.
5. If the student's latest answer clearly achieves one objective, return that objective index.
6. If no objective is clearly achieved, return null.
7. A mini lesson must be short and academic.
8. Return JSON only.

JSON format:
{{
  "tutor_response": "your next tutoring response with exactly one question",
  "achieved_objective_index": null,
  "mini_lesson": null,
  "is_complete": false
}}
"""

    history = progress.chat_history or []
    recent_history = history[-12:]

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(recent_history)
    messages.append({"role": "user", "content": student_message})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI servisine bağlanılamadı: {str(e)}",
        )

    if response.status_code != 200:
        print("OpenRouter status:", response.status_code)
        print("OpenRouter response:", response.text)

        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {response.status_code}. Check backend terminal for details.",
        )

    result = response.json()
    content = result["choices"][0]["message"]["content"]

    return parse_ai_json(content)


@app.post("/activities/{activity_id}/chat")
def chat_with_tutor(
    activity_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, "student")

    activity = get_activity_or_404(db, activity_id)
    ensure_student_enrolled(db, current_user, activity.course_id)

    if activity.status != "ACTIVE":
        raise HTTPException(
            status_code=403,
            detail="Aktivite ACTIVE olmadığı için chat kullanılamaz.",
        )

    student_message = str(data.get("message", "")).strip()

    if not student_message:
        raise HTTPException(status_code=400, detail="Mesaj boş olamaz.")

    progress = get_or_create_progress(db, current_user, activity)

    if progress.is_complete:
        return {
            "reply": "This activity is already completed.",
            "achieved_objective": None,
            "score_delta": 0,
            "updated_score": progress.current_score,
            "mini_lesson": None,
            "is_complete": True,
        }

    ai_json = call_ai_tutor(activity, progress, student_message)

    tutor_response = ai_json.get("tutor_response", "")
    raw_objective_index = ai_json.get("achieved_objective_index")

    achieved_objective = None
    score_delta = 0
    mini_lesson = None

    achieved_list = list(progress.achieved_objectives or [])

    if raw_objective_index is not None:
        try:
            candidate_index = int(raw_objective_index)
        except Exception:
            candidate_index = None

        if candidate_index is not None and 0 <= candidate_index < len(activity.objectives):
            achieved_objective = candidate_index

            if candidate_index not in achieved_list:
                achieved_list.append(candidate_index)
                score_delta = 1
                progress.current_score = progress.current_score + 1
                progress.achieved_objectives = achieved_list

                mini_lesson = ai_json.get("mini_lesson")

                if not mini_lesson:
                    mini_lesson = f"Mini-lesson: {activity.objectives[candidate_index]}"

                log = ScoreLog(
                    student_id=current_user.id,
                    course_id=activity.course_id,
                    activity_id=activity.id,
                    objective_index=candidate_index,
                    score_delta=score_delta,
                    updated_score=progress.current_score,
                    event_type="AI_OBJECTIVE",
                    event_metadata={
                        "source": "ai_tutor",
                        "objective_text": activity.objectives[candidate_index],
                        "student_message": student_message,
                    },
                )

                db.add(log)

    if len(achieved_list) >= len(activity.objectives):
        progress.is_complete = 1
        is_complete = True
    else:
        is_complete = False

    chat_history = list(progress.chat_history or [])
    chat_history.append({"role": "user", "content": student_message})
    chat_history.append({"role": "assistant", "content": tutor_response})
    progress.chat_history = chat_history

    db.commit()
    db.refresh(progress)

    return {
        "reply": tutor_response,
        "achieved_objective": achieved_objective,
        "score_delta": score_delta,
        "updated_score": progress.current_score,
        "mini_lesson": mini_lesson,
        "is_complete": bool(progress.is_complete),
    }


# ---------------------------------------------------------
# MANUAL GRADE AND SCORE LOGS
# ---------------------------------------------------------

@app.post("/activities/{activity_id}/manual-grade")
def manual_grade(
    activity_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    ensure_instructor_owns_activity(db, current_user, activity)

    if activity.status == "ENDED":
        raise HTTPException(
            status_code=403,
            detail="ENDED activity için yeni score log oluşturulamaz.",
        )

    student_id = data.get("student_id")
    score_delta = data.get("score_delta")
    reason = data.get("reason", "Manual grading")

    if student_id is None or score_delta is None:
        raise HTTPException(
            status_code=400,
            detail="student_id ve score_delta zorunludur.",
        )

    student = db.query(User).filter(User.id == student_id).first()

    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı.")

    ensure_student_enrolled(db, student, activity.course_id)

    progress = get_or_create_progress(db, student, activity)
    progress.current_score = progress.current_score + int(score_delta)

    log = ScoreLog(
        student_id=student.id,
        course_id=activity.course_id,
        activity_id=activity.id,
        objective_index=None,
        score_delta=int(score_delta),
        updated_score=progress.current_score,
        event_type="MANUAL_GRADE",
        event_metadata={
            "reason": reason,
            "graded_by_instructor_id": current_user.id,
        },
    )

    db.add(log)
    db.commit()
    db.refresh(progress)

    return {
        "msg": "Manual grade kaydedildi.",
        "student_id": student.id,
        "score_delta": int(score_delta),
        "updated_score": progress.current_score,
    }


@app.get("/activities/{activity_id}/score-logs")
def get_activity_score_logs(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    ensure_instructor_owns_activity(db, current_user, activity)

    logs = (
        db.query(ScoreLog)
        .filter(ScoreLog.activity_id == activity.id)
        .order_by(ScoreLog.created_at.asc())
        .all()
    )

    return [
        {
            "id": log.id,
            "student_id": log.student_id,
            "course_id": log.course_id,
            "activity_id": log.activity_id,
            "objective_index": log.objective_index,
            "score_delta": log.score_delta,
            "updated_score": log.updated_score,
            "event_type": log.event_type,
            "metadata": log.event_metadata,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@app.get("/activities/{activity_id}/my-progress")
def get_my_progress(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, "student")

    activity = get_activity_or_404(db, activity_id)
    ensure_student_enrolled(db, current_user, activity.course_id)

    progress = get_or_create_progress(db, current_user, activity)

    return {
        "student_id": current_user.id,
        "course_id": activity.course_id,
        "activity_id": activity.id,
        "current_score": progress.current_score,
        "achieved_objectives": progress.achieved_objectives,
        "is_complete": bool(progress.is_complete),
    }