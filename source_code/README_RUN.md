InClass Platform - Run Instructions

====================================
1. PROJECT OVERVIEW
====================================

InClass Platform is a classroom activity system.

The system allows instructors to manage course activities and allows students to work only on authorized ACTIVE activities.

Main features:

- Instructor and student login
- Server-side role authorization
- Server-side course authorization
- Instructor course listing
- Instructor activity management
- Activity create, update, start, end, reset
- Student access only to enrolled and ACTIVE activities
- AI tutoring flow
- Objective-based scoring
- Score logs with metadata
- Manual grading
- PostgreSQL persistence


====================================
2. REQUIREMENTS
====================================

Required software:

- Python 3.11 or newer
- PostgreSQL
- pgAdmin4
- Internet connection
- OpenRouter API key

Required Python packages are listed in:

source_code/backend/requirements.txt


====================================
3. PROJECT STRUCTURE
====================================

The submitted source code is located inside the source_code folder.

Expected structure:

source_code/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── seed.py
│   ├── init_db.py
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── login.html
    ├── register.html
    ├── instructor_dashboard.html
    ├── student_chat.html
    ├── api.js
    └── style.css


====================================
4. BACKEND SETUP
====================================

Open a terminal and go to the backend folder:

cd source_code/backend

Install required packages:

pip install -r requirements.txt


====================================
5. ENVIRONMENT FILE
====================================

Create a file named .env inside the backend folder:

source_code/backend/.env

Use .env.example as a template.

Example .env content:

SQLALCHEMY_DATABASE_URL=postgresql://postgres:1234@localhost:5432/inclass_db
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=deepseek/deepseek-chat
AUTH_SECRET=inclass-demo-secret-123

Important notes:

- Do not commit the real .env file to GitHub.
- Do not include the real .env file in the final submission ZIP.
- The real OpenRouter API key must be kept private.
- If your PostgreSQL password is not 1234, update the database URL.
- If your database name is different from inclass_db, update the database URL.


====================================
6. DATABASE SETUP
====================================

Make sure PostgreSQL is running.

Open pgAdmin4 and create a database named:

inclass_db

If needed, run this SQL command in pgAdmin4:

CREATE DATABASE inclass_db;

After the database is created, return to the backend terminal and run:

python seed.py

This command resets the database and loads the required demo data.

The seed command creates:

- 2 instructors
- 2 students
- 2 courses
- Student 1 enrolled in Course 1
- Student 2 not enrolled in Course 1
- 2 activities in Course 1
- Activity 1 starts as NOT_STARTED
- Empty score logs and student progress


====================================
7. RUN BACKEND
====================================

From the backend folder, run:

uvicorn main:app --reload

Backend URL:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs


====================================
8. RUN FRONTEND
====================================

Open the following file in a browser:

source_code/frontend/login.html

The frontend communicates with the backend at:

http://127.0.0.1:8000


====================================
9. DEMO ACCOUNTS
====================================

Use the following accounts after running python seed.py:

Instructor A:
Email: hoca_a@test.com
Password: 123

Instructor B:
Email: hoca_b@test.com
Password: 123

Student 1:
Email: ogr_1@test.com
Password: 123

Student 2:
Email: ogr_2@test.com
Password: 123


====================================
10. DEMO DATA
====================================

After running python seed.py, the system contains the following demo data:

Instructor A:
- Authorized for COMP302

Instructor B:
- Authorized for COMP400
- Not authorized for COMP302

Student 1:
- Enrolled in COMP302

Student 2:
- Not enrolled in COMP302

Courses:
- COMP302 - Software Engineering
- COMP400 - Senior Project

Activities in COMP302:

Activity 1:
- Activity No: 1
- Title: Retrieval Practice Demo
- Initial Status: NOT_STARTED

Activity 2:
- Activity No: 2
- Title: Spacing Effect Activity
- Initial Status: NOT_STARTED


====================================
11. EXPECTED DEMO FLOW
====================================

Recommended final demo order:

1. Login as Instructor A.
2. Show that Instructor A can see only COMP302.
3. Open COMP302 and show Activity 1 and Activity 2.
4. Show Activity 1 status as NOT_STARTED.
5. Logout and login as Student 1.
6. Show that Student 1 cannot access Activity 1 before it starts.
7. Logout and login as Instructor A.
8. Start Activity 1.
9. Logout and login as Student 1.
10. Show that Student 1 can now access Activity 1.
11. Open Activity 1.
12. Show that the activity text is visible.
13. Show that learning objectives are not exposed to the student.
14. Send a message to the AI tutor.
15. Show that the AI asks one guiding question at a time.
16. Give an answer that satisfies an objective.
17. Show +1 objective-based score.
18. Show updated score and mini-lesson.
19. Repeat the same objective.
20. Show that duplicate scoring does not happen.
21. Give an answer that satisfies the second objective.
22. Show activity completion.
23. Login as Instructor A.
24. Open Score Logs.
25. Show score log metadata.
26. Show manual grade if time remains.
27. Show reset behavior if time remains.
28. Login as Student 2.
29. Show that Student 2 cannot access COMP302.
30. Login as Instructor B.
31. Show that Instructor B cannot access COMP302.


====================================
12. AI DEMO ANSWERS
====================================

Use these English answers during the demo.

First message:

I think the second strategy is better because the student closes the book and tries to explain the ideas from memory.

Objective 1 answer:

Active retrieval practice is better than passive rereading because recalling information from memory strengthens long-term learning and shows what the student actually understands.

Duplicate scoring test answer:

Retrieving from memory is more useful than rereading because it makes the brain actively reconstruct the knowledge instead of only recognizing the text.

Objective 2 answer:

Feedback is important because after retrieval the student can compare the answer with the correct information, find mistakes, and correct misunderstandings.


====================================
13. MAIN API ENDPOINTS
====================================

Authentication:

POST /login
POST /register
GET /me

Courses:

GET /courses

Activities:

GET /courses/{course_id}/activities
POST /courses/{course_id}/activities
GET /activities/{activity_id}
PATCH /activities/{activity_id}
POST /activities/{activity_id}/start
POST /activities/{activity_id}/end
POST /activities/{activity_id}/reset

Student tutoring:

POST /activities/{activity_id}/chat
GET /activities/{activity_id}/my-progress

Scoring:

POST /activities/{activity_id}/manual-grade
GET /activities/{activity_id}/score-logs


====================================
14. AUTHORIZATION BEHAVIOR
====================================

The backend enforces authorization server-side.

Instructor authorization:

- Instructor A can access only COMP302.
- Instructor B can access only COMP400.
- Instructor B cannot access COMP302.

Student authorization:

- Student 1 can access COMP302 because Student 1 is enrolled in COMP302.
- Student 2 cannot access COMP302 because Student 2 is not enrolled in COMP302.
- Students can access only ACTIVE activities.
- NOT_STARTED and ENDED activities are not accessible to students.

Frontend role checks are used for navigation, but the real access control is handled by the backend.


====================================
15. SCORING BEHAVIOR
====================================

Objective-based scoring rules:

- First achievement of an objective gives exactly +1 point.
- Repeating the same objective does not give another point.
- Every score change is logged.
- Score logs include student, course, activity, score delta, updated score, event type, and metadata.
- A mini-lesson is shown after an objective earns a point.
- When all objectives are completed, the activity is marked complete for the student.

Score log event types:

AI_OBJECTIVE
MANUAL_GRADE
RESET


====================================
16. RESET BEHAVIOR
====================================

When an instructor resets an activity:

- Score logs for that activity are deleted.
- Student progress for that activity is deleted.
- Activity status becomes ENDED.
- Students cannot continue the activity after reset.


====================================
17. MANUAL GRADE BEHAVIOR
====================================

Instructor A can manually grade students in COMP302.

Manual grade creates a score log with:

- event_type = MANUAL_GRADE
- score_delta
- updated_score
- metadata reason

Unauthorized instructors cannot manually grade activities outside their assigned courses.


====================================
18. COMMON PROBLEMS AND SOLUTIONS
====================================

Problem:
Backend cannot connect to PostgreSQL.

Solution:
Check the database URL in source_code/backend/.env.

Example:

SQLALCHEMY_DATABASE_URL=postgresql://postgres:1234@localhost:5432/inclass_db

Make sure:

- PostgreSQL is running.
- The database exists.
- The password is correct.
- The database name is correct.


Problem:
AI returns 401.

Solution:
The OpenRouter API key is missing, invalid, or wrong.

Check this line in .env:

OPENROUTER_API_KEY=your_openrouter_api_key_here

OpenRouter keys usually start with:

sk-or-v1-


Problem:
AI returns 502.

Solution:
The backend reached the AI service, but the AI service returned an error.

Check the backend terminal for details.


Problem:
Frontend cannot connect to backend.

Solution:
Make sure the backend is running:

uvicorn main:app --reload

Also make sure the backend URL is:

http://127.0.0.1:8000


Problem:
Login works, but protected requests fail.

Solution:
Clear browser localStorage and login again.

In browser console:

localStorage.clear()


Problem:
Demo data is not correct.

Solution:
Run:

cd source_code/backend
python seed.py

Then restart backend:

uvicorn main:app --reload


====================================
19. IMPORTANT SECURITY NOTES
====================================

- The real .env file must not be committed.
- The real API key must not be submitted.
- Only .env.example should be included in the submission ZIP.
- If an API key is exposed, delete it and create a new one.


====================================
20. FINAL DEMO PREPARATION
====================================

Before the demo starts:

1. Make sure PostgreSQL is running.
2. Make sure the backend is running.
3. Make sure the frontend login page opens.
4. Make sure the OpenRouter API key is valid.
5. Run python seed.py for a clean demo state.
6. Login once as Instructor A and Student 1 to verify the system.
7. Keep demo accounts ready.
8. Keep the demo answer text ready.
9. Keep evidence screenshots ready if needed.

Recommended commands before demo:

cd source_code/backend
python seed.py
uvicorn main:app --reload

Then open:

source_code/frontend/login.html