# Local RAG Assistant

A retrieval-augmented generation (RAG) chatbot that answers questions over
your own documents — running **entirely locally**. No OpenAI/Anthropic API
key, no per-token billing, no data leaving your machine.

- **Embeddings:** local ONNX MiniLM model (bundled by ChromaDB, downloaded
  once, cached forever)
- **Vector store:** ChromaDB, persisted to disk
- **LLM:** [Ollama](https://ollama.com) running a small open-weight model
  (Llama 3.2 3B / Phi-3.5-mini) on your own CPU or GPU
- **UI:** Streamlit chat interface
- **Eval:** a small, hand-rolled harness measuring retrieval hit-rate and
  answer keyword coverage

## Architecture

```
 your files (.pdf/.txt)
        │  ingest.py
        ▼
 chunk (overlap-aware) → embed (local ONNX MiniLM) → store in ChromaDB
                                                            │
 user question ─────► embed ─────► similarity search ──────┘
                                          │
                                   top-k chunks
                                          │
                              prompt = question + chunks
                                          │
                                   Ollama (local LLM)
                                          │
                                     grounded answer
```

## Setup

```bash
# 1. Install Ollama: https://ollama.com/download
ollama pull llama3.2:3b        # or phi3.5, mistral, etc.

# 2. Python deps
python -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt

# 3. Add your documents
cp your_files.pdf data/        # a sample doc is already in data/ to try first

# 4. Build the vector index
python ingest.py               # add --reset to rebuild from scratch

# 5a. Chat in the terminal
python rag.py

# 5b. Or use the web UI
streamlit run app.py
```

## Evaluating it

```bash
python eval.py                  # full retrieval + generation eval
python eval.py --skip-generation  # just test retrieval (no Ollama needed)
```

Edit `eval_questions.json` to test against your own documents — for each
question, specify which source file should be retrieved and which keywords
a correct answer should contain. The script reports:

- **Retrieval hit-rate** — did the right document get retrieved?
- **Answer keyword coverage** — did the generated answer actually use it?

This is what turns "I built a RAG chatbot" into a bullet with a number
behind it.

## Notes on the design choices

- **Word-count chunking with overlap** rather than fixed character
  chunking — simple and transparent, but you should be ready to discuss
  the tradeoff against sentence-aware or token-aware chunking in an
  interview.
- **ChromaDB's default embedding function** (ONNX MiniLM) instead of
  pulling in `sentence-transformers`/`torch` directly — same underlying
  model family, far lighter dependency footprint. Swap it out via
  `embedding_functions` in `chromadb.utils` if you want to try a larger
  embedding model.
- **No LangChain/LlamaIndex** — the retrieval and prompt-building logic in
  `rag.py` is written by hand, so you understand (and can explain) every
  step instead of relying on a framework's abstractions.

## Suggested resume bullet

> Built a fully local, retrieval-augmented LLM assistant (Ollama + Llama
> 3.2, ChromaDB, custom chunking/retrieval pipeline) with no external
> APIs; designed a custom eval harness measuring retrieval hit-rate and
> answer keyword coverage across a test question set.

## Ideas to extend it (good for a v2 / interview talking points)

- Swap word-count chunking for sentence- or token-aware chunking
- Add re-ranking (cross-encoder) after initial retrieval
- Support multi-turn conversation with query rewriting
- Add citation verification (does the answer actually match the cited chunk?)
- Try a bigger local model via Ollama and compare eval scores
