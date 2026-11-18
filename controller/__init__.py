from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from controller import router

app = FastAPI()
app.include_router(router)
# Mounted last so it does not hide the /api routes.
app.mount("/", StaticFiles(directory="static", html=True), name="static")