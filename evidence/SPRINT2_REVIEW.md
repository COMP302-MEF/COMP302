# Sprint 2 Review Record

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

## Sprint Goal

Complete the end-to-end demo-ready InClass Platform by implementing protected backend authorization, instructor activity management, student ACTIVE activity access, AI tutoring, objective-based scoring, score logs, manual grading, reset behavior, and final demo evidence.

## Completed Work

| Item | Related Story | Result |
|---|---|---|
| Token-based protected backend requests | US-C | Completed |
| Server-side role authorization | US-C | Completed |
| Server-side course authorization | US-C | Completed |
| Instructor assigned course listing | US-D | Completed |
| Course activity listing | US-E | Completed |
| Activity create | US-F | Completed |
| Activity update | US-G | Completed |
| Activity start/end | US-H | Completed |
| Student ACTIVE activity access | US-I | Completed |
| AI tutoring flow | US-J | Completed |
| Student progress storage | US-J | Completed |
| Objective-based scoring | US-K | Completed |
| Duplicate score prevention | US-K | Completed |
| Mini-lesson after scoring | US-K | Completed |
| Activity completion behavior | US-K | Completed |
| Score logs with metadata | US-K | Completed |
| Manual grading | US-L | Completed |
| Activity reset | US-M | Completed |
| Demo seed data | Demo | Completed |
| Acceptance test matrix | Evidence | Completed |

## Demonstrated During Review

The team demonstrated:

1. Instructor A login.
2. Instructor A can see only COMP302.
3. Instructor B cannot access COMP302.
4. Activity list shows activity number and status.
5. Instructor can create or update activity.
6. Student 1 cannot access NOT_STARTED activity.
7. Instructor A starts Activity 1.
8. Student 1 can access ACTIVE Activity 1.
9. Student sees activity text but not learning objectives.
10. AI tutor asks one guiding question at a time.
11. First objective achievement gives +1 point.
12. Repeating the same objective does not give duplicate score.
13. Mini-lesson appears after objective scoring.
14. Score logs show metadata.
15. Manual grade creates MANUAL_GRADE log.
16. Reset clears scores/progress and sets activity to ENDED.
17. Student 2 cannot access COMP302.


## Feedback Received

| Feedback | Action Taken |
|---|---|
| AI service errors should be visible during debugging. | Added backend error handling and terminal logs for AI service errors. |
| Score logs button did not show logs initially. | Fixed instructor dashboard logs button and added score log table. |
| API key was incorrectly configured during testing. | Moved API key to `.env` and used OpenRouter key format. |
| Frontend files were missing during integration. | Restored frontend files and connected them to token-based backend. |

## Sprint 2 Review Outcome

Sprint 2 completed the final demo-ready product. The team was able to demonstrate the required instructor, student, AI tutoring, scoring, logging, manual grading, reset, and authorization behavior end to end through the frontend and backend.