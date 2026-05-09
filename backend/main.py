from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models

app = FastAPI()

# US-C: Kullanıcının Rolünü ve Yetkisini Kontrol Etme
@app.get("/user/verify/{email}")
def verify_user_access(email: str, db: Session = Depends(get_db)):
    # Veritabanında kullanıcıyı bul
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # Rol kontrolü ve kurs eşleştirme
    response = {
        "full_name": user.full_name,
        "role": user.role,
        "is_instructor": user.role == "instructor"
    }

    # Eğer eğitmense, yönettiği kursları getir
    if user.role == "instructor":
        courses = db.query(models.Course).filter(models.Course.instructor_id == user.id).all()
        response["managed_courses"] = [c.course_code for c in courses]
        response["access_level"] = "Full (Course Management)"
    else:
        response["access_level"] = "Limited (Student View)"
        
    return response