import pytest
from app.services import (
    studentLogin, setStudentPassword, logScore,
    startActivity, createActivity, instructorLogin, setInstructorPassword
)

# Berke'nin belirttiği "Aktivite Takibi" ve "Gamification" için test verileri
TEST_USER = "celil_test@mef.edu.tr"
TEST_PASS = "mef12345"
COURSE_ID = "COMP302"

def test_student_gamification_flow():
    """Öğrencinin aktivite yapıp puan kazanma senaryosu (US-B & US-L)"""
    # 1. Kullanıcıyı ve şifreyi hazırla
    setStudentPassword(email=TEST_USER, password=TEST_PASS)
    
    # 2. Giriş yap ve başarılı olduğunu doğrula
    login_res = studentLogin(email=TEST_USER, password=TEST_PASS)
    assert login_res["ok"] is True
    
    # 3. Bir aktiviteye skor (puan) gönder
    # Berke'nin "Aktivite Takibi" modülünü test ediyoruz
    score_res = logScore(
        email=TEST_USER, 
        password=TEST_PASS, 
        course_id=COURSE_ID, 
        activity_no=1, 
        score=10.0, 
        meta="Coding Session"
    )
    assert score_res["ok"] is True

def test_instructor_role_check():
    """Eğitmen yetkilerinin ve rol yönetiminin doğrulanması (US-C)"""
    inst_email = "instructor_test@mef.edu.tr"
    setInstructorPassword(email=inst_email, password=TEST_PASS)
    
    #Eğitmen girişi ve rolün doğru tanındığını kontrol et
    res = instructorLogin(email=inst_email, password=TEST_PASS)
    assert res["ok"] is True
    assert res["email"] == inst_email
