import json
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from google.genai import errors as genai_errors
from pydantic import BaseModel, Field

import config
import rag_chain

router = APIRouter()

MAX_RETRIES = 2
BUSY_CODES = (429, 503)  # Google says "too many requests" / "too busy right now"


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=config.MAX_QUESTION_CHARS)


def _sse(payload):
    """Format one Server-Sent Event. JSON keeps newlines inside the text safe."""
    return f"data: {json.dumps(payload)}\n\n"


def _open_stream(question):
    """Start the answer and wait for its first piece.

    Doing this before replying means a failure becomes a proper HTTP error
    (the website can show a friendly message) instead of a half-broken stream.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            stream = rag_chain.stream_answer(question)
            return next(stream, ""), stream
        except genai_errors.APIError as e:
            if e.code in BUSY_CODES:
                if attempt < MAX_RETRIES:
                    time.sleep(1 + attempt)
                    continue
                raise HTTPException(
                    503, "The AI service is busy right now. Please try again in a moment."
                )
            raise HTTPException(502, "The AI service returned an error.")
        except Exception:
            raise HTTPException(
                500, "The knowledge base is not ready. Run ingest.py first."
            )


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    first_piece, stream = _open_stream(request.question)

    def event_stream():
        if first_piece:
            yield _sse({"text": first_piece})
        try:
            for piece in stream:
                yield _sse({"text": piece})
        except Exception:
            yield _sse({"error": "The answer was interrupted. Please try again."})
        yield _sse({"done": True})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
