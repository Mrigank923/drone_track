import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
from pathlib import Path
from dotenv import load_dotenv


app = FastAPI(title="Drone Tracking Backend (MongoDB)")


# Enable permissive CORS for development. Adjust in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)


@app.get("/")
def root():
    return {"status": "ok", "msg": "Drone Tracking Backend"}