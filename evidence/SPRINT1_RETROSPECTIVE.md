# Sprint 1 Retrospective Record

## Project

InClass Platform

## Sprint

Sprint 1


## Participants

- Demir Çalışır
- Berke Karakuş
- El Celil Erden
- Kıvanç Akay
- Efe Günay

## Sprint 1 Goal Review

Sprint 1 goal was to build the foundation of the InClass Platform by setting up PostgreSQL, backend structure, authentication, basic role separation, and initial course/activity listing.

The team mostly achieved the Sprint 1 goal. The basic project foundation was created, but some frontend/backend naming inconsistencies and old unused files caused confusion.

---

## What Went Well

- PostgreSQL database setup was completed.
- Initial FastAPI backend structure was created.
- Basic login and register functionality was implemented.
- Initial frontend pages were created.
- Course and activity listing endpoints were started.
- The team identified the main demo-critical features needed for Sprint 2.

---

## What Did Not Go Well

- Some old files from a previous activity tracking idea remained in the project.
- Frontend localStorage naming was inconsistent.
- Some backend and frontend endpoints did not match at first.
- The first version of the project had too much logic inside `main.py`.
- The team needed clearer folder structure earlier.

---

## What Can Be Improved

- Clean unused files earlier.
- Keep a consistent API contract between frontend and backend.
- Move sensitive values to `.env` from the beginning.
- Split backend into clearer files such as `database.py`, `models.py`, and `main.py`.
- Prepare demo seed data earlier.

---

## Action Items for Sprint 2

| Action Item | Owner | Priority | Status |
|---|---|---|---|
| Clean unused frontend pages | Demir Çalışır | High | Planned |
| Standardize frontend localStorage keys | Berke Karakuş | High | Planned |
| Move database URL and API key to `.env` | Berke Karakuş | High | Planned |
| Add server-side authorization | Efe Günay | High | Planned |
| Implement AI tutoring flow | El Celil Erden | High | Planned |
| Implement objective-based scoring | Kıvanç Akay | High | Planned |
| Prepare final demo seed data | Demir Çalışır | Medium | Planned |

---

## Retrospective Outcome

The team agreed to use Sprint 2 to complete the end-to-end product and remove confusion caused by mixed project structures. The main improvement target was to make the project demo-ready with clear authorization, AI tutoring, objective-based scoring, and evidence files.