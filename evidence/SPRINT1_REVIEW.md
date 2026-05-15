# Sprint 1 Review Record

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

## Sprint Goal

Build the foundation of the InClass Platform by setting up PostgreSQL, backend structure, authentication, basic role separation, and initial course/activity listing.

## Completed Work

| Item | Related Story | Result |
|---|---|---|
| Login frontend | US-A / US-B | Completed |
| Register frontend | US-A / US-B | Completed |
| Backend login endpoint | US-A / US-B | Completed |
| Backend register endpoint | US-A / US-B | Completed |
| PostgreSQL connection | Setup | Completed |
| User model | US-C | Completed |
| Course model | US-C / US-D | Completed |
| Enrollment model | US-C | Completed |
| Activity model draft | US-E | Completed |
| Course listing endpoint | US-D | Completed |
| Activity listing endpoint | US-E | Completed |
| Initial instructor dashboard | US-D / US-E | Completed |
| Initial student page | US-B / US-I | Completed |

## Demonstrated During Review

The team demonstrated:

1. FastAPI backend running.
2. PostgreSQL connection.
3. Login page.
4. Register page.
5. Instructor login.
6. Student login.
7. Basic instructor dashboard.
8. Basic course listing.
9. Basic activity listing.


## Feedback Received

| Feedback | Action Planned |
|---|---|
| Authorization should be enforced in backend, not only frontend. | Add token-based protected requests in Sprint 2. |
| Activity management needs create/update/start/end features. | Implement instructor activity management in Sprint 2. |
| Student access should depend on ACTIVE activity status. | Implement ACTIVE activity checks in Sprint 2. |
| AI tutoring and scoring must be completed for final demo. | Implement AI chat, scoring, and score logs in Sprint 2. |

## Sprint 1 Review Outcome

Sprint 1 achieved the foundation needed for the final product. The system had the initial backend, database, authentication draft, and basic frontend pages. The remaining demo-critical features were moved to Sprint 2.