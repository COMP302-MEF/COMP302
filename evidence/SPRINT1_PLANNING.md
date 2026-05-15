# Sprint 1 Planning Record

## Project

InClass Platform

## Sprint

Sprint 1

## Sprint Duration

2 weeks


## Participants

- Demir Çalışır
- Berke Karakuş
- El Celil Erden
- Kıvanç Akay
- Efe Günay

## Sprint Goal

Build the foundation of the InClass Platform by setting up PostgreSQL, backend structure, authentication, basic role separation, and initial course/activity listing.

## Team Capacity

| Item | Value |
|---|---:|
| Sprint length | 2 weeks |
| Team velocity input | 35 SP |
| Planned Sprint 1 scope | 23 SP |

## Selected Stories and Tasks

| Task ID | Related Story | Task Description | Estimate | Owner | Status at Planning |
|---|---|---|---:|---|---|
| S1-T01 | US-A / US-B | Create login and register frontend pages | 3 | Team Member | To Do |
| S1-T02 | US-A / US-B | Implement backend login and register endpoints | 3 | Team Member | To Do |
| S1-T03 | US-C | Create initial User, Course, Enrollment, and Activity models | 5 | Team Member | To Do |
| S1-T04 | US-D | Implement instructor assigned course listing | 3 | Team Member | To Do |
| S1-T05 | US-E | Implement course activity listing endpoint | 3 | Team Member | To Do |
| S1-T06 | Setup | Configure PostgreSQL database connection | 3 | Team Member | To Do |
| S1-T07 | Setup | Prepare initial seed data | 3 | Team Member | To Do |

## Planning Discussion

The team decided to focus Sprint 1 on creating the technical foundation needed for the InClass Platform. Authentication, database setup, and basic course/activity listing were selected first because later Sprint 2 features depend on these foundations.

The AI tutoring flow, objective-based scoring, manual grading, and reset behavior were intentionally left for Sprint 2 because they require the role/course authorization and activity data model to be stable first.

## Risks Identified

| Risk | Mitigation |
|---|---|
| PostgreSQL connection issues | Test database connection early and document setup steps |
| Frontend/backend field mismatch | Keep shared API expectations clear |
| Role authorization confusion | Start with simple role field and improve in Sprint 2 |
| Time loss from old unused files | Clean unused code before Sprint 2 |

## Definition of Done Reminder

A Sprint 1 item is considered done when:

- Backend endpoint or model is implemented.
- Frontend can call the endpoint where applicable.
- PostgreSQL connection works.
- Basic test with demo data passes.
- Code is committed to GitHub.
- Task is updated in ClickUp.

## Expected Sprint 1 Review Output

By the end of Sprint 1, the team expects to show:

- Running FastAPI backend.
- PostgreSQL connection.
- Login and register pages.
- Basic instructor dashboard.
- Basic student panel.
- Course listing.
- Activity listing.