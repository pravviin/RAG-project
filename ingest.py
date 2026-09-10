"""
ingest.py — Load documents from ./data, chunk them, embed them, and store
them in a local, persistent ChromaDB collection.

Run: python ingest.py
No API keys, no network calls except the one-time embedding model download
(ONNX MiniLM, bundled by chromadb, cached locally after first run).
"""

import os
import glob
import argparse

import chromadb
from pypdf import PdfReader

DATA_DIR = "data"
DB_DIR = "chroma_db"
COLLECTION_NAME = "documents"

CHUNK_SIZE = 220      # words per chunk
CHUNK_OVERLAP = 40    # words of overlap between consecutive chunks


def load_text_from_file(path: str) -> str:
    """Extract raw text from a .txt or .pdf file."""
    if path.lower().endswith(".pdf"):
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Split text into overlapping word-count chunks.

    Overlap matters: it stops facts that straddle a chunk boundary from
    being lost to retrieval. Word-count chunking is a simple, transparent
    baseline — swap in a token-aware or sentence-aware splitter if you
    want to go further (worth mentioning in an interview).
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def ingest(data_dir: str = DATA_DIR, db_dir: str = DB_DIR, reset: bool = False):
    client = chromadb.PersistentClient(path=db_dir)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Cleared existing collection '{COLLECTION_NAME}'.")
        except Exception:
            pass

    # chromadb's default embedding function runs a local ONNX MiniLM model —
    # no torch, no API key, downloaded once and cached under ~/.cache/chroma.
    collection = client.get_or_create_collection(COLLECTION_NAME)

    files = glob.glob(os.path.join(data_dir, "*.pdf")) + glob.glob(os.path.join(data_dir, "*.txt"))
    if not files:
        print(f"No .pdf or .txt files found in ./{data_dir}/. Add some documents and re-run.")
        return

    all_ids, all_docs, all_metas = [], [], []
    for path in files:
        filename = os.path.basename(path)
        print(f"Reading {filename} ...")
        text = load_text_from_file(path)
        chunks = chunk_text(text)
        print(f"  -> {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            all_ids.append(f"{filename}::{i}")
            all_docs.append(chunk)
            all_metas.append({"source": filename, "chunk_index": i})

    if not all_docs:
        print("No extractable text found in the provided files.")
        return

    # Batch add (chromadb embeds internally using the collection's embedding function)
    BATCH = 100
    for i in range(0, len(all_docs), BATCH):
        collection.add(
            ids=all_ids[i:i + BATCH],
            documents=all_docs[i:i + BATCH],
            metadatas=all_metas[i:i + BATCH],
        )

    print(f"\nIngested {len(all_docs)} chunks from {len(files)} file(s) into '{db_dir}/'.")
    print(f"Collection now has {collection.count()} total chunks.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Clear the collection before ingesting")
    args = parser.parse_args()
    ingest(reset=args.reset)
