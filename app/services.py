import os
from unittest import result

import bcrypt
from supabase import create_client, Client
from dotenv import load_dotenv
from tenacity import retry_if_not_exception_type

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

#--Helpers--

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def _get_instructor(email: str) -> dict | None:
    result = supabase.table("instructors").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None

def _get_student(email: str) -> dict | None:
    result = supabase.table("students").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None

def _verify_instructor(email: str, password: str) -> dict | None:
    instructor = _get_instructor(email)
    if not instructor:
        return None
    if not instructor.get("password_hash"):
        return None
    if not _check_password(password, instructor["password_hash"]):
        return None
    return instructor

def _verify_student(email: str, password: str) -> dict | None:
    student = _get_student(email)
    if not student:
        return None
    if not student.get("password_hash"):
        return None
    if not _check_password(password, student["password_hash"]):
        return None
    return student

#--Instructor Auth--

def instructorLogin(email: str, password: str) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    return {"ok": True, "email": instructor['email']}

def setInstructorPassword(email: str, password: str | None = None) -> dict:
    instructor = _get_instructor(email)
    if not instructor:
        return {"ok": False, "error": "Instructor not found"}
    if instructor.get("password_hash"):
        return {"ok": False, "error": "Password already set"}
    hashed = _hash_password(password)
    supabase.table("instructors").update({"password_hash": hashed}).eq("email", email).execute()
    return {"ok": True}

def changeInstructorPassword(email: str, password: str, old_password: str, new_password: str) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    if not _check_password(old_password, instructor["password_hash"]):
        return {"ok": False, "error": "Old password incorrect"}
    hashed = _hash_password(new_password)
    supabase.table("instructors").update({"password_hash": hashed}).eq("email", email).execute()
    return {"ok": True}

#--Student Auth--

def studentLogin(email: str, password: str) -> dict:
    student = _verify_student(email, password)
    if not student:
        return {"ok": False, "error": "Invalid credentials"}
    return {"ok": True, "email": student["email"]}

def setStudentPassword(email: str, password: str) -> dict:
    student = _get_student(email)
    if not student:
        return {"ok": False, "error": "Student not found"}
    if student.get("password_hash"):
        return {"ok": False, "error": "Password already set"}
    hashed = _hash_password(password)
    supabase.table("students").update({"password_hash": hashed}).eq("email", email).execute()
    return {"ok": True}

def changeStudentPassword(email: str, password: str, new_password: str, old_password: str) -> dict:
    student = _verify_student(email, password)
    if not student:
        return {"ok": False, "error": "Invalid credentials"}
    if not _check_password(old_password, student["password_hash"]):
        return {"ok": False, "error": "Old password incorrect"}
    hashed = _hash_password(new_password)
    supabase.table("students").update({"password_hash": hashed}).eq("email", email).execute()
    return {"ok": True}

#--Instructor--

def listMyCourses(email: str, password: str) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    result = supabase.table("course_instructors").select("course_id").eq("instructor_email", email).execute()
    course_ids = [r["course_id"] for r in result.data]
    courses = []
    for cid in course_ids:
        c = supabase.table("courses").select("*").eq("course_id", cid).execute()
        if c.data:
            courses.append(c.data[0])
    return {"ok": True, "courses": courses}

def listActivities(email:str, password: str, course_id: str) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_instructors").select("*").eq("instructor_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    result = supabase.table("activities").select("activity_no_status").eq("course_id", course_id).order("activity_no").execute()
    return {"ok": True, "activities": result.data}

def createActivity(email:str, password:str, course_id:str, activity_text:str, learning_objectives: list[str], activity_no_optional: int | None = None) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_instructors").select("*").eq("course_id", course_id).eq("instructor_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    if activity_no_optional is not None:
       existing = supabase.table("activities").select("*").eq("course_id", course_id).order("activity_no", activity_no_optional).execute()
       if existing.data:
           return {"ok": False, "error": "Activity number already exists"}
       activity_no = activity_no_optional
    else:
        last = supabase.table("activities").select("activity_no").eq("course_id", course_id).order("activity_no", desc=True).limit(1).execute()
        activity_no = (last.data[0]["activity_no"] + 1) if last.data else 1
    supabase.table("activities").insert({
        "course_id": course_id,
        "activity_no": activity_no,
        "activity_text": activity_text,
        "learning_objectives": learning_objectives,
        "status": "NOT_STARTED",
    }).execute()
    return {"ok": True, "activity_no": activity_no}

def updateActivity(email: str, password: str, course_id: str, activity_no: int, patch: dict) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_instructors").select("*").eq("instructor_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    if not patch:
        return {"ok": False, "error": "Empty patch"}
    existing = supabase.table("activities").select("*").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    if not existing.data:
        return {"ok": False, "error": "Activity not found"}
    allowed_fields = {"activity_text", "learning_objectives"}
    filtered_patch = {k: v for k, v in patch.items() if k in allowed_fields}
    if not filtered_patch:
        return{"ok": False, "error": "No allowed fields in patch"}
    supabase.table("activities").update(filtered_patch).eq("course_id", course_id).eq("activity_no", activity_no).execute()
    return {"ok": True}

def startActivity(email:str, password:str, course_id: str, activity_no: int) -> dict:
    instrcutor = _verify_instructor(email, password)
    if not instrcutor:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_instructors").select("*").eq("instructor_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    existing = supabase.table("activities").select("*").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    if not existing.data:
        return {"ok": False, "error": "Activity not found"}
    supabase.table("activities").update({"status": "ENDED"}).eq("course_id", course_id).eq("activity_no", activity_no).execute()
    return {"ok": True}

def endActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    instrcutor = _verify_instructor(email, password)
    if not instrcutor:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_instructors").select("*").eq("instructor_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    existing = supabase.table("activities").select("*").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    if not existing.data:
        return {"ok": False, "error": "Activity not found"}
    supabase.table("activites").update({"status": "ENDED"}).eq("course_id", course_id).eq("activity_no", activity_no).execute()
    return {"ok": True}

def exportScores(email: str, password: str, course_id: str, activity_no: int) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_instructors").select("*").eq("instructor_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    result = supabase.table("score_logs").select("*").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    if not result.data:
        return {"ok": True, "csv": "student_email,score,meta,created_at\n"}
    lines = ["student_email,score,meta,created_at"]
    for row in result.data:
        lines.append(f"{row['student_email']},{row['score']},{row.get('meta', '')},{row['created_at']}")
    return {"ok": True, "csv": "\n".join(lines)}

def resetActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_instructors").select("*").eq("instructor_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    supabase.table("score_logs").delete().eq("course_id", course_id).eq("activity_no", activity_no).execute()
    supabase.table("activities").update({"status": "ENDED"}).eq("course_id", course_id).eq("activity_no", activity_no).execute()
    return {"ok": True}

def resetStudentPassword(email: str, password: str, course_id: str, student_email: str, new_password: str) -> dict:
    instructor = _verify_instructor(email, password)
    if not instructor:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_instructors").select("*").eq("instructor_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    student = _get_student(student_email)
    if not student:
        return {"ok": False, "error": "Student not found"}
    hashed = _hash_password(new_password)
    supabase.table("students").update({"password_hash": hashed}).eq("email", student_email).execute()
    return {"ok": True}


#--Student--

def getActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    student = _verify_student(email, password)
    if not student:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_students").select("*").eq("student_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    result = supabase.table("activities").select("*").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    if not result.data:
        return {"ok": False, "error": "Activity not found"}
    activity = result.data[0]
    if activity["status"] == "NOT_STARTED":
        return {"ok": False, "error": "Activity not started yet"}
    if activity["status"] == "ENDED":
        return {"ok": False, "error": "Activity has ended"}
    return {
        "ok": True,
        "activity_no": activity["activity_no"],
        "activity_text": activity["activity_text"],
        "status": activity["status"]
    }

def logScore(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str | None = None) -> dict:
    student = _verify_student(email, password)
    if not student:
        return {"ok": False, "error": "Invalid credentials"}
    access = supabase.table("course_students").select("*").eq("student_email", email).eq("course_id", course_id).execute()
    if not access.data:
        return {"ok": False, "error": "Access denied"}
    activity = supabase.table("activities").select("status").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    if not activity.data:
        return {"ok": False, "error": "Activity not found"}
    if activity.data[0]["status"] != "ACTIVE":
        return {"ok": False, "error": "Activity is not active"}
    supabase.table("score_logs").insert({
        "course_id": course_id,
        "activity_no": activity_no,
        "student_email": email,
        "score": score,
        "meta": meta
    }).execute()
    return {"ok": True}