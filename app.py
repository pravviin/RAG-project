"""
app.py — Streamlit chat UI for the local RAG assistant.

Run: streamlit run app.py
"""

import streamlit as st
from rag import RAGPipeline, DEFAULT_MODEL

st.set_page_config(page_title="Local RAG Assistant", page_icon="📚")

st.title("📚 Local RAG Assistant")
st.caption("Runs fully offline — local embeddings, local vector store, local LLM via Ollama. No API keys.")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Ollama model", value=DEFAULT_MODEL)
    top_k = st.slider("Chunks to retrieve (k)", min_value=1, max_value=10, value=4)
    show_sources = st.checkbox("Show retrieved chunks", value=True)
    st.markdown("---")
    st.markdown(
        "**Setup checklist**\n"
        "1. `ollama pull " + model + "`\n"
        "2. `python ingest.py` (with docs in `./data`)\n"
        "3. Ask away below"
    )

if "pipeline" not in st.session_state or st.session_state.get("model") != model:
    st.session_state.pipeline = RAGPipeline(model=model)
    st.session_state.model = model

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("hits") and show_sources:
            with st.expander("Retrieved chunks"):
                for h in msg["hits"]:
                    st.markdown(f"**{h['source']}** (score: {h['score']:.2f})")
                    st.text(h["text"][:400] + ("..." if len(h["text"]) > 400 else ""))

if query := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving context and generating..."):
            answer, hits = st.session_state.pipeline.answer(query, k=top_k)
        st.markdown(answer)
        if hits and show_sources:
            with st.expander("Retrieved chunks"):
                for h in hits:
                    st.markdown(f"**{h['source']}** (score: {h['score']:.2f})")
                    st.text(h["text"][:400] + ("..." if len(h["text"]) > 400 else ""))

    st.session_state.messages.append({"role": "assistant", "content": answer, "hits": hits})
