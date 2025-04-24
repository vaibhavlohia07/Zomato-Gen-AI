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
    # model = Llama(
    #     model_path=os.getenv("MODEL_PATH", "/Users/henrylohia/Desktop/sexy/models/llama-3/llama-pro-8b-instruct.Q4_K_M.gguf"),
    #     n_ctx=4096,
    #     n_threads=8,
    #     n_gpu_layers=20,
    #     use_mmap=True,
    #     use_mlock=False,
    #     verbose=False,
    # )
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

# Run LLaMA with better prompt and ordered history
# def query_llama(context, query, history):
#     history_string = "\n".join([f"Query: {q}\nResponse: {r}" for q, r in history]) or "No previous conversation history."
#     prompt = f"""You are a helpful assistant, knowledgeable about restaurants and their menus. 
# You are helping a user who is asking multiple follow-up questions.
# Use the conversation history to resolve references like "it", "that restaurant", or "its location" by linking them to the last relevant subject mentioned.

# CONTEXT (retrieved from documents):
# {context}

# USER QUESTION:
# {query}

# PREVIOUS CONVERSATION HISTORY:
# {history_string}

# Your job is to infer the intended subject (restaurant or menu item) from the history, and respond directly to the user's question, even if the question is brief or ambiguous. 

# Make your answer:
# - Relevant and specific
# - Short and clear
# - Grammatically correct
# - Based only on available context and history

# If unsure, say “I am not sure” or something similar.

# Answer:"""
#     response = llm(prompt, max_tokens=200, temperature=0.7, stop=["\n\n"])
#     reply = response["choices"][0]["text"].strip()
#     history.append((query, reply))
#     return reply, history

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

