import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app import services

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI()

#--Student Auth--

@app.post("/student/login")
def studentLogin(email: str, password: str):
    return services.setStudentPassword(email=email, password=password)

@app.post("/student/set-password")
def studentSetPassword(email: str, password: str):
    return services.setStudentPassword(email=email, password=password)

app.post("/student/set-password")
def changeStudentPassword(email: str, password: str, new_password: str, old_password: str):
    return services.changeStudentPassword(email=email, password=password, new_password=new_password, old_password=old_password)


#--Instructor Auth--

@app.post("/instructor/login")
def instructorLogin(email: str, password: str):
    return services.instructorLogin(email=email, password=password)

@app.post("/instructor/set-password")
def setInstructorPassword(email: str, password: str = None):
    return services.setInstructorPassword(email=email, password=password)

@app.post("/instructor/change-password")
def changeInstructorPassword(email: str, password: str, old_password: str, new_password: str):
    return services.changeInstructorPassword(email=email, password=password, old_password=old_password, new_password=new_password)

#--Instructor--

@app.post("/instructor/list-my-mcourses")
def listMyCourses(email: str, password: str):
    return services.listMyCourses(email=email, password=password)

@app.post("/instructor/list-activities")
def listActivities(email: str, password: str, course_id: str):
    return services.listActivities(email=email, password=password, course_id=course_id)

@app.post("/instructor/create-activity")
def createActivity(email: str, password: str, course_id: str, activity_text: str, learning_objectives: list[str], activity_no_optional: int = None):
    return services.createActivity(email=email, password=password, course_id=course_id, activity_text=activity_text, learning_objectives=learning_objectives, activity_no_optional=activity_no_optional)

@app.post("/instructor/update-activity")
def updateActivity(email: str, password: str, course_id: str, activity_no: int, patch: dict):
    return services.updateActivity(email=email, password=password, course_id=course_id, activity_id=activity_no, patch=patch)

@app.post("/instructor/start-activity")
def startActivity(email: str, password: str, course_id: str, activity_no: int):
    return services.startActivity(email=email, password=password, course_id=course_id, activity_no=activity_no)

@app.post("/instructor/end-activity")
def endActivity(email: str, password: str, course_id: str, activity_no: int):
    return services.endActivity(email=email, password=password, course_id=course_id, activity_no=activity_no)

@app.post("/instructor/export-scores")
def exportScores(email: str, password: str, course_id: str, activity_no: int):
    return services.exportScores(email=email, password=password, course_id=course_id, activity_no=activity_no)

@app.post("instructor/reset-activity")
def resetActivity(email: str, password: str, course_id: str, activity_no: int):
    return services.resetActivity(email=email, password=password, course_id=course_id, activity_no=activity_no)

@app.post("/instructor/reset-student-password")
def resetStudentPassword(email: str, password: str, course_id: str, student_email: str, new_password: str):
    return services.resetStudentPassword(email=email, password=password, course_id=course_id, student_email=student_email, new_password=new_password)

#--Student--

@app.post("/student/get-activity")
def getActivity(email: str, password: str, course_id: str, activity_no: int):
    return services.getActivity(email=email, password=password, course_id=course_id, activity_no=activity_no)

@app.post("/student/log-score")
def logScore(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str = None):
    return services.logScore(email=email,password=password, course_id=course_id, activity_no=activity_no, score=score, meta=meta)