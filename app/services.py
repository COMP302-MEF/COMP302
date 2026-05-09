import os
from datetime import datetime, timezone
from typing import Optional

from supabase import create_client, Client
from dotenv import load_dotenv
import bcrypt
from fastapi import Header, HTTPException

from app.llm_service import generate_llm_tutoring_reply

load_dotenv(override=True)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# -- AUTH HELPERS --

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        if not hashed:
            return False
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def verify_token_get_email(
    authorization: Optional[str] = Header(default=None),
    x_user_email: Optional[str] = Header(default=None)
) -> str:
    """
    Gets the current user email.

    For local testing:
    - Send x-user-email header.

    For Supabase auth token:
    - Send Authorization: Bearer <token>
    """

    if x_user_email:
        return x_user_email

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user and user_response.user.email:
                return user_response.user.email
        except Exception:
            pass

    raise HTTPException(
        status_code=401,
        detail="Unauthorized: missing or invalid user identity"
    )


# -- AUTHENTICATION & ENROLLMENT --

def instructorRegister(email: str, password: str, name: str, **kwargs) -> dict:
    hashed = hash_password(password)

    supabase.table("instructors").upsert({
        "email": email,
        "password_hash": hashed,
        "name": name
    }).execute()

    supabase.table("courses").upsert({
        "course_id": "COMP302",
        "course_name": "Software Engineering"
    }).execute()

    supabase.table("course_instructors").upsert({
        "course_id": "COMP302",
        "instructor_email": email
    }).execute()

    return {"ok": True, "email": email}


def instructorLogin(email: str, password: str, **kwargs) -> dict:
    res = supabase.table("instructors").select("*").eq("email", email).execute()

    if res.data:
        for row in res.data:
            if verify_password(password, row.get("password_hash")):
                return {"ok": True, "email": email}

    return {"ok": False, "error": "Invalid credentials"}


def studentRegister(email: str, password: str, name: str, **kwargs) -> dict:
    hashed = hash_password(password)

    supabase.table("students").upsert({
        "email": email,
        "password_hash": hashed,
        "name": name
    }).execute()

    supabase.table("courses").upsert({
        "course_id": "COMP302",
        "course_name": "Software Engineering"
    }).execute()

    supabase.table("course_students").upsert({
        "course_id": "COMP302",
        "student_email": email
    }).execute()

    return {"ok": True, "email": email}


def studentLogin(email: str, password: str, **kwargs) -> dict:
    res = supabase.table("students").select("*").eq("email", email).execute()

    if res.data:
        for row in res.data:
            if verify_password(password, row.get("password_hash")):
                return {"ok": True, "email": email}

    return {"ok": False, "error": "Invalid credentials"}


# -- PASSWORD MANAGEMENT --

def changeInstructorPassword(email: str, password: str = None, **kwargs) -> dict:
    actual_password = kwargs.get("new_password") or password

    if not actual_password:
        return {"ok": False, "error": "Password required"}

    check = supabase.table("instructors").select("email").eq("email", email).execute()

    if not check.data:
        return {"ok": False, "error": "Instructor not found"}

    hashed = hash_password(actual_password)

    supabase.table("instructors").update({
        "password_hash": hashed
    }).eq("email", email).execute()

    return {"ok": True}


def setInstructorPassword(email: str, password: str, **kwargs) -> dict:
    res = supabase.table("instructors").select("password_hash").eq("email", email).execute()

    if res.data and res.data[0].get("password_hash"):
        return {"ok": False, "error": "Instructor password already exists"}

    return changeInstructorPassword(email, password)


def resetInstructorPassword(email: str, password: str = None, **kwargs) -> dict:
    return changeInstructorPassword(email, password, **kwargs)


def changeStudentPassword(email: str, password: str = None, **kwargs) -> dict:
    actual_password = kwargs.get("new_password") or password

    if not actual_password:
        return {"ok": False, "error": "Password required"}

    check = supabase.table("students").select("email").eq("email", email).execute()

    if not check.data:
        return {"ok": False, "error": "Student not found"}

    hashed = hash_password(actual_password)

    supabase.table("students").update({
        "password_hash": hashed
    }).eq("email", email).execute()

    return {"ok": True}


def setStudentPassword(email: str, password: str, **kwargs) -> dict:
    res = supabase.table("students").select("password_hash").eq("email", email).execute()

    if res.data and res.data[0].get("password_hash"):
        return {"ok": False, "error": "Student password already exists"}

    return changeStudentPassword(email, password)


def resetStudentPassword(email: str, password: str = None, **kwargs) -> dict:
    return changeStudentPassword(email, password, **kwargs)


# -- AUTHORIZATION HELPERS --

def is_student_enrolled(student_email: str, course_id: str) -> bool:
    res = (
        supabase.table("course_students")
        .select("course_id")
        .eq("course_id", course_id)
        .eq("student_email", student_email)
        .execute()
    )

    return bool(res.data)


def is_instructor_assigned(instructor_email: str, course_id: str) -> bool:
    res = (
        supabase.table("course_instructors")
        .select("course_id")
        .eq("course_id", course_id)
        .eq("instructor_email", instructor_email)
        .execute()
    )

    return bool(res.data)


# -- CORE FEATURES --

def listMyCourses(email: str, **kwargs) -> dict:
    res_i = (
        supabase.table("course_instructors")
        .select("course_id")
        .eq("instructor_email", email)
        .execute()
    )

    res_s = (
        supabase.table("course_students")
        .select("course_id")
        .eq("student_email", email)
        .execute()
    )

    ids = [r["course_id"] for r in res_i.data] + [r["course_id"] for r in res_s.data]

    if not ids:
        return {"ok": True, "courses": []}

    courses = (
        supabase.table("courses")
        .select("*")
        .in_("course_id", ids)
        .execute()
    )

    return {"ok": True, "courses": courses.data}


def createActivity(
    email: str,
    course_id: str,
    activity_text: str,
    learning_objectives: list[str],
    activity_no_optional: int = None,
    **kwargs
) -> dict:
    supabase.table("courses").upsert({
        "course_id": course_id,
        "course_name": "Course"
    }).execute()

    supabase.table("course_instructors").upsert({
        "course_id": course_id,
        "instructor_email": email
    }).execute()

    if activity_no_optional is not None:
        activity_no = activity_no_optional

        exist = (
            supabase.table("activities")
            .select("activity_no")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if exist.data:
            return {
                "ok": False,
                "error": "Duplicate activity number in the same course."
            }

    else:
        last = (
            supabase.table("activities")
            .select("activity_no")
            .eq("course_id", course_id)
            .order("activity_no", desc=True)
            .limit(1)
            .execute()
        )

        activity_no = (last.data[0]["activity_no"] + 1) if last.data else 1

    supabase.table("activities").insert({
        "course_id": course_id,
        "activity_no": activity_no,
        "activity_text": activity_text,
        "learning_objectives": learning_objectives,
        "status": "NOT_STARTED"
    }).execute()

    return {"ok": True, "activity_no": activity_no}


def getActivity(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    """
    US-I + US-J:
    Student can fetch only ACTIVE activities.
    Activity text is shown first.
    Learning objectives are not exposed.
    Exactly one guiding question is returned.
    """

    if not is_student_enrolled(student_email=email, course_id=course_id):
        return {
            "ok": False,
            "error": "Student is not authorized for this course."
        }

    res = (
        supabase.table("activities")
        .select("*")
        .eq("course_id", course_id)
        .eq("activity_no", activity_no)
        .execute()
    )

    if not res.data:
        return {
            "ok": False,
            "error": "Activity not found."
        }

    act = res.data[0]

    if act["status"] != "ACTIVE":
        return {
            "ok": False,
            "error": "Activity is not active."
        }

    progress = get_or_create_student_progress(
        student_email=email,
        course_id=course_id,
        activity_no=activity_no
    )

    first_question = progress.get("last_question")

    if not first_question:
        first_question = generate_guiding_question(
            activity_text=act["activity_text"],
            current_step=progress.get("current_step", 0)
        )

        update_student_progress(
            student_email=email,
            course_id=course_id,
            activity_no=activity_no,
            current_step=progress.get("current_step", 0),
            last_question=first_question,
            completed=False
        )

        save_tutoring_message(
            student_email=email,
            course_id=course_id,
            activity_no=activity_no,
            sender="SYSTEM",
            message=first_question
        )

    return {
        "ok": True,
        "activity_no": act["activity_no"],
        "activity_text": act["activity_text"],
        "status": act["status"],
        "message": first_question,
        "question_count": 1,
        "completed": progress.get("completed", False)
    }


def startActivity(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    supabase.table("activities").update({
        "status": "ACTIVE"
    }).eq("course_id", course_id).eq("activity_no", activity_no).execute()

    return {"ok": True}


def endActivity(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    supabase.table("activities").update({
        "status": "ENDED"
    }).eq("course_id", course_id).eq("activity_no", activity_no).execute()

    return {"ok": True}


def logScore(
    email: str,
    course_id: str,
    activity_no: int,
    score: float,
    meta: str = None,
    **kwargs
) -> dict:
    act = (
        supabase.table("activities")
        .select("status")
        .eq("course_id", course_id)
        .eq("activity_no", activity_no)
        .execute()
    )

    if act.data and act.data[0]["status"] == "ENDED":
        return {
            "ok": False,
            "error": "Ended activity cannot accept new score logs."
        }

    supabase.table("students").upsert({"email": email}).execute()

    supabase.table("score_logs").insert({
        "course_id": course_id,
        "activity_no": activity_no,
        "student_email": email,
        "score": score,
        "meta": meta
    }).execute()

    return {"ok": True}


def listActivities(email: str, course_id: str, **kwargs) -> dict:
    r = (
        supabase.table("activities")
        .select("activity_no, status")
        .eq("course_id", course_id)
        .order("activity_no")
        .execute()
    )

    return {"ok": True, "activities": r.data}


def resetActivity(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    supabase.table("score_logs").delete().eq("course_id", course_id).eq("activity_no", activity_no).execute()

    supabase.table("activities").update({
        "status": "ENDED"
    }).eq("course_id", course_id).eq("activity_no", activity_no).execute()

    return {"ok": True}


def exportScores(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    r = (
        supabase.table("score_logs")
        .select("*")
        .eq("course_id", course_id)
        .eq("activity_no", activity_no)
        .execute()
    )

    csv = "student_email,score,meta,created_at\n"

    for row in r.data:
        csv += f"{row['student_email']},{row['score']},{row.get('meta', '')},{row['created_at']}\n"

    return {"ok": True, "csv": csv}


def updateActivity(email: str, course_id: str, activity_no: int, patch: dict, **kwargs) -> dict:
    if not patch:
        return {
            "ok": False,
            "error": "Empty patch is not allowed."
        }

    supabase.table("activities").update(patch).eq("course_id", course_id).eq("activity_no", activity_no).execute()

    return {"ok": True}


# -- US-J STUDENT TUTORING FLOW HELPERS --

def get_or_create_student_progress(student_email: str, course_id: str, activity_no: int) -> dict:
    res = (
        supabase.table("student_progress")
        .select("*")
        .eq("student_email", student_email)
        .eq("course_id", course_id)
        .eq("activity_no", activity_no)
        .execute()
    )

    if res.data:
        return res.data[0]

    new_progress = {
        "student_email": student_email,
        "course_id": course_id,
        "activity_no": activity_no,
        "current_step": 0,
        "completed": False,
        "last_question": None
    }

    inserted = supabase.table("student_progress").insert(new_progress).execute()

    if inserted.data:
        return inserted.data[0]

    return new_progress


def update_student_progress(
    student_email: str,
    course_id: str,
    activity_no: int,
    current_step: int,
    last_question: str,
    completed: bool = False
) -> None:
    now = datetime.now(timezone.utc).isoformat()

    (
        supabase.table("student_progress")
        .update({
            "current_step": current_step,
            "last_question": last_question,
            "completed": completed,
            "updated_at": now
        })
        .eq("student_email", student_email)
        .eq("course_id", course_id)
        .eq("activity_no", activity_no)
        .execute()
    )


def save_tutoring_message(
    student_email: str,
    course_id: str,
    activity_no: int,
    sender: str,
    message: str
) -> None:
    supabase.table("tutoring_messages").insert({
        "student_email": student_email,
        "course_id": course_id,
        "activity_no": activity_no,
        "sender": sender,
        "message": message
    }).execute()


def generate_guiding_question(activity_text: str, current_step: int) -> str:
    """
    Fallback question generator.
    Used for first activity fetch or if LLM is unavailable.
    Returns exactly one guiding question.
    """

    questions = [
        "What is the main difference between rereading and explaining ideas from memory?",
        "Which study strategy is more likely to support long-term learning?",
        "How does checking mistakes after recalling information help learning?",
        "What is your final explanation using the activity terminology?"
    ]

    if current_step < len(questions):
        return questions[current_step]

    return "Can you summarize your reasoning in one clear sentence?"


def studentChat(
    email: str,
    course_id: str,
    activity_no: int,
    student_message: str,
    chat_history: list[dict[str, str]] = None,
    **kwargs
) -> dict:
    """
    US-J:
    Stores student answer.
    Sends activity text, hidden objectives, student message, and chat history to LLM.
    Returns exactly one next guiding question.
    Stores student progress per student and activity.
    Blocks flow when activity is not ACTIVE.
    """

    chat_history = chat_history or []

    if not is_student_enrolled(student_email=email, course_id=course_id):
        return {
            "ok": False,
            "error": "Student is not authorized for this course."
        }

    res = (
        supabase.table("activities")
        .select("*")
        .eq("course_id", course_id)
        .eq("activity_no", activity_no)
        .execute()
    )

    if not res.data:
        return {
            "ok": False,
            "error": "Activity not found."
        }

    act = res.data[0]

    if act["status"] != "ACTIVE":
        return {
            "ok": False,
            "error": "This activity is not active. Tutoring flow cannot continue."
        }

    progress = get_or_create_student_progress(
        student_email=email,
        course_id=course_id,
        activity_no=activity_no
    )

    if student_message and student_message.strip():
        save_tutoring_message(
            student_email=email,
            course_id=course_id,
            activity_no=activity_no,
            sender="STUDENT",
            message=student_message.strip()
        )

    next_step = progress.get("current_step", 0) + 1

    learning_objectives = act.get("learning_objectives") or []

    try:
        llm_result = generate_llm_tutoring_reply(
            activity_text=act["activity_text"],
            learning_objectives=learning_objectives,
            student_message=student_message,
            chat_history=chat_history
        )

        next_question = llm_result["reply"]

    except Exception:
        next_question = generate_guiding_question(
            activity_text=act["activity_text"],
            current_step=next_step
        )

    update_student_progress(
        student_email=email,
        course_id=course_id,
        activity_no=activity_no,
        current_step=next_step,
        last_question=next_question,
        completed=False
    )

    save_tutoring_message(
        student_email=email,
        course_id=course_id,
        activity_no=activity_no,
        sender="SYSTEM",
        message=next_question
    )

    return {
        "ok": True,
        "activity_no": activity_no,
        "message": next_question,
        "question_count": 1,
        "completed": False
    }