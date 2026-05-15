# Sprint 2 Retrospective Record

## Project

InClass Platform

## Sprint

Sprint 2


## Participants

- Demir Çalışır
- Berke Karakuş
- El Celil Erden
- Kıvanç Akay
- Efe Günay

## Sprint 2 Goal Review

Sprint 2 goal was to complete the end-to-end demo-ready InClass Platform by implementing protected backend authorization, instructor activity management, student ACTIVE activity access, AI tutoring, objective-based scoring, score logs, manual grading, reset behavior, and final evidence preparation.

The team achieved the Sprint 2 goal. The final system supports instructor and student login, server-side authorization, activity management, AI tutoring, objective-based scoring, score logs, manual grading, reset behavior, and demo data preparation.

---

## What Went Well

- Token-based protected backend requests were implemented.
- Server-side role and course authorization worked.
- Instructor activity management was completed.
- Student access was limited to enrolled and ACTIVE activities.
- AI tutoring flow worked from the student frontend.
- Objective-based scoring was implemented.
- Duplicate scoring was prevented.
- Score logs with metadata were shown in the instructor dashboard.
- Manual grading and reset behavior were completed.
- Demo seed data made testing easier.
- Final demo flow was tested end to end.

---

## What Did Not Go Well

- API key configuration caused 401 and 502 errors during testing.
- The wrong API key type was initially used for the AI service.
- Some frontend files were lost and had to be restored.
- The score logs button did not work at first.
- Some old files from the previous project idea caused confusion.
- Evidence files were prepared late.

---

## What Can Be Improved

- Keep `.env.example` ready from the beginning.
- Never place real API keys inside source code.
- Test AI service configuration earlier.
- Keep frontend files backed up.
- Prepare evidence screenshots during the sprint instead of at the end.
- Make commit messages more meaningful.
- Keep ClickUp task updates synchronized with GitHub commits.

---

## Action Items for Future Projects

| Action Item | Owner | Priority | Status |
|---|---|---|---|
| Create `.env.example` at project start | Berke Karakuş | High | Done |
| Keep real `.env` out of GitHub | Demir Çalışır | High | Done |
| Use meaningful commit messages | Demir Çalışır | Medium | Planned |
| Capture screenshots during development | Berke Karakuş | Medium | Planned |
| Test API keys before demo week | Efe Günay | High | Done |
| Keep ClickUp task history updated | El Celil Erden | High | Planned |
| Maintain a clean source code folder structure | Kıvanç Akay | High | Done |

---

## Retrospective Outcome

The team completed the final product and prepared the required demo behavior. The most important lesson from Sprint 2 was that environment configuration, frontend/backend consistency, and evidence preparation should be handled earlier to reduce final integration risk.