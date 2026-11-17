from base64 import decode
import io
import posixpath
import shlex
import tarfile

from ._setup import client

MAX_OUTPUT = 10_000 # characters;


def _clean(path: str) -> str:
    # The model sometimes sends "/workspace/app.py". We always want "app.py".
    if path.startswith("/workspace/"):
        path = path[len("/workspace/"):]
    return path.lstrip("/")

def run(container_id: str, command: str, timeout: int = 60) -> dict:
    container=client.containers.get(container_id)
    exit_code, output = container.exec_run(
        ["timeout", str(timeout),"sh","-c", command],
        workdir="/workspace"
    )
    text=output.decode("utf-8", errors="replace")
    if len(text)> MAX_OUTPUT:
        text = text[MAX_OUTPUT]+ "\n...[output truncated]"
    return{"exit_dode":exit_code, "output":text}

def write_file(container_id:str, path: str,content: str) -> None:
    container=client.containers.get(container_id)
    path=_clean(path)

    folder = posixpath.dirname(path)
    if folder:
        container.exec_run(["mkdir", "-p", folder], workdir="/workspace")

    data = content.encode("utf-8")
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        info = tarfile.TarInfo(name=path)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    buffer.seek(0)
    container.put_archive("/workspace", buffer)


def read_file(container_id: str, path: str) -> str:
    result = run(container_id, "cat " + shlex.quote(_clean(path)))
    return result["output"]


def export_workspace(container_id: str) -> bytes:
    container = client.containers.get(container_id)
    stream, _ = container.get_archive("/workspace")
    return b"".join(stream)
