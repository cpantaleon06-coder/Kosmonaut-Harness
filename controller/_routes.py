import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response
from pydantic import BaseModel

import brain

router = APIRouter()


class MessageIn(BaseModel):
    message: str


# Plain "def" (not "async def"): FastAPI runs these in a thread pool,
# so one long agent run does not block other requests.
@router.post("/api/message")
def post_message(body: MessageIn):
    return brain.handle_message(body.message)


# The browser UI uses jobs instead of /api/message: Firefox drops a request
# that sends nothing for 300 s, and an agent run can take longer than that.
# shortcut: jobs live in memory and are lost on restart; move them to Postgres if that matters.
jobs: dict[str, dict] = {}


def _run_job(job_id: str, message: str) -> None:
    try:
        jobs[job_id] = {"status": "done", "result": brain.handle_message(message)}
    except Exception as error:
        jobs[job_id] = {"status": "error", "error": str(error)}


@router.post("/api/jobs")
def start_job(body: MessageIn, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}
    background_tasks.add_task(_run_job, job_id, body.message)
    return {"job_id": job_id}


@router.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@router.get("/api/projects/{project_id}/download")
def download_project(project_id: str):
    data = brain.get_archive(project_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return Response(
        content=data,
        media_type="application/x-tar",
        headers={"Content-Disposition": f'attachment; filename="project-{project_id}.tar"'},
    )
