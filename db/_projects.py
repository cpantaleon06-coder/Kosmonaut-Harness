import os
import uuid

import psycopg
from dotenv import load_dotenv

load_dotenv()


def save_project(task: str, reply: str, archive_key: str) -> str:
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        row = conn.execute(
            "INSERT INTO projects (task, reply, archive_key) VALUES (%s, %s, %s) RETURNING id",
            (task, reply, archive_key),
        ).fetchone()
    return str(row[0])


def get_project(project_id: str) -> dict | None:
    try:
        uuid.UUID(project_id)
    except ValueError:
        return None  # not a valid id

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        row = conn.execute(
            "SELECT id, task, reply, archive_key FROM projects WHERE id = %s",
            (project_id,),
        ).fetchone()
    if row is None:
        return None
    return {"id": str(row[0]), "task": row[1], "reply": row[2], "archive_key": row[3]}
