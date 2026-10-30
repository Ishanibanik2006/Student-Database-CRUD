# Students Database CRUD Application

A Python backend project built with **FastAPI** and **SQLite** for the EWB internship assignment.

## Features

- **Create:** add a student using `POST /students`.
- **Read:** list/filter students using `GET /students`; view one student using `GET /students/{student_id}`.
- **Update:** edit student details using `PUT` or `PATCH /students/{student_id}`.
- **Delete:** remove a student using `DELETE /students/{student_id}`.
- SQLite stores records persistently in `students.db`.
- Input validation, duplicate-ID handling, and 404 handling.
- Interactive API documentation at `/docs`.

## Student fields

Required: `student_id`, `name`, `date_of_birth`, and at least one contact method (`email` or `phone`).

Optional: `course`, `address`, `enrollment_date`, and the second contact method.

Dates must use `YYYY-MM-DD`. Student IDs may contain letters, numbers, `_`, and `-`.

## 1. Requirements

- Python 3.10 or newer
- pip

## 2. Installation

Open a terminal in this project folder.

### Windows
```bash
py -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Run the API

```bash
uvicorn main:app --reload
```

Open these addresses in your browser:

- API home: http://127.0.0.1:8000/
- Interactive Swagger documentation: http://127.0.0.1:8000/docs
- ReDoc documentation: http://127.0.0.1:8000/redoc

The SQLite database file is created automatically the first time the application starts.

## 4. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/students` | Create a student |
| GET | `/students` | List/filter students |
| GET | `/students/{student_id}` | View one student |
| PUT | `/students/{student_id}` | Update supplied fields |
| PATCH | `/students/{student_id}` | Partially update supplied fields |
| DELETE | `/students/{student_id}` | Delete a student |

### Filtering examples

- `/students?name=riya`
- `/students?course=BCA`
- `/students?born_after=2005-01-01`
- `/students?born_before=2006-12-31`
- `/students?limit=20&offset=0`

Filters can be combined.

## 5. Sample request bodies

### Create — POST `/students`

```json
{
  "student_id": "STU001",
  "name": "Riya Das",
  "date_of_birth": "2005-04-12",
  "email": "riya@example.com",
  "phone": "9876543210",
  "course": "BCA",
  "address": "Kolkata",
  "enrollment_date": "2024-08-01"
}
```

### Update — PUT or PATCH `/students/STU001`

```json
{
  "course": "BCA - 2nd Year",
  "phone": "9876501234"
}
```

### Delete

Send `DELETE /students/STU001`. A successful delete returns HTTP `204 No Content`.

## 6. Testing

Install dependencies, then run:

```bash
pytest -q
```

The tests use a temporary SQLite database and do not change your main `students.db`.

## 7. Security and design notes

- SQL values are passed using SQLite parameter placeholders (`?`), rather than being pasted into SQL strings. This helps prevent SQL injection.
- The API validates incoming data with Pydantic.
- Do not enter real student personal information in a public demo. Use dummy records.
- Do not commit `students.db`, virtual environments, passwords, or secrets to GitHub.

## 8. GitHub submission

1. Create a new **public or trainer-approved private** GitHub repository.
2. Upload the project files, including `main.py`, `database.py`, `requirements.txt`, `README.md`, `tests/`, and `.gitignore`.
3. Do not upload your virtual environment or database file.
4. Copy the repository URL and submit it through the channel announced by your EWB trainer.

Example Git commands:

```bash
git init
git add .
git commit -m "Build student database CRUD API"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your own repository URL.
