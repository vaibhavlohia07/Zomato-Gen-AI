import os
import faiss
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from data_cleaning import load_and_clean_menus_from_json
from llama_cpp import Llama
import google.generativeai as genai



# Load Hugging Face token
load_dotenv()
HF_TOKEN = os.getenv("hf_token")
MENU_FOLDER = os.getenv("menu_folder")
os.environ["GGML_METAL_VERBOSE"] = "0"
GEMINI_TOKEN = os.getenv("gemini_token")
genai.configure(api_key=os.getenv("GEMINI_TOKEN"))
model = genai.GenerativeModel("gemini-1.5-pro")


# Step 1: Load and Format Data from CSVs
import re
import pandas as pd
from pathlib import Path

def load_data_from_json():
    docs = load_and_clean_menus_from_json("menu")
    return docs

# Query prefix to align embeddings and retrieval
QUERY_PREFIX = ""

# Step 2: Build FAISS Vector Store
def build_faiss(documents, model_name="all-MiniLM-L6-v2"):
    embedder = SentenceTransformer(model_name)
    docs_with_prefix = [QUERY_PREFIX + doc for doc in documents]
    embeddings = embedder.encode(docs_with_prefix)
    index = faiss.IndexFlatL2(embeddings[0].shape[0])
    index.add(np.array(embeddings))
    return index, embeddings, embedder

# Step 3: Retrieve Top-k Relevant Chunkss
def retrieve(query, index, embedder, documents, k=10):
    query = QUERY_PREFIX + query
    query_vec = embedder.encode([query])
    _, I = index.search(np.array(query_vec), k)
    docs = [documents[i] for i in I[0]]
    #print("Retrieved documents:", docs)
    return docs


# Step 4: Run Local LLaMA Model
# MODEL_PATH = "/Users/henrylohia/Desktop/sexy/models/llama-3/llama-pro-8b-instruct.Q4_K_M.gguf"
# llm = Llama(
#     model_path=MODEL_PATH,
#     n_ctx=4096,
#     n_threads=8,
#     n_gpu_layers=20,
#     use_mmap=True,
#     use_mlock=False,
#     verbose=False,
# )

def query_llama(context, query, history):
    '''
    Input: context: str, query: str, history: list of tuples (query, response)
    Output: response: str, history: list of tuples (query, response)
    This function takes the context and query, and generates a response using the LLaMA model.
    It also maintains the conversation history, which is used to provide context for the model.
    The history is a list of tuples, where each tuple contains the user's query and the model's response.
    The function returns the generated response and the updated history.
    '''
    if history:
        recent_history = history[-2:]
        history_string = "\n".join([f"Query: {q}\nResponse: {r}" for q, r in recent_history])
    else:
        history_string = "No previous conversation history."

    prompt = f"""You are a helpful assistant, knowledgeable about various kinds of restaurants, and have to answer user queries related to them.
Use the following context to answer the question faithfully.
Context:
{context}
The question provided by the user is,
Question: {query}
Your previous conversation history with the user is:
{history_string}
Ensure your answer is clear, concise, and directly addresses the user's question, and is framed like a proper answer.
You may format your answer, and apply things like capitalisation and grammar wherever required, without changing the information itself.
Ensure your answer is not too verbose, and is to the point, and do not add line breaks until the end of your response.
If you do not know the answer, say "I don't know" or "I am not sure" or "I cannot say" or "I have no idea" or "I cannot answer that", do not leave an empty response.
You may answer a question based on the history of the conversation, particulary if the user has asked a question which has not yet been answered properly, or a clarifying question has been asked to which the user has responded.
Answer:"""
    # output = llm(prompt, max_tokens=200, temperature=0.7, stop=["\n\n"])
    # response = output["choices"][0]["text"].strip()
    response = model.generate_content(prompt).text.strip()
    history.append((query, response))
    return response, history

def chatbot(query, history):
    docs = load_data_from_json()
    query = query.lower()
    index, embeddings, embedder = build_faiss(docs)
    context = "\n".join(retrieve(query, index, embedder, docs))
    return query_llama(context, query, history)

if __name__ == "__main__":
    q1 = "What's the price range for pizza hut's dessert menu?"
    q2 = "can you tell me the location of it"
    history = []
    print("User:", q1)
    r1, history = chatbot(q1, history)
    print("Bot:", r1)
    print(history)
    r2, history = chatbot(q2, history)
    print(history)
    print("User:", q2)
    print("Bot:", r2)
    # llm._sampler.close()
    # llm.close()

