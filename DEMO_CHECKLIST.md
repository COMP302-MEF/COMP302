# Demo Checklist - InClass Platform

## Before Demo

- [ ] Backend is running with `uvicorn main:app --reload`
- [ ] Frontend opens from `source_code/frontend/login.html`
- [ ] PostgreSQL is running
- [ ] `.env` file is configured
- [ ] OpenRouter API key is valid
- [ ] Demo database reset completed with `python seed.py`
- [ ] Test accounts verified
- [ ] Activity 1 starts as NOT_STARTED
- [ ] Score logs are clean
- [ ] Internet connection is ready

## Demo Accounts

| Role | Email | Password |
|---|---|---|
| Instructor A | hoca_a@test.com | 123 |
| Instructor B | hoca_b@test.com | 123 |
| Student 1 | ogr_1@test.com | 123 |
| Student 2 | ogr_2@test.com | 123 |

## Demo Flow

1. Login as Instructor A.
2. Show only COMP302 is visible.
3. Show Activity 1 and Activity 2 listed in order.
4. Create or update an activity.
5. Logout and login as Student 1 before activity start.
6. Show no active activity is visible.
7. Login as Instructor A and start Activity 1.
8. Login as Student 1 and open active Activity 1.
9. Show activity text is visible but objectives are hidden.
10. Send first student answer.
11. Show AI asks one guiding question.
12. Show objective achievement gives +1 and mini-lesson.
13. Repeat same objective and show no duplicate score.
14. Cover second objective and show completion.
15. Login as Instructor A and open Score Logs.
16. Show metadata fields.
17. Show manual grade.
18. Login as Instructor B and show unauthorized course is not visible.
19. Reset Activity 1.
20. Login as Student 1 and show reset/ENDED activity is inaccessible.