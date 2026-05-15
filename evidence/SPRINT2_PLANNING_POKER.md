# Sprint 2 Planning Poker Re-estimate Evidence

## Project

InClass Platform

## Sprint

Sprint 2

## Meeting Purpose

The purpose of this meeting was to review the remaining product backlog items and re-estimate the Sprint 2 scope using Planning Poker.

Sprint 2 focused on completing the end-to-end demo-ready product, including instructor activity management, student AI tutoring, objective-based scoring, manual grading, reset behavior, and final test evidence.

## Participants

- Demir Çalışır
- Berke Karakuş
- El Celil Erden
- Kıvanç Akay
- Efe Günay

## Selected Sprint 2 Stories

| Story ID | Story Summary | Initial SP | Re-estimated SP | Decision |
|---|---|---:|---:|---|
| US-C | Complete server-side role and course authorization | 5 | 5 | Kept |
| US-F | Instructor creates new activity with text and objectives | 5 | 5 | Kept |
| US-G | Instructor updates activity text and objectives | 5 | 5 | Kept |
| US-H | Instructor starts and ends activity | 5 | 5 | Kept |
| US-I | Student accesses only authorized ACTIVE activities | 5 | 5 | Kept |
| US-J | Student AI tutoring flow | 8 | 8 | Kept |
| US-K | Objective-based scoring, mini-lesson, and score logs | 8 | 8 | Kept |
| US-L | Instructor manual grading | 5 | 5 | Kept |
| US-M | Instructor reset activity | 5 | 5 | Kept |
| DEMO-1 | Demo seed data and final demo preparation | 3 | 3 | Added as demo task |
| EVIDENCE-1 | Acceptance test matrix and screenshots | 3 | 3 | Added as evidence task |

## Discussion Notes

- US-J and US-K were estimated as the largest items because the AI tutoring flow, JSON response handling, scoring rules, mini-lesson behavior, and score logs had to work together.
- Server-side authorization remained high priority because the frontend alone is not enough to protect restricted resources.
- Manual grading and reset were included because they are required final product features.
- Demo seed data was added as a separate task to make the final demo start from a known clean state.
- Evidence preparation was added because acceptance criteria and tutoring-flow evidence are required for submission.

## Final Sprint 2 Estimate

| Category | Story Points |
|---|---:|
| Product stories | 51 |
| Demo and evidence tasks | 6 |
| Total Sprint 2 Estimate | 57 |

## Re-estimation Result

The team agreed to keep the complete Sprint 2 scope because all remaining product stories were needed for the final demo. The team also agreed to prioritize the demo-critical path first:

1. Authorization
2. Activity start/end
3. Student ACTIVE activity access
4. AI tutoring
5. Objective scoring and score logs
6. Manual grading and reset
7. Final evidence preparation

## Evidence Notes

This file documents the Planning Poker re-estimation outcome for Sprint 2. The related task-level Sprint Backlog is documented separately in `SPRINT2_BACKLOG.md`.