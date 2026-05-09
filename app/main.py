import os
from typing import List, Dict

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app import services

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(
    title="InClass Platform API",
    description="Instructor activity management and student tutoring flow API",
    version="1.0.0"
)


# ── Health Check ───────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "ok": True,
        "message": "InClass Platform API is running"
    }


# ── Instructor Main ────────────────────────────────────────────────────────

@app.post("/instructor/list-my-courses")
def listMyCourses(
    email: str = Depends(services.verify_token_get_email)
):
    return services.listMyCourses(email=email)


@app.post("/instructor/list-activities")
def listActivities(
    *,
    course_id: str,
    email: str = Depends(services.verify_token_get_email)
):
    return services.listActivities(
        email=email,
        course_id=course_id
    )


@app.post("/instructor/create-activity")
def createActivity(
    *,
    course_id: str,
    activity_text: str,
    learning_objectives: List[str],
    activity_no_optional: int = None,
    email: str = Depends(services.verify_token_get_email)
):
    return services.createActivity(
        email=email,
        course_id=course_id,
        activity_text=activity_text,
        learning_objectives=learning_objectives,
        activity_no_optional=activity_no_optional
    )


@app.post("/instructor/update-activity")
def updateActivity(
    *,
    course_id: str,
    activity_no: int,
    patch: dict,
    email: str = Depends(services.verify_token_get_email)
):
    return services.updateActivity(
        email=email,
        course_id=course_id,
        activity_no=activity_no,
        patch=patch
    )


@app.post("/instructor/start-activity")
def startActivity(
    *,
    course_id: str,
    activity_no: int,
    email: str = Depends(services.verify_token_get_email)
):
    return services.startActivity(
        email=email,
        course_id=course_id,
        activity_no=activity_no
    )


@app.post("/instructor/end-activity")
def endActivity(
    *,
    course_id: str,
    activity_no: int,
    email: str = Depends(services.verify_token_get_email)
):
    return services.endActivity(
        email=email,
        course_id=course_id,
        activity_no=activity_no
    )


@app.post("/instructor/export-scores")
def exportScores(
    *,
    course_id: str,
    activity_no: int,
    email: str = Depends(services.verify_token_get_email)
):
    return services.exportScores(
        email=email,
        course_id=course_id,
        activity_no=activity_no
    )


@app.post("/instructor/reset-activity")
def resetActivity(
    *,
    course_id: str,
    activity_no: int,
    email: str = Depends(services.verify_token_get_email)
):
    return services.resetActivity(
        email=email,
        course_id=course_id,
        activity_no=activity_no
    )


# ── Student Main ───────────────────────────────────────────────────────────

@app.post("/student/get-activity")
def getActivity(
    *,
    course_id: str,
    activity_no: int,
    email: str = Depends(services.verify_token_get_email)
):
    return services.getActivity(
        email=email,
        course_id=course_id,
        activity_no=activity_no
    )


@app.post("/student/log-score")
def logScore(
    *,
    course_id: str,
    activity_no: int,
    score: float,
    meta: str = None,
    email: str = Depends(services.verify_token_get_email)
):
    return services.logScore(
        email=email,
        course_id=course_id,
        activity_no=activity_no,
        score=score,
        meta=meta
    )


# ── US-J Student Tutoring Flow ─────────────────────────────────────────────

class ChatPayload(BaseModel):
    course_id: str
    activity_no: int
    student_message: str
    chat_history: List[Dict[str, str]] = Field(default_factory=list)


@app.post("/student/chat")
def studentChat(
    payload: ChatPayload,
    email: str = Depends(services.verify_token_get_email)
):
    return services.studentChat(
        email=email,
        course_id=payload.course_id,
        activity_no=payload.activity_no,
        student_message=payload.student_message,
        chat_history=payload.chat_history
    )