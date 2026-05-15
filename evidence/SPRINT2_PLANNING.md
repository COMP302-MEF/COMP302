# Sprint 2 Planning Record

## Project

InClass Platform

## Sprint

Sprint 2

## Sprint Duration

2 weeks


## Participants

- Demir Çalışır
- Berke Karakuş
- El Celil Erden
- Kıvanç Akay
- Efe Günay

## Sprint Goal

Complete the end-to-end demo-ready InClass Platform by implementing protected backend authorization, instructor activity management, student ACTIVE activity access, AI tutoring, objective-based scoring, score logs, manual grading, reset behavior, and final demo evidence.

## Team Capacity

| Item | Value |
|---|---:|
| Sprint length | 2 weeks |
| Team velocity input | 35 SP |
| Planned Sprint 2 scope | 57 SP |

## Selected Stories and Tasks

| Task ID | Related Story | Task Description | Estimate | Owner | Status at Planning |
|---|---|---|---:|---|---|
| S2-T01 | US-C | Implement token-based protected backend requests | 5 | Berke Karakuş | To Do |
| S2-T02 | US-C | Enforce server-side role and course authorization | 5 | Berke Karakuş | To Do |
| S2-T03 | US-F | Implement instructor activity create endpoint and UI | 5 | Demir Çalışır | To Do |
| S2-T04 | US-G | Implement instructor activity update endpoint and UI | 5 | Demir Çalışır | To Do |
| S2-T05 | US-H | Implement activity start and end behavior | 5 | Kıvanç Akay | To Do |
| S2-T06 | US-I | Implement student ACTIVE activity access control | 5 | Kıvanç Akay | To Do |
| S2-T07 | US-J | Implement AI tutoring flow | 8 | Efe Günay | To Do |
| S2-T08 | US-K | Implement objective-based scoring and duplicate prevention | 8 | Efe Günay | To Do |
| S2-T09 | US-K | Implement score logs with metadata and mini-lesson behavior | 5 | El Celil Erden | To Do |
| S2-T10 | US-L | Implement instructor manual grading | 5 | El Celil Erden | To Do |
| S2-T11 | US-M | Implement activity reset behavior | 5 | Demir Çalışır | To Do |
| S2-T12 | Demo | Prepare final demo seed data | 3 | Berke Karakuş | To Do |
| S2-T13 | Evidence | Prepare acceptance test matrix and screenshots | 3 | Kıvanç Akay | To Do |

## Planning Discussion

The team selected the remaining stories required for a complete final demo. The highest priority items were server-side authorization, activity status control, student access control, AI tutoring, objective-based scoring, and score logs.

The team agreed that the demo-critical path should be implemented in this order:

1. Token-based authentication and authorization.
2. Instructor activity management.
3. Student ACTIVE activity access.
4. AI tutoring endpoint.
5. Objective-based scoring.
6. Score logs metadata.
7. Manual grading and reset.
8. Demo evidence and screenshots.

## Risks Identified

| Risk | Mitigation |
|---|---|
| AI service may return invalid JSON | Add JSON parsing safeguards and clear error messages |
| API key may be invalid or missing | Move API key to `.env` and test before demo |
| Students may access unauthorized activities if only frontend is checked | Enforce authorization in backend |
| Duplicate objective scoring may occur | Store achieved objectives in student progress |
| Demo data may be inconsistent | Use `python seed.py` before demo |
| Frontend and backend endpoints may mismatch | Test full demo flow after each backend change |

## Definition of Done Reminder

A Sprint 2 item is considered done when:

- Backend endpoint is implemented.
- PostgreSQL persistence is implemented.
- Server-side authorization is enforced.
- Frontend demonstrates the behavior end to end.
- Error cases return clear messages.
- Feature is tested with demo data.
- Evidence screenshot or test note is prepared.
- Code is committed to GitHub.
- Task is updated in ClickUp.

## Expected Sprint 2 Review Output

By the end of Sprint 2, the team expects to show:

- Instructor A can access only assigned courses.
- Student 1 can access only enrolled and ACTIVE activities.
- Unauthorized instructor and student access is rejected.
- Instructor can create, update, start, end, and reset activities.
- AI tutor guides students with one question at a time.
- Objective-based scoring works.
- Repeated objective achievement does not add duplicate points.
- Score logs include metadata.
- Instructor can manually grade.
- Final demo data is ready.