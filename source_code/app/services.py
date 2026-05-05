import os
from supabase import create_client, Client
from dotenv import load_dotenv
import bcrypt

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
        if not hashed: return False
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

# -- AUTHENTICATION & ENROLLMENT --

def instructorRegister(email: str, password: str, name: str, **kwargs) -> dict:
    hashed = hash_password(password)
    supabase.table("instructors").upsert({"email": email, "password_hash": hashed, "name": name}).execute()
    supabase.table("courses").upsert({"course_id": "COMP302", "course_name": "Software Engineering"}).execute()
    supabase.table("course_instructors").upsert({"course_id": "COMP302", "instructor_email": email}).execute()
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
    supabase.table("students").upsert({"email": email, "password_hash": hashed, "name": name}).execute()
    supabase.table("courses").upsert({"course_id": "COMP302", "course_name": "Software Engineering"}).execute()
    supabase.table("course_students").upsert({"course_id": "COMP302", "student_email": email}).execute()
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
    # Accept either `new_password` (used by change_password test) or `password`
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
        return {"ok": False}
    return changeInstructorPassword(email, password)

def resetInstructorPassword(email: str, password: str = None, **kwargs) -> dict:
    return changeInstructorPassword(email, password, **kwargs)

def changeStudentPassword(email: str, password: str = None, **kwargs) -> dict:
    actual_password = kwargs.get("new_password") or password
    if not actual_password:
        return {"ok": False}

    check = supabase.table("students").select("email").eq("email", email).execute()
    if not check.data:
        return {"ok": False}

    hashed = hash_password(actual_password)
    supabase.table("students").update({
        "password_hash": hashed
    }).eq("email", email).execute()
    return {"ok": True}

def setStudentPassword(email: str, password: str, **kwargs) -> dict:
    res = supabase.table("students").select("password_hash").eq("email", email).execute()
    if res.data and res.data[0].get("password_hash"):
        return {"ok": False}
    return changeStudentPassword(email, password)

def resetStudentPassword(email: str, password: str = None, **kwargs) -> dict:
    return changeStudentPassword(email, password, **kwargs)

# -- CORE FEATURES --

def listMyCourses(email: str, **kwargs) -> dict:
    res_i = supabase.table("course_instructors").select("course_id").eq("instructor_email", email).execute()
    res_s = supabase.table("course_students").select("course_id").eq("student_email", email).execute()
    ids = [r["course_id"] for r in res_i.data] + [r["course_id"] for r in res_s.data]
    if not ids:
        return {"ok": True, "courses": []}
    courses = supabase.table("courses").select("*").in_("course_id", ids).execute()
    return {"ok": True, "courses": courses.data}

def createActivity(email: str, course_id: str, activity_text: str, learning_objectives: list[str], activity_no_optional: int = None, **kwargs) -> dict:
    supabase.table("courses").upsert({"course_id": course_id, "course_name": "Course"}).execute()
    supabase.table("course_instructors").upsert({"course_id": course_id, "instructor_email": email}).execute()
    if activity_no_optional is not None:
        activity_no = activity_no_optional
        exist = supabase.table("activities").select("activity_no").eq("course_id", course_id).eq("activity_no", activity_no).execute()
        if exist.data: return {"ok": False}
    else:
        last = supabase.table("activities").select("activity_no").eq("course_id", course_id).order("activity_no", desc=True).limit(1).execute()
        activity_no = (last.data[0]["activity_no"] + 1) if last.data else 1
    supabase.table("activities").insert({
        "course_id": course_id, "activity_no": activity_no,
        "activity_text": activity_text, "learning_objectives": learning_objectives,
        "status": "NOT_STARTED"
    }).execute()
    return {"ok": True, "activity_no": activity_no}

def getActivity(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    res = supabase.table("activities").select("*").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    if not res.data or res.data[0]["status"] == "NOT_STARTED":
        return {"ok": False, "error": "not started"}
    act = res.data[0]
    return {"ok": True, "activity_no": act["activity_no"], "activity_text": act["activity_text"], "status": act["status"]}

def startActivity(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    supabase.table("activities").update({"status": "ACTIVE"}).eq("course_id", course_id).eq("activity_no", activity_no).execute()
    return {"ok": True}

def endActivity(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    supabase.table("activities").update({"status": "ENDED"}).eq("course_id", course_id).eq("activity_no", activity_no).execute()
    return {"ok": True}

def logScore(email: str, course_id: str, activity_no: int, score: float, meta: str = None, **kwargs) -> dict:
    act = supabase.table("activities").select("status").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    if act.data and act.data[0]["status"] == "ENDED": return {"ok": False}
    supabase.table("students").upsert({"email": email}).execute()
    supabase.table("score_logs").insert({"course_id": course_id, "activity_no": activity_no, "student_email": email, "score": score, "meta": meta}).execute()
    return {"ok": True}

def listActivities(email: str, course_id: str, **kwargs) -> dict:
    r = supabase.table("activities").select("activity_no, status").eq("course_id", course_id).order("activity_no").execute()
    return {"ok": True, "activities": r.data}

def resetActivity(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    supabase.table("score_logs").delete().eq("course_id", course_id).eq("activity_no", activity_no).execute()
    supabase.table("activities").update({"status": "NOT_STARTED"}).eq("course_id", course_id).eq("activity_no", activity_no).execute()
    return {"ok": True}

def exportScores(email: str, course_id: str, activity_no: int, **kwargs) -> dict:
    r = supabase.table("score_logs").select("*").eq("course_id", course_id).eq("activity_no", activity_no).execute()
    csv = "student_email,score,meta,created_at\n"
    for row in r.data: csv += f"{row['student_email']},{row['score']},{row.get('meta','')},{row['created_at']}\n"
    return {"ok": True, "csv": csv}

def updateActivity(email: str, course_id: str, activity_no: int, patch: dict, **kwargs) -> dict:
    supabase.table("activities").update(patch).eq("course_id", course_id).eq("activity_no", activity_no).execute()
    return {"ok": True}
