import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "students.db"))


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT,
                CHECK (email IS NOT NULL OR phone IS NOT NULL)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_students_name ON students(name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_students_course ON students(course)")
