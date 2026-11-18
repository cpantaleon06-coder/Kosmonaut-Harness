# Kosmonaut Harness

A cloud-native AI coding harness. You send a coding task over HTTP. The server
starts a fresh Docker container, runs an LLM agent inside it until the task is
done, saves the container's `/workspace` as a tar file, and then destroys the
container. You get the agent's reply and a link to download the files.

The LLM is Gemma 4 served by a local Ollama through its OpenAI-compatible API.
Files go to Neon Object Storage (S3 API), and one row per task goes to Neon Postgres.

## How a request flows

```
browser / curl
     │  POST /api/message  (or POST /api/jobs + polling)
     ▼
controller ──► brain.handle_message(task)
                 │
                 ├─ sandbox.create()            new python:3.12-slim container
                 ├─ harness.run_agent()         LLM + tools loop, max 25 steps
                 │     └─ tools: run_command, write_file, read_file → sandbox
                 ├─ sandbox.export_workspace()  /workspace as tar bytes
                 ├─ sandbox.destroy()           always, even on error
                 ├─ db.upload_archive()         tar → Neon Object Storage
                 └─ db.save_project()           row → Neon Postgres
```

## Architecture

| Package | Role |
|---|---|
| `controller/` | FastAPI routes. `POST /api/message` runs a task and answers when it is done. `POST /api/jobs` starts the same work in the background and `GET /api/jobs/{id}` reports its status (the browser UI uses these). `GET /api/projects/{id}/download` returns the saved tar. |
| `brain/` | Runs one task from start to finish: container, agent, export, cleanup, storage. |
| `harness/` | The agent loop: call the LLM with the tool list, run each tool call it makes, feed the results back, stop when it answers without tool calls or after 25 steps. |
| `sandbox/` | Docker wrapper. Each container gets 512 MB RAM, 1 CPU and 256 processes. Commands time out after 60 s and output is cut at 10,000 characters. |
| `db/` | Neon Postgres (`projects` table) and Neon Object Storage (tar files). |
| `static/` | A one-page UI: a text box, a Send button, the reply and a download link. |

`try_sandbox.py`, `try_llm.py`, `try_db.py` and `try_brain.py` check each layer on its own.

## Setup

You need Python 3.12+, Docker, Ollama and a Neon project with Object Storage enabled.

1. Pull the model and pre-pull the sandbox image:

   ```bash
   ollama pull gemma4
   ```

   ```bash
   docker pull python:3.12-slim
   ```

2. Create the virtual environment:

   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```

3. Create the table in Neon Postgres:

   ```sql
   CREATE TABLE projects (
       id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
       task        text NOT NULL,
       reply       text NOT NULL,
       archive_key text NOT NULL,
       created_at  timestamptz NOT NULL DEFAULT now()
   );
   ```

4. Create `.env` in the project root (it is git-ignored):

   ```
   DATABASE_URL=postgresql://...
   AWS_REGION=...
   AWS_ENDPOINT_URL_S3=...
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   BUCKET_NAME=...
   ```

   The LLM endpoint and model are currently set in `harness/_llm_client.py`
   (`http://localhost:11434/v1/`, `gemma4:latest`).

5. Check each layer, then start the server:

   ```bash
   .venv/bin/python try_sandbox.py && .venv/bin/python try_db.py && .venv/bin/python try_brain.py
   ```

   ```bash
   .venv/bin/uvicorn main:app --port 8000
   ```

   Open http://localhost:8000, or call the API directly:

   ```bash
   curl -X POST localhost:8000/api/message -H 'Content-Type: application/json' -d '{"message":"Create hello.py that prints hello, and run it."}'
   ```

## Long runs

Firefox drops a request that receives nothing for 300 seconds, so an agent run
longer than 5 minutes ended in "NetworkError when attempting to fetch resource".
The UI now starts a job and polls it every 2 seconds instead. Jobs are kept in
memory: if the server restarts (for example `uvicorn --reload` after a code
edit) the UI reports "Job lost". The finished project is still saved in Postgres.
uvicorn waits for running tasks before it reloads, so a reload never cuts a run
short.

## Measured concurrency

Machine: 12 CPU threads, 38 GB RAM, NVIDIA GTX 1650 (4 GB). Ollama 0.40.16
with `gemma4:latest` (100% on GPU, 4096 context, default settings). Task:
"Write fib.py that prints the first 20 Fibonacci numbers, run it, and show
the output." Each test sent N requests to `POST /api/message` at the same time.

| Parallel requests | Containers seen in `docker ps` | All succeeded | Wall time | Time per task |
|---|---|---|---|---|
| 1 | 1 | yes | 24 s | 24 s |
| 3 | 3 | yes | 72 s | 24 s |
| 6 | 6 | yes | 196 s | 33 s |

- Docker is not the limit. All containers ran side by side, an idle sandbox
  used under 1 MB of RAM, and every container was removed afterwards.
- The LLM is the limit. Total time grows in step with the number of tasks,
  so Ollama is in effect serving one request at a time: throughput stays at
  about one task every 24–33 s however many run in parallel, and each extra
  parallel request makes every user wait longer.
- In practice this machine serves one agent at full speed. Several can be
  queued safely, but by extrapolation, around 10 parallel tasks would push
  each run past 5 minutes. That is why the UI polls a job instead of holding
  one request open.

To go faster, raise Ollama's `OLLAMA_NUM_PARALLEL` (if VRAM allows) or point
the harness at a larger GPU or a hosted OpenAI-compatible endpoint.
