import datetime
import json
import os
import secrets
import traceback
from typing import Any, Optional

import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Activity, Course, Enrollment, ScoreLog, StudentProgress, User

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="InClass Platform API", version="2-sprint-demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- Schemas --------------------
class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str


class ActivityCreateRequest(BaseModel):
    activity_no: int
    title: str
    activity_text: str
    objectives: list[str]


class ActivityUpdateRequest(BaseModel):
    activity_no: Optional[int] = None
    title: Optional[str] = None
    activity_text: Optional[str] = None
    objectives: Optional[list[str]] = None
    status: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, Any]] = []


class ManualGradeRequest(BaseModel):
    student_id: int
    score_delta: int
    reason: str = "Manual instructor adjustment"


# -------------------- Helpers --------------------
def as_json_list(value: Optional[str]) -> list[Any]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        # Backwards compatibility for old newline objectives text.
        return [line.strip() for line in value.splitlines() if line.strip()]


def to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def user_to_public(user: User) -> dict[str, Any]:
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


def get_current_user(
    db: Session = Depends(get_db),
    x_user_token: Optional[str] = Header(default=None),
    user_id: Optional[int] = Query(default=None),
) -> User:
    """Primary auth path is X-User-Token. user_id fallback is kept only for easier local demo testing."""
    user = None
    if x_user_token:
        user = db.query(User).filter(User.auth_token == x_user_token).first()
    elif user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required or invalid token.")
    return user


def require_role(user: User, role: str):
    if user.role != role:
        raise HTTPException(status_code=403, detail=f"Only {role}s are allowed for this action.")


def get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    return course


def get_activity_or_404(db: Session, activity_id: int) -> Activity:
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
    return activity


def ensure_instructor_for_course(user: User, course: Course):
    require_role(user, "instructor")
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="Instructor is not authorized for this course.")


def ensure_student_enrolled(db: Session, user: User, course_id: int):
    require_role(user, "student")
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=403, detail="Student is not enrolled in this course.")


def activity_to_dict(activity: Activity, include_objectives: bool = False) -> dict[str, Any]:
    data = {
        "id": activity.id,
        "course_id": activity.course_id,
        "activity_no": activity.activity_no,
        "title": activity.title,
        "activity_text": activity.activity_text,
        "text": activity.activity_text,  # frontend compatibility
        "status": activity.status,
    }
    if include_objectives:
        data["objectives"] = as_json_list(activity.objectives)
    return data


def get_or_create_progress(db: Session, student: User, activity: Activity) -> StudentProgress:
    progress = (
        db.query(StudentProgress)
        .filter(StudentProgress.student_id == student.id, StudentProgress.activity_id == activity.id)
        .first()
    )
    if not progress:
        progress = StudentProgress(
            student_id=student.id,
            course_id=activity.course_id,
            activity_id=activity.id,
            covered_objectives="[]",
            total_score=0,
            chat_history="[]",
            is_complete=False,
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


def parse_llm_json(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}") + 1
        if start == -1 or end <= start:
            raise ValueError(f"LLM did not return JSON: {content}")
        return json.loads(content[start:end])


def build_tutor_prompt(activity: Activity, progress: StudentProgress) -> str:
    objectives = as_json_list(activity.objectives)
    covered = as_json_list(progress.covered_objectives)
    return f"""
You are an English-speaking university tutor for the InClass Platform.

Activity text:
{activity.activity_text}

Learning objectives, numbered from 1:
{json.dumps(objectives, ensure_ascii=False)}

Already covered objectives:
{covered}

Current score:
{progress.total_score}

Rules:
1. Use English only.
2. Ask exactly one guiding question at a time.
3. Do not reveal the final answer directly before the student has reasoned about it.
4. Use the activity terminology.
5. If the student's latest answer demonstrates one objective, set achieved_objective_index to its 1-based number.
6. If no new objective is demonstrated, set achieved_objective_index to null.
7. If you set achieved_objective_index, include a short academic mini_lesson for that objective.
8. If all objectives are covered, set is_complete true and include a brief celebration.
9. Return JSON only.

Required JSON shape:
{{
  "tutor_response": "one guiding response with exactly one question unless complete",
  "achieved_objective_index": null,
  "mini_lesson": "short lesson only when an objective is achieved",
  "is_complete": false
}}
"""


def call_openrouter(messages: list[dict[str, str]]) -> dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="OPENROUTER_API_KEY is missing. Add it to backend/.env and restart Uvicorn.",
        )

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=45,
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
    return parse_llm_json(content)


# -------------------- Authentication --------------------
@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user.auth_token = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "token": user.auth_token,
    }


@app.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.role not in ["student", "instructor"]:
        raise HTTPException(status_code=400, detail="Role must be student or instructor.")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists.")

    user = User(name=data.name, email=data.email, password=data.password, role=data.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "Registration successful.", "user": user_to_public(user)}


@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return user_to_public(current_user)


# -------------------- Courses --------------------
@app.get("/courses")
def get_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "instructor":
        return (
            db.query(Course)
            .filter(Course.instructor_id == current_user.id)
            .order_by(Course.course_code.asc())
            .all()
        )

    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    course_ids = [e.course_id for e in enrollments]
    if not course_ids:
        return []
    return db.query(Course).filter(Course.id.in_(course_ids)).order_by(Course.course_code.asc()).all()


@app.get("/courses/{course_id}/students")
def get_course_students(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = get_course_or_404(db, course_id)
    ensure_instructor_for_course(current_user, course)
    rows = (
        db.query(User)
        .join(Enrollment, Enrollment.student_id == User.id)
        .filter(Enrollment.course_id == course_id, User.role == "student")
        .order_by(User.name.asc())
        .all()
    )
    return [user_to_public(u) for u in rows]


# -------------------- Activities --------------------
@app.get("/courses/{course_id}/activities")
def get_course_activities(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = get_course_or_404(db, course_id)

    include_objectives = False
    if current_user.role == "instructor":
        ensure_instructor_for_course(current_user, course)
        include_objectives = True
    else:
        ensure_student_enrolled(db, current_user, course_id)

    activities = (
        db.query(Activity)
        .filter(Activity.course_id == course_id)
        .order_by(Activity.activity_no.asc())
        .all()
    )
    return [activity_to_dict(a, include_objectives=include_objectives) for a in activities]


@app.post("/courses/{course_id}/activities")
def create_activity(
    course_id: int,
    data: ActivityCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = get_course_or_404(db, course_id)
    ensure_instructor_for_course(current_user, course)

    if data.activity_no <= 0 or not data.title.strip() or not data.activity_text.strip() or not data.objectives:
        raise HTTPException(status_code=400, detail="activity_no, title, activity_text and objectives are required.")

    activity = Activity(
        course_id=course_id,
        activity_no=data.activity_no,
        title=data.title.strip(),
        activity_text=data.activity_text.strip(),
        objectives=to_json([o.strip() for o in data.objectives if o.strip()]),
        status="NOT_STARTED",
    )
    db.add(activity)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate activity number in this course.")
    db.refresh(activity)
    return activity_to_dict(activity, include_objectives=True)


@app.put("/activities/{activity_id}")
def update_activity(
    activity_id: int,
    data: ActivityUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    course = get_course_or_404(db, activity.course_id)
    ensure_instructor_for_course(current_user, course)

    patch = data.dict(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="Empty update patch is not allowed.")

    allowed_statuses = {"NOT_STARTED", "ACTIVE", "ENDED"}
    if "status" in patch and patch["status"] not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid activity status.")

    if "activity_no" in patch:
        if patch["activity_no"] <= 0:
            raise HTTPException(status_code=400, detail="activity_no must be positive.")
        activity.activity_no = patch["activity_no"]
    if "title" in patch:
        if not patch["title"].strip():
            raise HTTPException(status_code=400, detail="title cannot be empty.")
        activity.title = patch["title"].strip()
    if "activity_text" in patch:
        if not patch["activity_text"].strip():
            raise HTTPException(status_code=400, detail="activity_text cannot be empty.")
        activity.activity_text = patch["activity_text"].strip()
    if "objectives" in patch:
        if not patch["objectives"]:
            raise HTTPException(status_code=400, detail="objectives cannot be empty.")
        activity.objectives = to_json([o.strip() for o in patch["objectives"] if o.strip()])
    if "status" in patch:
        activity.status = patch["status"]

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate activity number in this course.")
    db.refresh(activity)
    return activity_to_dict(activity, include_objectives=True)


@app.post("/activities/{activity_id}/start")
def start_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    course = get_course_or_404(db, activity.course_id)
    ensure_instructor_for_course(current_user, course)
    activity.status = "ACTIVE"
    db.commit()
    return {"msg": "Activity started.", "activity": activity_to_dict(activity, include_objectives=True)}


@app.post("/activities/{activity_id}/end")
def end_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    course = get_course_or_404(db, activity.course_id)
    ensure_instructor_for_course(current_user, course)
    activity.status = "ENDED"
    db.commit()
    return {"msg": "Activity ended.", "activity": activity_to_dict(activity, include_objectives=True)}


@app.post("/activities/{activity_id}/reset")
def reset_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    course = get_course_or_404(db, activity.course_id)
    ensure_instructor_for_course(current_user, course)

    db.query(ScoreLog).filter(ScoreLog.activity_id == activity_id).delete()
    db.query(StudentProgress).filter(StudentProgress.activity_id == activity_id).delete()
    activity.status = "ENDED"
    db.commit()
    return {"msg": "Activity reset: scores/progress deleted and activity set to ENDED."}


@app.get("/activities/{activity_id}")
def get_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    course = get_course_or_404(db, activity.course_id)

    if current_user.role == "instructor":
        ensure_instructor_for_course(current_user, course)
        return activity_to_dict(activity, include_objectives=True)

    ensure_student_enrolled(db, current_user, activity.course_id)
    if activity.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="Activity is not ACTIVE.")

    progress = get_or_create_progress(db, current_user, activity)
    data = activity_to_dict(activity, include_objectives=False)
    data.update(
        {
            "current_score": progress.total_score,
            "covered_objectives": as_json_list(progress.covered_objectives),
            "is_complete": progress.is_complete,
        }
    )
    return data


# -------------------- Tutoring and Scoring --------------------
@app.post("/activities/{activity_id}/chat")
def chat_with_tutor(
    activity_id: int,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        activity = get_activity_or_404(db, activity_id)
        ensure_student_enrolled(db, current_user, activity.course_id)

        if activity.status != "ACTIVE":
            raise HTTPException(status_code=403, detail="Activity is not ACTIVE. Tutoring is closed.")

        progress = get_or_create_progress(db, current_user, activity)
        if progress.is_complete:
            return {
                "reply": "This activity is already complete. Great work!",
                "achieved_objective": None,
                "earned_point": False,
                "updated_score": progress.total_score,
                "is_complete": True,
            }

        saved_history = as_json_list(progress.chat_history)
        client_history = data.history or []
        history = client_history if client_history else saved_history

        prompt = build_tutor_prompt(activity, progress)
        messages = [{"role": "system", "content": prompt}]
        for item in history[-12:]:
            role = item.get("role")
            content = item.get("content")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

        student_message = data.message.strip() or "Please start the activity."
        if student_message == "__START__":
            student_message = "Please show me the activity text and ask the first guiding question."
        messages.append({"role": "user", "content": student_message})

        llm_json = call_openrouter(messages)

        objectives = as_json_list(activity.objectives)
        covered = as_json_list(progress.covered_objectives)
        obj_idx = llm_json.get("achieved_objective_index")
        earned_point = False
        duplicate_objective = False

        if obj_idx is not None:
            try:
                obj_idx = int(obj_idx)
            except Exception:
                obj_idx = None

        if obj_idx is not None and not (1 <= obj_idx <= len(objectives)):
            obj_idx = None

        if obj_idx is not None:
            if obj_idx not in covered:
                covered.append(obj_idx)
                progress.total_score += 1
                earned_point = True
                db.add(
                    ScoreLog(
                        student_id=current_user.id,
                        course_id=activity.course_id,
                        activity_id=activity.id,
                        objective_index=obj_idx,
                        score_delta=1,
                        total_score_after=progress.total_score,
                        event_type="objective_earned",
                        metadata_json=to_json(
                            {
                                "source": "llm",
                                "student_message": student_message,
                                "objective_text": objectives[obj_idx - 1],
                            }
                        ),
                    )
                )
            else:
                duplicate_objective = True
                db.add(
                    ScoreLog(
                        student_id=current_user.id,
                        course_id=activity.course_id,
                        activity_id=activity.id,
                        objective_index=obj_idx,
                        score_delta=0,
                        total_score_after=progress.total_score,
                        event_type="duplicate_objective",
                        metadata_json=to_json({"source": "llm", "student_message": student_message}),
                    )
                )

        progress.covered_objectives = to_json(sorted(covered))
        if len(covered) >= len(objectives):
            progress.is_complete = True

        tutor_reply = llm_json.get("tutor_response", "")
        mini_lesson = llm_json.get("mini_lesson") or ""

        if earned_point:
            tutor_reply = (
                f"✅ Objective {obj_idx} achieved. Updated score: {progress.total_score}.\n"
                f"Mini-lesson: {mini_lesson}\n\n"
                f"{tutor_reply}"
            )
        elif duplicate_objective:
            tutor_reply = f"You already earned Objective {obj_idx}, so no extra point is added.\n\n{tutor_reply}"

        if progress.is_complete:
            tutor_reply = f"{tutor_reply}\n\n🏆 All objectives are covered. Activity complete!"

        new_history = history + [
            {"role": "user", "content": student_message},
            {"role": "assistant", "content": tutor_reply},
        ]
        progress.chat_history = to_json(new_history[-20:])
        db.commit()

        return {
            "reply": tutor_reply,
            "achieved_objective": obj_idx if earned_point else None,
            "earned_point": earned_point,
            "updated_score": progress.total_score,
            "covered_objectives": sorted(covered),
            "is_complete": progress.is_complete,
        }
    except HTTPException:
        raise
    except Exception as exc:
        print("CHAT ERROR")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {exc}")


@app.get("/activities/{activity_id}/score-logs")
def get_score_logs(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    course = get_course_or_404(db, activity.course_id)
    ensure_instructor_for_course(current_user, course)

    logs = (
        db.query(ScoreLog)
        .filter(ScoreLog.activity_id == activity_id)
        .order_by(ScoreLog.timestamp.asc())
        .all()
    )
    result = []
    for log in logs:
        student = db.query(User).filter(User.id == log.student_id).first()
        result.append(
            {
                "id": log.id,
                "student_id": log.student_id,
                "student_name": student.name if student else "Unknown",
                "course_id": log.course_id,
                "activity_id": log.activity_id,
                "objective_index": log.objective_index,
                "score_delta": log.score_delta,
                "total_score_after": log.total_score_after,
                "event_type": log.event_type,
                "metadata": json.loads(log.metadata_json or "{}"),
                "timestamp": log.timestamp.isoformat(),
            }
        )
    return result


@app.post("/activities/{activity_id}/manual-grade")
def manual_grade(
    activity_id: int,
    data: ManualGradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    course = get_course_or_404(db, activity.course_id)
    ensure_instructor_for_course(current_user, course)

    if activity.status == "ENDED":
        raise HTTPException(status_code=403, detail="ENDED activity cannot accept new score logs.")

    student = db.query(User).filter(User.id == data.student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    ensure_student_enrolled(db, student, activity.course_id)

    progress = get_or_create_progress(db, student, activity)
    progress.total_score += data.score_delta
    db.add(
        ScoreLog(
            student_id=student.id,
            course_id=activity.course_id,
            activity_id=activity.id,
            objective_index=None,
            score_delta=data.score_delta,
            total_score_after=progress.total_score,
            event_type="manual_grade",
            metadata_json=to_json({"reason": data.reason, "instructor_id": current_user.id}),
        )
    )
    db.commit()
    return {"msg": "Manual grade logged.", "student_id": student.id, "updated_score": progress.total_score}


@app.get("/activities/{activity_id}/progress")
def get_activity_progress(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = get_activity_or_404(db, activity_id)
    course = get_course_or_404(db, activity.course_id)
    ensure_instructor_for_course(current_user, course)

    rows = db.query(StudentProgress).filter(StudentProgress.activity_id == activity_id).all()
    result = []
    for progress in rows:
        student = db.query(User).filter(User.id == progress.student_id).first()
        result.append(
            {
                "student_id": progress.student_id,
                "student_name": student.name if student else "Unknown",
                "total_score": progress.total_score,
                "covered_objectives": as_json_list(progress.covered_objectives),
                "is_complete": progress.is_complete,
                "updated_at": progress.updated_at.isoformat() if progress.updated_at else None,
            }
        )
    return result


# -------------------- Demo Setup --------------------
@app.post("/setup-demo")
def setup_demo(db: Session = Depends(get_db)):
    """Clean demo data and reload the minimum dataset required by the demo document."""
    db.query(ScoreLog).delete()
    db.query(StudentProgress).delete()
    db.query(Activity).delete()
    db.query(Enrollment).delete()
    db.query(Course).delete()
    db.query(User).delete()
    db.commit()

    instructor_a = User(name="Instructor A", email="hoca_a@test.com", password="123", role="instructor")
    instructor_b = User(name="Instructor B", email="hoca_b@test.com", password="123", role="instructor")
    student_1 = User(name="Student 1", email="ogr_1@test.com", password="123", role="student")
    student_2 = User(name="Student 2", email="ogr_2@test.com", password="123", role="student")
    db.add_all([instructor_a, instructor_b, student_1, student_2])
    db.commit()

    course_1 = Course(course_code="COMP302", course_name="Software Engineering", instructor_id=instructor_a.id)
    course_2 = Course(course_code="COMP400", course_name="Independent Study", instructor_id=instructor_b.id)
    db.add_all([course_1, course_2])
    db.commit()

    db.add(Enrollment(student_id=student_1.id, course_id=course_1.id))

    activity_text = (
        "A student studies for an exam by rereading the textbook many times. "
        "Another student studies by closing the book and trying to explain the ideas from memory, "
        "then checking mistakes. Which strategy is likely to support better long-term learning, and why?"
    )
    objectives = [
        "Explain that active retrieval practice improves long-term learning more than passive rereading.",
        "Explain that feedback after retrieval helps identify and correct misunderstandings.",
    ]
    db.add_all(
        [
            Activity(
                course_id=course_1.id,
                activity_no=1,
                title="Retrieval Practice Demo",
                activity_text=activity_text,
                objectives=to_json(objectives),
                status="NOT_STARTED",
            ),
            Activity(
                course_id=course_1.id,
                activity_no=2,
                title="Spacing Effect Activity",
                activity_text="Compare studying in one long session with studying in shorter sessions across several days.",
                objectives=to_json(["Explain why spaced practice improves retention.", "Give an example of a spacing schedule."]),
                status="NOT_STARTED",
            ),
        ]
    )
    db.commit()

    return {
        "msg": "Demo data loaded.",
        "accounts": {
            "Instructor A": "hoca_a@test.com / 123",
            "Instructor B": "hoca_b@test.com / 123",
            "Student 1": "ogr_1@test.com / 123",
            "Student 2": "ogr_2@test.com / 123",
        },
    }
