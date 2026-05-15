# Sprint 2 Backlog

## Project

InClass Platform

## Sprint

Sprint 2

## Sprint Goal

Complete the end-to-end demo-ready InClass Platform by implementing protected backend authorization, instructor activity management, student ACTIVE activity access, AI tutoring, objective-based scoring, score logs, manual grading, reset behavior, and final demo evidence.

## Sprint 2 Task Breakdown

| Task ID | Related Story | Task Description | Estimate | Owner | Status |
|---|---|---|---:|---|---|
| S2-T01 | US-C | Add token-based authentication to backend | 3 SP | Berke Karakuş | Done |
| S2-T02 | US-C | Add protected request handling in frontend | 2 SP | Berke Karakuş | Done |
| S2-T03 | US-C | Enforce server-side role authorization | 3 SP | Berke Karakuş | Done |
| S2-T04 | US-C | Enforce server-side course authorization | 3 SP | Berke Karakuş | Done |
| S2-T05 | US-F | Implement activity create backend endpoint | 3 SP | Berke Karakuş | Done |
| S2-T06 | US-F | Add activity create form to instructor dashboard | 2 SP | Demir Çalışır | Done |
| S2-T07 | US-G | Implement activity update backend endpoint | 3 SP | Demir Çalışır  | Done |
| S2-T08 | US-G | Add activity update UI to instructor dashboard | 2 SP | Demir Çalışır  | Done |
| S2-T09 | US-H | Implement activity start endpoint and UI | 2 SP | Demir Çalışır  | Done |
| S2-T10 | US-H | Implement activity end endpoint and UI | 2 SP | Demir Çalışır  | Done |
| S2-T11 | US-I | Restrict student access to enrolled courses | 3 SP | Kıvanç Akay | Done |
| S2-T12 | US-I | Restrict student access to ACTIVE activities only | 3 SP | Kıvanç Akay | Done |
| S2-T13 | US-J | Implement AI tutor chat endpoint | 5 SP | Kıvanç Akay | Done |
| S2-T14 | US-J | Add student chat frontend | 3 SP | Kıvanç Akay | Done |
| S2-T15 | US-J | Store student chat progress per activity | 3 SP | El Celil Erden | Done |
| S2-T16 | US-K | Implement objective achievement detection handling | 4 SP | El Celil Erden | Done |
| S2-T17 | US-K | Implement duplicate score prevention | 3 SP | El Celil Erden | Done |
| S2-T18 | US-K | Implement score logs with metadata | 3 SP | TEl Celil Erden | Done |
| S2-T19 | US-K | Show updated score and mini-lesson in frontend | 3 SP | El Celil Erden | Done |
| S2-T20 | US-K | Implement activity completion behavior | 2 SP | Efe Günay | Done |
| S2-T21 | US-L | Implement manual grade backend endpoint | 3 SP | Efe Günay | Done |
| S2-T22 | US-L | Add manual grade UI to instructor dashboard | 2 SP | Efe Günay | Done |
| S2-T23 | US-M | Implement reset activity backend endpoint | 3 SP | Efe Günay | Done |
| S2-T24 | US-M | Add reset UI to instructor dashboard | 2 SP | Efe Günay | Done |
| S2-T25 | Demo | Prepare clean demo seed data | 3 SP | Demir Çalışır | Done |
| S2-T26 | Evidence | Prepare acceptance test matrix | 2 SP | Berke Karakuş  | Done |
| S2-T27 | Evidence | Capture score log and demo screenshots | 2 SP | Efe Günay | Done |
| S2-T28 | Fix | Fix OpenRouter API key configuration issue | 1 SP | El Celil Erden | Done |
| S2-T29 | Fix | Restore missing frontend files | 1 SP | Kıvanç Akay | Done |

## Sprint 2 Total Estimate

75 SP

## Sprint 2 Notes

Sprint 2 focused on completing the final working product. The highest priority was the demo-critical path:

1. Instructor logs in and sees assigned course.
2. Instructor starts an activity.
3. Student accesses only ACTIVE and authorized activity.
4. Student chats with AI tutor.
5. Objective-based scoring gives +1 only once per objective.
6. Score logs store metadata.
7. Instructor can manually grade and reset activities.
8. Unauthorized users are rejected by backend authorization.

## Sprint 2 Output

At the end of Sprint 2, the project had:

- Token-based protected backend requests.
- Server-side role and course authorization.
- Instructor activity create, update, start, end, reset, and list features.
- Student ACTIVE activity access control.
- AI tutoring flow.
- Student progress persistence.
- Objective-based score handling.
- Duplicate scoring prevention.
- Score logs with metadata.
- Manual grade feature.
- Reset behavior.
- Demo seed data.
- Frontend working end to end.
- Acceptance test matrix and demo screenshots.