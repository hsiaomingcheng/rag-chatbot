"""Read the knowledge base, split it into chunks, embed them, store them in ChromaDB.

Run from the backend folder:  .venv/bin/python ingest.py
"""

import hashlib
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


def fingerprint(text):
    """A short code that changes whenever the knowledge base text changes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def has_api_key():
    return bool(config.GEMINI_API_KEY) and config.GEMINI_API_KEY != "your_api_key_here"


def build_database(text):
    """Embed the knowledge base and store it in ChromaDB, replacing any old copy."""
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
        config.COLLECTION_NAME,
        # The fingerprint lets ensure_database() tell if the stored copy is current.
        metadata={"hnsw:space": "cosine", "source_hash": fingerprint(text)},
    )
    collection.add(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=vectors,
    )
    print(f"Stored {collection.count()} chunks in {config.CHROMA_DIR}")


def ensure_database():
    """Build the database only if it is missing or out of date. Returns True if rebuilt.

    Free hosting wipes the disk on restart, so the server calls this on startup.
    """
    text = load_text(config.KNOWLEDGE_BASE_PATH)
    db = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    try:
        collection = db.get_collection(config.COLLECTION_NAME)
        up_to_date = (
            collection.count() > 0
            and (collection.metadata or {}).get("source_hash") == fingerprint(text)
        )
    except Exception:
        up_to_date = False

    if up_to_date:
        print("Knowledge base is up to date; skipping ingest.")
        return False

    build_database(text)
    return True


def main():
    if not has_api_key():
        raise SystemExit("GEMINI_API_KEY is missing. Put your key in the .env file.")
    build_database(load_text(config.KNOWLEDGE_BASE_PATH))


if __name__ == "__main__":
    main()
