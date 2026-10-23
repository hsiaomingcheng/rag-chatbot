"""Answer a question: find the most relevant chunks, then let Gemini answer from them.

Try it from the backend folder:  .venv/bin/python rag_chain.py "Where did Chris work?"
"""

import sys

import chromadb
from google import genai
from google.genai import types

import config

SYSTEM_INSTRUCTION = """You are an assistant that answers questions about Chris Hsiao, \
a job candidate, for recruiters and interviewers.
Answer ONLY from the reference material provided with each question.
If the material does not contain the answer, say you don't have that information \
and suggest contacting Chris by email. Never invent facts.
Keep answers concise and friendly, and refer to Chris in the third person."""

_client = None
_collection = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _get_collection():
    global _collection
    if _collection is None:
        db = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
        _collection = db.get_collection(config.COLLECTION_NAME)
    return _collection


def retrieve(question, top_k=config.TOP_K):
    """Return the `top_k` chunks whose meaning is closest to the question."""
    response = _get_client().models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    result = _get_collection().query(
        query_embeddings=[response.embeddings[0].values], n_results=top_k
    )
    return result["documents"][0]


def build_prompt(question, chunks):
    context = "\n\n---\n\n".join(chunks)
    return f"Reference material:\n\n{context}\n\nQuestion: {question}"


def stream_answer(question):
    """Yield the answer piece by piece (this is what gives the typing effect)."""
    chunks = retrieve(question)
    stream = _get_client().models.generate_content_stream(
        model=config.CHAT_MODEL,
        contents=build_prompt(question, chunks),
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )
    for piece in stream:
        if piece.text:
            yield piece.text


def main():
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_api_key_here":
        raise SystemExit("GEMINI_API_KEY is missing. Put your key in the .env file.")
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python rag_chain.py "your question"')

    question = " ".join(sys.argv[1:])
    for text in stream_answer(question):
        print(text, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
