"""
eval.py — Lightweight evaluation harness for the RAG pipeline.

Measures two things, per the standard RAG eval split:
  1. Retrieval hit-rate: did the expected source file show up in the top-k
     retrieved chunks?
  2. Answer keyword coverage: does the generated answer mention the
     keywords we'd expect a correct answer to contain?

This is a simple, transparent stand-in for a fuller framework like RAGAS —
good enough to produce real numbers for a resume bullet, and easy to
explain in an interview because you wrote every line of it yourself.

Run: python eval.py
"""

import json
import argparse

from rag import RAGPipeline


def load_eval_set(path: str = "eval_questions.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_eval(k: int = 4, skip_generation: bool = False):
    pipeline = RAGPipeline()
    eval_set = load_eval_set()

    if pipeline.collection.count() == 0:
        print("No documents ingested yet. Run `python ingest.py` first.")
        return

    retrieval_hits = 0
    keyword_scores = []

    print(f"Running {len(eval_set)} eval questions (k={k})...\n")

    for i, item in enumerate(eval_set, start=1):
        question = item["question"]
        expected_source = item.get("expected_source")
        expected_keywords = item.get("expected_keywords", [])

        hits = pipeline.retrieve(question, k=k)
        retrieved_sources = {h["source"] for h in hits}
        hit = expected_source in retrieved_sources if expected_source else None
        if hit:
            retrieval_hits += 1

        print(f"[{i}] {question}")
        print(f"    Retrieved sources: {sorted(retrieved_sources)}")
        print(f"    Expected source '{expected_source}': {'HIT' if hit else 'MISS'}")

        if not skip_generation:
            prompt = pipeline.build_prompt(question, hits)
            answer = pipeline.generate(prompt)
            found = [kw for kw in expected_keywords if kw.lower() in answer.lower()]
            score = len(found) / len(expected_keywords) if expected_keywords else None
            if score is not None:
                keyword_scores.append(score)
            print(f"    Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print(f"    Keyword coverage: {found} -> {score:.0%}" if score is not None else "")
        print()

    n = len(eval_set)
    print("=" * 50)
    print(f"Retrieval hit-rate: {retrieval_hits}/{n} ({retrieval_hits / n:.0%})")
    if keyword_scores:
        avg = sum(keyword_scores) / len(keyword_scores)
        print(f"Average answer keyword coverage: {avg:.0%}")
    print("=" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Only test retrieval, skip calling the LLM (useful if Ollama isn't running)",
    )
    args = parser.parse_args()
    run_eval(k=args.k, skip_generation=args.skip_generation)
