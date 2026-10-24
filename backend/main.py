"""App entry point. Start it from the backend folder:

    .venv/bin/uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from api import chat, health

app = FastAPI(title="RAG Resume Chatbot")

# CORS: lets the website (a different address) call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
