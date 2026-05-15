# Product Backlog

## Project Name

InClass Platform

## Product Backlog with Initial Story Points

| Story ID | User Story | Initial SP | Priority | Notes |
|---|---|---:|---|---|
| US-A | As an instructor, I want to sign in so that I can use instructor functions securely. | 3 | High | Instructor authentication |
| US-B | As a student, I want to sign in so that I can use student functions securely. | 3 | High | Student authentication |
| US-C | As a system, I want to map users to roles and course access so that protected resources are secure. | 5 | High | Server-side role and course authorization |
| US-D | As an instructor, I want to list only my assigned courses so that I cannot access unrelated courses. | 3 | High | Instructor course authorization |
| US-E | As an instructor, I want to list activities in a selected course so that I can manage class activities. | 3 | High | Activity listing by course |
| US-F | As an instructor, I want to create a new activity with text and objectives so that I can prepare class activities. | 5 | High | Activity create |
| US-G | As an instructor, I want to update activity text and objectives so that I can revise activities before class. | 5 | High | Activity update |
| US-H | As an instructor, I want to start and end an activity so that class timing is controlled. | 5 | High | Activity status management |
| US-I | As a student, I want to access activity content only when the activity is ACTIVE so that class rules are enforced. | 5 | High | Student access control |
| US-J | As a student, I want to submit answers and receive guiding questions so that I can progress step by step. | 8 | High | AI tutoring flow |
| US-K | As a system, I want to increase score when an objective is achieved so that grading is objective based. | 8 | High | Objective-based scoring and score logs |
| US-L | As an instructor, I want to enter manual grades for exceptions so that classroom disruptions can be handled. | 5 | Medium | Manual grading |
| US-M | As an instructor, I want to reset an activity by deleting scores and closing the activity so that incorrect runs can be cleaned safely. | 5 | Medium | Reset activity |

## Total Initial Estimate

63 story points

## Notes

- The backlog was planned across two sprints.
- Sprint 1 focused on database setup, authentication, basic course and activity listing.
- Sprint 2 focused on authorization, AI tutoring, objective-based scoring, score logs, manual grading, reset behavior, and demo readiness.
- Each story required backend, frontend, PostgreSQL persistence where needed, and test evidence.