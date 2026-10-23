"""Shared settings. Change a model name here and every other file picks it up."""

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

load_dotenv(PROJECT_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-3.5-flash-lite"

KNOWLEDGE_BASE_PATH = PROJECT_DIR / "data" / "candidate_profile.md"
CHROMA_DIR = BACKEND_DIR / "chroma_db"
COLLECTION_NAME = "candidate_profile"

CHUNK_SIZE = 800  # max characters per chunk
CHUNK_OVERLAP = 100  # characters shared between neighbouring chunks
TOP_K = 3  # how many chunks to retrieve per question
