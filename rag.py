"""
Restaurant Menu Chatbot System

This module implements a chatbot system that answers queries about restaurant menus
using vector similarity search with FAISS and generative AI models. The system loads
restaurant menu data, embeds it using sentence transformers, and retrieves relevant
information to answer user queries.
"""

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

# Load environment variables
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
    """
    Load and clean restaurant menu data from JSON files.
    
    Returns:
        list: A list of document strings containing restaurant and menu information.
    """
    docs = load_and_clean_menus_from_json("menu")
    return docs

# Query prefix to align embeddings and retrieval
QUERY_PREFIX = ""

def build_faiss(documents, model_name="all-MiniLM-L6-v2"):
    """
    Build a FAISS vector index from document embeddings.
    
    This function creates embeddings for each document using a sentence transformer model,
    and builds a FAISS index for efficient similarity search.
    
    Parameters:
        documents (list): List of document strings to embed and index.
        model_name (str): Name of the sentence transformer model to use for embeddings.
                          Default is "all-MiniLM-L6-v2".
    
    Returns:
        tuple: Contains:
            - faiss.Index: The FAISS index built from document embeddings.
            - numpy.ndarray: The document embeddings.
            - SentenceTransformer: The sentence transformer model used for embeddings.
    """
    embedder = SentenceTransformer(model_name)
    docs_with_prefix = [QUERY_PREFIX + doc for doc in documents]
    embeddings = embedder.encode(docs_with_prefix)
    index = faiss.IndexFlatL2(embeddings[0].shape[0])
    index.add(np.array(embeddings))
    return index, embeddings, embedder

def retrieve(query, index, embedder, documents, k=10):
    """
    Retrieve the top-k most relevant documents for a given query.
    
    This function embeds the query using the same embedder used for documents,
    performs a similarity search in the FAISS index, and returns the most relevant documents.
    
    Parameters:
        query (str): The user query to search for.
        index (faiss.Index): The FAISS index to search in.
        embedder (SentenceTransformer): The sentence transformer model for embedding the query.
        documents (list): The original list of document strings.
        k (int): Number of documents to retrieve. Default is 10.
    
    Returns:
        list: The top-k most relevant documents.
    """
    query = QUERY_PREFIX + query
    query_vec = embedder.encode([query])
    _, I = index.search(np.array(query_vec), k)
    docs = [documents[i] for i in I[0]]
    return docs

def query_llama(context, query, history):
    """
    Generate a response to a user query using the Gemini model.
    
    This function takes the retrieved context, user query, and conversation history,
    constructs a prompt for the Gemini model, and generates a response.
    
    Parameters:
        context (str): The retrieved context information from relevant documents.
        query (str): The user's query.
        history (list): List of tuples containing previous (query, response) pairs.
    
    Returns:
        tuple: Contains:
            - str: The generated response.
            - list: The updated conversation history with the new query-response pair.
    """
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
    
    # Generate response using Gemini model
    response = model.generate_content(prompt).text.strip()
    history.append((query, response))
    return response, history

def chatbot(query, history):
    """
    Main chatbot function that processes user queries and generates responses.
    
    This function loads the restaurant data, processes the user query, retrieves relevant
    context using FAISS, and generates a response using the language model.
    
    Parameters:
        query (str): The user's query.
        history (list): List of tuples containing previous (query, response) pairs.
    
    Returns:
        tuple: Contains:
            - str: The generated response.
            - list: The updated conversation history with the new query-response pair.
    """
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
