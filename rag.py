"""
rag.py — Core retrieval-augmented generation pipeline.

Retrieval: local ChromaDB (persisted on disk, built by ingest.py).
Generation: local Ollama server (no API key, no cloud, no per-token cost).

Requires Ollama running: `ollama serve` (usually auto-started) and a model
pulled, e.g. `ollama pull llama3.2:3b`.
"""

import requests
import chromadb

DB_DIR = "chroma_db"
COLLECTION_NAME = "documents"
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using ONLY the "
    "context provided below. If the answer isn't in the context, say "
    "you don't have enough information — do not make anything up. "
    "Cite which source each fact comes from using the [source] tags given."
)


class RAGPipeline:
    def __init__(self, db_dir: str = DB_DIR, model: str = DEFAULT_MODEL):
        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection(COLLECTION_NAME)
        self.model = model

    def retrieve(self, query: str, k: int = 4):
        """Return the top-k most relevant chunks for a query."""
        if self.collection.count() == 0:
            return []

        results = self.collection.query(query_texts=[query], n_results=k)
        hits = []
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            hits.append({"text": doc, "source": meta["source"], "score": 1 - dist})
        return hits

    def build_prompt(self, query: str, hits: list) -> str:
        context_blocks = "\n\n".join(
            f"[{h['source']}]\n{h['text']}" for h in hits
        )
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"### Context:\n{context_blocks}\n\n"
            f"### Question:\n{query}\n\n"
            f"### Answer:"
        )

    def generate(self, prompt: str) -> str:
        """Call the local Ollama server. Raises a clear error if it's not running."""
        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=120,
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        except requests.exceptions.ConnectionError:
            return (
                "[Could not reach Ollama at localhost:11434 — is it running? "
                "Start it with `ollama serve` and make sure you've pulled a model, "
                f"e.g. `ollama pull {self.model}`.]"
            )

    def answer(self, query: str, k: int = 4):
        """Full pipeline: retrieve -> build prompt -> generate. Returns (answer, hits)."""
        hits = self.retrieve(query, k=k)
        if not hits:
            return (
                "No documents have been ingested yet. Run `python ingest.py` first.",
                [],
            )
        prompt = self.build_prompt(query, hits)
        answer = self.generate(prompt)
        return answer, hits


if __name__ == "__main__":
    pipeline = RAGPipeline()
    print("Local RAG assistant — type a question (or 'quit')\n")
    while True:
        q = input("> ")
        if q.strip().lower() in ("quit", "exit"):
            break
        answer, hits = pipeline.answer(q)
        print(f"\n{answer}\n")
        if hits:
            sources = ", ".join(sorted({h["source"] for h in hits}))
            print(f"(sources: {sources})\n")
