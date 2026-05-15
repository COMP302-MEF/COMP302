# Acceptance Criteria and Tutoring Flow Test Evidence Matrix

## Project: InClass Platform

| Story | Requirement / Acceptance Criteria | Test Steps | Expected Result | Actual Result | Evidence |
|---|---|---|---|---|---|
| US-A | Instructor can authenticate successfully | Login with `hoca_a@test.com / 123` | Instructor dashboard opens | PASS | Screenshot: instructor_login.png |
| US-B | Student can authenticate successfully | Login with `ogr_1@test.com / 123` | Student panel opens | PASS | Screenshot: student_login.png |
| US-C | Backend enforces role and course authorization | Login as Instructor B and check courses | Instructor B cannot see COMP302 | PASS | Screenshot: instructor_b_no_comp302.png |
| US-D | Instructor sees only assigned courses | Login as Instructor A | Only COMP302 appears | PASS | Screenshot: instructor_a_courses.png |
| US-E | Instructor lists activities in selected course | Click COMP302 | Activity 1 and Activity 2 appear in order | PASS | Screenshot: activity_list.png |
| US-F | Instructor creates activity with text and objectives | Create Activity No 3 | Activity 3 appears as NOT_STARTED | PASS | Screenshot: activity_create.png |
| US-F | Duplicate activity number rejected | Try creating Activity No 3 again | Clear duplicate error appears | PASS | Screenshot: duplicate_activity_no.png |
| US-G | Instructor updates allowed activity fields | Edit title/text/objectives | Updated activity appears | PASS | Screenshot: activity_update.png |
| US-G | Empty or invalid update rejected | Send empty update or invalid field | Clear error appears | PASS | Screenshot: invalid_update.png |
| US-H | Instructor starts activity | Press Start on Activity 1 | Status becomes ACTIVE | PASS | Screenshot: activity_active.png |
| US-H | Instructor ends activity | Press End on Activity 1 | Status becomes ENDED | PASS | Screenshot: activity_ended.png |
| US-I | NOT_STARTED activity inaccessible to student | Login as Student 1 before start | Activity does not appear | PASS | Screenshot: student_no_active_activity.png |
| US-I | ACTIVE activity accessible to enrolled student | Start Activity 1, login as Student 1 | Activity appears and opens | PASS | Screenshot: student_active_activity.png |
| US-I | Objectives are not exposed to student | Open active activity as Student 1 | Activity text visible, objectives hidden | PASS | Screenshot: objectives_hidden.png |
| US-I | Unauthorized student rejected | Login as Student 2 | COMP302 / Activity 1 not visible | PASS | Screenshot: student2_rejected.png |
| US-J | Tutoring flow asks one question at a time | Student sends answer | AI gives one guiding question | PASS | Screenshot: ai_guiding_question.png |
| US-J | Student progress is stored | Continue chat and refresh/check progress | Progress persists for student/activity | PASS | Screenshot: student_progress.png |
| US-K | First objective achievement gives +1 | Student explains retrieval practice | Score delta +1, updated score shown | PASS | Screenshot: objective_0_score.png |
| US-K | Repeating same objective does not give another point | Student repeats same idea | Score does not increase again | PASS | Screenshot: repeated_objective_no_score.png |
| US-K | Score log metadata stored | Open Logs as Instructor A | Metadata includes source, objective_text, student_message | PASS | Screenshot: score_logs_metadata.png |
| US-K | Mini-lesson shown after point | Objective achieved | Mini-lesson appears after score update | PASS | Screenshot: mini_lesson.png |
| US-K | Completion after all objectives | Student covers all objectives | Completion message appears and chat stops | PASS | Screenshot: activity_complete.png |
| US-L | Manual grade can be submitted by authorized instructor | Instructor A adds manual grade for Student 1 | MANUAL_GRADE log appears | PASS | Screenshot: manual_grade_log.png |
| US-L | Unauthorized instructor cannot submit manual grade | Instructor B attempts access | 403 / no access | PASS | Screenshot: manual_grade_unauthorized.png |
| US-M | Reset deletes scores/progress and closes activity | Instructor A resets Activity 1 | Logs/progress cleared, status ENDED | PASS | Screenshot: reset_result.png |
| US-M | Reset activity blocks further scoring | Student tries after reset | Activity inaccessible / 403 | PASS | Screenshot: reset_blocks_student.png |

## Notes

- Demo database is reset with `python seed.py` before the demo.
- Backend runs with PostgreSQL.
- Frontend uses token-based requests.
- Score logs include metadata for AI objective scoring and manual grading.