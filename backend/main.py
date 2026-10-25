"""App entry point. Start it from the backend folder:

    .venv/bin/uvicorn main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
import ingest
from api import chat, health

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app):
    # Runs once at startup. Free hosting wipes the disk on restart, so make
    # sure the knowledge base database exists before answering questions.
    if not ingest.has_api_key():
        logger.error("GEMINI_API_KEY is missing; the knowledge base was not built.")
    else:
        try:
            ingest.ensure_database()
        except Exception:
            # Keep the server up (so /api/health still works); chat reports "not ready".
            logger.exception("Could not prepare the knowledge base.")
    yield


app = FastAPI(title="RAG Resume Chatbot", lifespan=lifespan)

# CORS: lets the website (a different address) call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
