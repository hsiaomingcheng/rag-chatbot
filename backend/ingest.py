"""Read the knowledge base, split it into chunks, embed them, store them in ChromaDB.

Run from the backend folder:  .venv/bin/python ingest.py
"""

import re

import chromadb
from google import genai
from google.genai import types

import config

EMBED_BATCH_SIZE = 50


def load_text(path):
    text = path.read_text(encoding="utf-8")
    # Drop HTML comments (e.g. the TODO notes) so they never reach the chatbot.
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def split_into_sections(text):
    """Split markdown at headings. Returns a list of (heading, body)."""
    sections = []
    heading = ""
    lines = []
    for line in text.splitlines():
        if re.match(r"#{1,3} ", line):
            if "\n".join(lines).strip():
                sections.append((heading, "\n".join(lines).strip()))
            heading = line.lstrip("# ").strip()
            lines = []
        else:
            lines.append(line)
    if "\n".join(lines).strip():
        sections.append((heading, "\n".join(lines).strip()))
    return sections


def split_long_text(text, size, overlap):
    """Cut text that is longer than `size` into overlapping pieces."""
    if len(text) <= size:
        return [text]
    pieces = []
    start = 0
    while start < len(text):
        pieces.append(text[start : start + size])
        if start + size >= len(text):
            break
        start += size - overlap
    return pieces


def build_chunks(text):
    """Every chunk starts with its section heading, so it still makes sense on its own."""
    chunks = []
    for heading, body in split_into_sections(text):
        for piece in split_long_text(body, config.CHUNK_SIZE, config.CHUNK_OVERLAP):
            chunks.append(f"{heading}\n{piece}" if heading else piece)
    return chunks


def embed_documents(client, chunks):
    vectors = []
    for i in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch = chunks[i : i + EMBED_BATCH_SIZE]
        response = client.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        vectors.extend(e.values for e in response.embeddings)
    return vectors


def main():
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_api_key_here":
        raise SystemExit("GEMINI_API_KEY is missing. Put your key in the .env file.")

    text = load_text(config.KNOWLEDGE_BASE_PATH)
    chunks = build_chunks(text)
    print(f"Split the knowledge base into {len(chunks)} chunks.")

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    vectors = embed_documents(client, chunks)

    db = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    # Start fresh each time so re-running never creates duplicates.
    try:
        db.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    collection = db.create_collection(
        config.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    collection.add(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=vectors,
    )
    print(f"Stored {collection.count()} chunks in {config.CHROMA_DIR}")


if __name__ == "__main__":
    main()
