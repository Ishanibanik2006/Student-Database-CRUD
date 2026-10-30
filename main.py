from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from database import init_db, get_connection


class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None

    @model_validator(mode="after")
    def require_contact_method(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least an email address or phone number.")
        return self


class StudentCreate(StudentBase):
    student_id: str = Field(..., min_length=2, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None

    model_config = ConfigDict(extra="forbid")


class Student(StudentBase):
    student_id: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Students Database CRUD API",
    description="A beginner-friendly FastAPI + SQLite backend for managing student records.",
    version="1.0.0",
    lifespan=lifespan,
)


def row_to_student(row):
    return dict(row)


@app.get("/", tags=["Home"])
def home():
    return {
        "message": "Students Database CRUD API is running.",
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Home"])
def health():
    return {"status": "ok"}


@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentCreate):
    data = student.model_dump()
    data["date_of_birth"] = data["date_of_birth"].isoformat()
    if data["enrollment_date"]:
        data["enrollment_date"] = data["enrollment_date"].isoformat()

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO students
                (student_id, name, date_of_birth, email, phone, course, address, enrollment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["student_id"], data["name"], data["date_of_birth"],
                    str(data["email"]) if data["email"] else None,
                    data["phone"], data["course"], data["address"], data["enrollment_date"],
                ),
            )
            row = conn.execute(
                "SELECT * FROM students WHERE student_id = ?", (data["student_id"],)
            ).fetchone()
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise HTTPException(status_code=409, detail="A student with this student_id already exists.")
        raise

    return row_to_student(row)


@app.get("/students", response_model=list[Student], tags=["Students"])
def list_students(
    name: Optional[str] = Query(default=None, description="Filter by part of a student's name"),
    course: Optional[str] = Query(default=None, description="Filter by course"),
    born_after: Optional[date] = Query(default=None, description="Date of birth after this date"),
    born_before: Optional[date] = Query(default=None, description="Date of birth before this date"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    conditions = []
    values = []

    if name:
        conditions.append("LOWER(name) LIKE LOWER(?)")
        values.append(f"%{name}%")
    if course:
        conditions.append("LOWER(course) = LOWER(?)")
        values.append(course)
    if born_after:
        conditions.append("date_of_birth > ?")
        values.append(born_after.isoformat())
    if born_before:
        conditions.append("date_of_birth < ?")
        values.append(born_before.isoformat())

    sql = "SELECT * FROM students"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY name LIMIT ? OFFSET ?"
    values.extend([limit, offset])

    with get_connection() as conn:
        rows = conn.execute(sql, values).fetchall()
    return [row_to_student(row) for row in rows]


@app.get("/students/{student_id}", response_model=Student, tags=["Students"])
def get_student(student_id: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return row_to_student(row)


@app.put("/students/{student_id}", response_model=Student, tags=["Students"])
def update_student(student_id: str, student: StudentUpdate):
    updates = student.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update.")

    if "date_of_birth" in updates and updates["date_of_birth"] is not None:
        updates["date_of_birth"] = updates["date_of_birth"].isoformat()
    if "enrollment_date" in updates and updates["enrollment_date"] is not None:
        updates["enrollment_date"] = updates["enrollment_date"].isoformat()
    if "email" in updates and updates["email"] is not None:
        updates["email"] = str(updates["email"])

    # A contact method must remain after a partial update.
    with get_connection() as conn:
        current = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        if current is None:
            raise HTTPException(status_code=404, detail="Student not found.")

        new_email = updates.get("email", current["email"])
        new_phone = updates.get("phone", current["phone"])
        if not new_email and not new_phone:
            raise HTTPException(status_code=422, detail="A student must have an email or phone number.")

        assignments = ", ".join(f"{column} = ?" for column in updates)
        values = list(updates.values()) + [student_id]
        conn.execute(
            f"UPDATE students SET {assignments} WHERE student_id = ?", values
        )
        updated = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    return row_to_student(updated)


@app.patch("/students/{student_id}", response_model=Student, tags=["Students"])
def patch_student(student_id: str, student: StudentUpdate):
    return update_student(student_id, student)


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: str):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE student_id = ?", (student_id,)
        )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
