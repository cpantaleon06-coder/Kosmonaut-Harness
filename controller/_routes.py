from fastapi import APIRouter, HTTPException, Response
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
