import docker
client = docker.from_env()

def create() -> str:
    container = client.containers.run(
        "python:3.12-slim",
        "sleep infinity",
        detach=True,
        working_dir="/workspace",
        mem_limit="512m",
        nano_cpus=1_000_000_000,
        pids_limit=256, 
    )
    return container.id

def destroy(container_id: str) -> None:
    # destroy:
    client.containers.get(container_id).remove(force=True)
