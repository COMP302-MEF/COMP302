# InClass Platform - Run Guide

## 1. PostgreSQL
Create a PostgreSQL database in pgAdmin4, for example:

```sql
CREATE DATABASE inclass_db;
```

## 2. Environment
Copy `.env.example` to `.env` and update values:

```env
SQLALCHEMY_DATABASE_URL=postgresql://postgres:1234@localhost:5432/inclass_db
OPENROUTER_API_KEY=your_openrouter_key
```

Do not commit `.env` to GitHub.

## 3. Install packages

```bash
cd backend
pip install -r requirements.txt
```

## 4. Load clean demo data

```bash
python seed.py
```

## 5. Start backend

```bash
uvicorn main:app --reload
```

## 6. Open frontend
Open `frontend/login.html` in the browser.

Demo accounts:

- Instructor A: `hoca_a@test.com` / `123`
- Instructor B: `hoca_b@test.com` / `123`
- Student 1: `ogr_1@test.com` / `123`
- Student 2: `ogr_2@test.com` / `123`

## Demo flow

1. Login as Student 1 and try to open Activity 1 before start. Backend rejects because status is NOT_STARTED.
2. Login as Instructor A and start Activity 1.
3. Login as Student 1 again. Activity 1 becomes accessible. Objectives are hidden.
4. Login as Student 2 and try activity ID 1 from the access-test box. Backend rejects because Student 2 is not enrolled.
5. Login as Student 1 and chat with the tutor.
6. When an objective is achieved, score increases once and score log metadata is visible in Instructor A dashboard.
7. Instructor A can manual grade, end, and reset the activity.
