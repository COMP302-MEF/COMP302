# Product Goal

## Project Name

InClass Platform

## Product Goal

The goal of the InClass Platform is to build a working classroom activity system where instructors manage course activities and students participate only in authorized ACTIVE activities.

The platform supports objective-based AI tutoring. Students work on instructor-provided activity text, receive one guiding question at a time, and progress through learning objectives with the help of an AI tutor.

The system records objective-based scoring in PostgreSQL. When a student achieves a learning objective for the first time, the system gives exactly +1 point, updates the student's score, shows a short academic mini-lesson, and writes a score log with metadata.

## Main Product Capabilities

The final product demonstrates:

- Instructor and student authentication.
- Server-side role authorization.
- Server-side course authorization.
- Instructor access limited to assigned courses.
- Student access limited to enrolled courses.
- Student access only to ACTIVE activities.
- Instructor activity create, update, start, end, reset, and list features.
- AI tutoring flow with one guiding question at a time.
- Objective-based scoring.
- Duplicate score prevention for repeated objectives.
- Score logs with metadata.
- Manual grading for exceptional cases.
- PostgreSQL-backed persistence.

## Success Definition

The product is successful when the team can demonstrate an end-to-end flow where:

1. Instructor A logs in and sees only the assigned course.
2. Student 1 cannot access a NOT_STARTED activity.
3. Instructor A starts the activity.
4. Student 1 accesses the ACTIVE activity.
5. Student 1 sees the activity text but not the learning objectives.
6. The AI tutor guides the student step by step.
7. The system gives +1 when an objective is achieved for the first time.
8. Repeating the same objective does not give another point.
9. Score logs show student, course, activity, score change, and metadata.
10. Instructor A can end or reset the activity.
11. Unauthorized users cannot access restricted courses or activities.