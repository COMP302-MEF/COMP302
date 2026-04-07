import pytest
from app.services import (
    instructorLogin, setInstructorPassword, changeInstructorPassword,
    studentLogin, setStudentPassword, changeStudentPassword,
    listMyCourses, listActivities, createActivity, updateActivity,
    startActivity, endActivity, resetActivity, exportScores,
    resetStudentPassword, getActivity, logScore,
    supabase
)

# ── Test verileri ──────────────────────────────────────────────────────────

INSTRUCTOR_EMAIL = "instructor1@mef.edu.tr"
INSTRUCTOR_PASSWORD = "testpass123"
STUDENT_EMAIL = "student1@mef.edu.tr"
STUDENT_PASSWORD = "testpass123"
COURSE_ID = "COMP101"
TEST_ACTIVITY_NO = 99  # test için özel numara, gerçek verilerle çakışmasın


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def cleanup():
    # test öncesi: instructor ve student şifrelerini sıfırla
    supabase.table("instructors").update({"password_hash": None}).eq("email", INSTRUCTOR_EMAIL).execute()
    supabase.table("students").update({"password_hash": None}).eq("email", STUDENT_EMAIL).execute()
    # test aktivitesini temizle
    supabase.table("score_logs").delete().eq("course_id", COURSE_ID).eq("activity_no", TEST_ACTIVITY_NO).execute()
    supabase.table("activities").delete().eq("course_id", COURSE_ID).eq("activity_no", TEST_ACTIVITY_NO).execute()

    yield  # test burada çalışır

    # test sonrası: aynı temizliği tekrar yap
    supabase.table("score_logs").delete().eq("course_id", COURSE_ID).eq("activity_no", TEST_ACTIVITY_NO).execute()
    supabase.table("activities").delete().eq("course_id", COURSE_ID).eq("activity_no", TEST_ACTIVITY_NO).execute()


# ── Instructor Auth testleri ───────────────────────────────────────────────

def test_set_instructor_password():
    result = setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    assert result["ok"] is True

def test_instructor_login_success():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    result = instructorLogin(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    assert result["ok"] is True
    assert result["email"] == INSTRUCTOR_EMAIL

def test_instructor_login_wrong_password():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    result = instructorLogin(email=INSTRUCTOR_EMAIL, password="wrongpass")
    assert result["ok"] is False

def test_set_instructor_password_twice_fails():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    result = setInstructorPassword(email=INSTRUCTOR_EMAIL, password="anotherpass")
    assert result["ok"] is False

def test_change_instructor_password():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    result = changeInstructorPassword(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        old_password=INSTRUCTOR_PASSWORD, new_password="newpass123"
    )
    assert result["ok"] is True
    login = instructorLogin(email=INSTRUCTOR_EMAIL, password="newpass123")
    assert login["ok"] is True


# ── Student Auth testleri ──────────────────────────────────────────────────

def test_set_student_password():
    result = setStudentPassword(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    assert result["ok"] is True

def test_student_login_success():
    setStudentPassword(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    result = studentLogin(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    assert result["ok"] is True
    assert result["email"] == STUDENT_EMAIL

def test_student_login_wrong_password():
    setStudentPassword(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    result = studentLogin(email=STUDENT_EMAIL, password="wrongpass")
    assert result["ok"] is False

def test_set_student_password_twice_fails():
    setStudentPassword(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    result = setStudentPassword(email=STUDENT_EMAIL, password="anotherpass")
    assert result["ok"] is False


# ── Instructor Main testleri ───────────────────────────────────────────────

def test_list_my_courses():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    result = listMyCourses(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    assert result["ok"] is True
    assert any(c["course_id"] == COURSE_ID for c in result["courses"])

def test_create_activity():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    result = createActivity(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        course_id=COURSE_ID,
        activity_text="Test activity",
        learning_objectives=["Objective 1", "Objective 2"],
        activity_no_optional=TEST_ACTIVITY_NO
    )
    assert result["ok"] is True
    assert result["activity_no"] == TEST_ACTIVITY_NO

def test_create_activity_duplicate_fails():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    createActivity(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        course_id=COURSE_ID,
        activity_text="Test activity",
        learning_objectives=["Objective 1"],
        activity_no_optional=TEST_ACTIVITY_NO
    )
    result = createActivity(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        course_id=COURSE_ID,
        activity_text="Duplicate activity",
        learning_objectives=["Objective 1"],
        activity_no_optional=TEST_ACTIVITY_NO
    )
    assert result["ok"] is False

def test_start_and_end_activity():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    createActivity(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        course_id=COURSE_ID,
        activity_text="Test activity",
        learning_objectives=["Objective 1"],
        activity_no_optional=TEST_ACTIVITY_NO
    )
    start = startActivity(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO)
    assert start["ok"] is True
    end = endActivity(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO)
    assert end["ok"] is True


# ── Student Main testleri ──────────────────────────────────────────────────

def test_get_activity_not_started():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    setStudentPassword(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    createActivity(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        course_id=COURSE_ID,
        activity_text="Test activity",
        learning_objectives=["Objective 1"],
        activity_no_optional=TEST_ACTIVITY_NO
    )
    result = getActivity(email=STUDENT_EMAIL, password=STUDENT_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO)
    assert result["ok"] is False
    assert "not started" in result["error"].lower()

def test_get_activity_active():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    setStudentPassword(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    createActivity(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        course_id=COURSE_ID,
        activity_text="Test activity",
        learning_objectives=["Objective 1"],
        activity_no_optional=TEST_ACTIVITY_NO
    )
    startActivity(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO)
    result = getActivity(email=STUDENT_EMAIL, password=STUDENT_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO)
    assert result["ok"] is True
    assert result["activity_text"] == "Test activity"
    assert "learning_objectives" not in result  # öğrenci hedefleri görmemeli

def test_log_score_active():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    setStudentPassword(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    createActivity(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        course_id=COURSE_ID,
        activity_text="Test activity",
        learning_objectives=["Objective 1"],
        activity_no_optional=TEST_ACTIVITY_NO
    )
    startActivity(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO)
    result = logScore(email=STUDENT_EMAIL, password=STUDENT_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO, score=1.0, meta="test")
    assert result["ok"] is True

def test_log_score_ended_fails():
    setInstructorPassword(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD)
    setStudentPassword(email=STUDENT_EMAIL, password=STUDENT_PASSWORD)
    createActivity(
        email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD,
        course_id=COURSE_ID,
        activity_text="Test activity",
        learning_objectives=["Objective 1"],
        activity_no_optional=TEST_ACTIVITY_NO
    )
    startActivity(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO)
    endActivity(email=INSTRUCTOR_EMAIL, password=INSTRUCTOR_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO)
    result = logScore(email=STUDENT_EMAIL, password=STUDENT_PASSWORD, course_id=COURSE_ID, activity_no=TEST_ACTIVITY_NO, score=1.0)
    assert result["ok"] is False