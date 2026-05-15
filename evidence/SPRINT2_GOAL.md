# Sprint 2 Goal

## Project

InClass Platform

## Sprint

Sprint 2

## Sprint Goal

The goal of Sprint 2 is to complete the end-to-end demo-ready InClass Platform by implementing instructor activity management, student ACTIVE activity access control, AI tutoring, objective-based scoring, score logs, manual grading, reset behavior, and final evidence preparation.

## Sprint 2 Focus

Sprint 2 focuses on:

- Token-based protected backend requests.
- Server-side role authorization.
- Server-side course authorization.
- Instructor activity create, update, list, start, end, and reset features.
- Student access only to enrolled and ACTIVE activities.
- AI tutoring flow with one guiding question at a time.
- Objective-based scoring.
- Duplicate score prevention for repeated objectives.
- Mini-lesson behavior after scoring.
- Activity completion behavior.
- Score logs with metadata.
- Manual grading for exceptional cases.
- Demo seed data.
- Acceptance test matrix and screenshots.

## Sprint 2 Success Criteria

Sprint 2 is successful if:

1. Instructor A can log in and see only COMP302.
2. Instructor B cannot access COMP302.
3. Student 1 can access COMP302 because the student is enrolled.
4. Student 2 cannot access COMP302 because the student is not enrolled.
5. Student 1 cannot access NOT_STARTED activities.
6. Student 1 can access Activity 1 after Instructor A starts it.
7. Student sees activity text but not learning objectives.
8. AI tutor guides the student in English with one question at a time.
9. First objective achievement gives exactly +1 point.
10. Repeating the same objective does not give another point.
11. Score logs include student, course, activity, score delta, updated score, event type, and metadata.
12. Mini-lesson appears after objective scoring.
13. Activity completes when all objectives are covered.
14. Instructor can manually grade a student.
15. Instructor can reset an activity.
16. ENDED or reset activities block further student work.
17. Final demo data can be loaded with a seed command.

## Sprint 2 Demo Scope

At the end of Sprint 2, the team should be able to demonstrate:

- Instructor login.
- Student login.
- Course authorization.
- Activity listing.
- Activity create and update.
- Activity start and end.
- Student ACTIVE activity access.
- AI tutoring flow.
- Objective-based scoring.
- Score logs metadata.
- Manual grading.
- Reset behavior.
- Unauthorized student and instructor rejection.

## Notes

Sprint 2 completes the core product required for the final demo and prepares evidence files for submission.