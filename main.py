from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controller import router

app = FastAPI(title="Kosmonaut Harness")
app.include_router(router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
