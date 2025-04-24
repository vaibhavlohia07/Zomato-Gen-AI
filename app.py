import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import torch
torch.classes.__path__ = []

import streamlit as st
from chatbot import load_data_from_json, build_faiss, retrieve, query_llama
from llama_cpp import Llama

# Streamlit page config
st.set_page_config(page_title="🍽️ Restaurant Menu Chatbot", layout="wide")

# Initialize chatbot model and FAISS
@st.cache_resource(show_spinner="Loading model and data...")
def init_bot():
    docs = load_data_from_json()
    index, embeddings, embedder = build_faiss(docs)
    return docs, index, embedder

docs, index, embedder = init_bot()

# Streamlit UI
st.title("🍽️ Restaurant Menu Chatbot")
st.write("Ask a question about the restaurant menus:")

# History as list of (query, response) to preserve order
if "history" not in st.session_state:
    st.session_state.history = []

# User input
query_input = st.text_input("Type your query", value="", key="user_input")

# Handle query
if st.button("Ask") and query_input.strip():
    query = query_input.strip().lower()
    recent_history = st.session_state.history[-2:]  # last 2 query-response pairs
    history_string = "\n".join([f"Query: {q}" for q, r in recent_history])
    context = "\n".join(retrieve(query+" "+history_string, index, embedder, docs))
    response, history = query_llama(context, query, st.session_state.history)
    st.session_state.history = history
    st.session_state.last_response = response

# Display last response
if "last_response" in st.session_state:
    st.subheader("🤖 Bot Response")
    st.markdown(st.session_state.last_response)

# Show chat history
if st.session_state.history:
    with st.expander("📜 Chat History"):
        for q, r in reversed(st.session_state.history):
            st.markdown(f"**You:** {q}")
            st.markdown(f"**Bot:** {r}")

