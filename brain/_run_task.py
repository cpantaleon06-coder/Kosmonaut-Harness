import uuid

import db
import harness
import sandbox


def handle_message(task: str) -> dict:
    container_id = sandbox.create()
    try:
        reply = harness.run_agent(task, container_id)
        archive = sandbox.export_workspace(container_id)
    finally:
        sandbox.destroy(container_id)

    archive_key = f"projects/{uuid.uuid4()}.tar"
    db.upload_archive(archive_key, archive)
    project_id = db.save_project(task, reply, archive_key)
    return {"project_id": project_id, "reply": reply}


def get_archive(project_id: str) -> bytes | None:
    project = db.get_project(project_id)
    if project is None:
        return None
    return db.download_archive(project["archive_key"])
handle_message  is  the  core  data  flow:  create  container,  run  agent,  export  files,  destroy  container,  upload  files,  save  row.
