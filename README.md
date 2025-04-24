# Zomato-Gen-AI

A powerful, AI-driven assistant specialized in restaurant information and menu queries. Leveraging advanced natural language processing capabilities, it provides users with accurate and concise responses about various restaurants, their menus, pricing, and locations.

## Directory Structure

```
Zomato-Gen-AI/
├── menu/
│   ├── baap_of_rolls_menu.json
│   ├── desi_tadka_menu.json
│   ├── dominos_menu.json
│   ├── foodbay_menu.json
│   ├── kfc_menu.json
│   ├── patiala_lassi_menu.json
│   ├── pizza_hut_menu.json
│   ├── prakash_hotel_menu.json
│   └── waffle_by_nature_menu.json
├── models/
├── README.md
├── app.py
├── data_cleaning.py
├── data_scraper.py
├── database.csv
├── rag.py
├── requirements.txt
└── scraper_runner.py

```
## Setup
Config (.env)
```sh
hf_token = "YOUR-API-KEY"
gemini_token = "PUBLIC-API-KEY"
```

Environment
```sh
conda create -n myenv python=3.10
conda activate myenv
pip install -r requirements.txt
```

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Implementation Details & Design Decisions](#implementation-details--design-decisions)
3. [Challenges Faced & Solutions](#challenges-faced--solutions)
4. [Future Improvement Opportunities](#future-improvement-opportunities)

---

## System Architecture

```
             +----------------+             +--------------------+             
             | scraper_runner | --------->  |    scraper.py      |             
             +----------------+             +--------------------+             
                                                    |                          
                                                    v                          
                                        +------------------------+             
                                        |   JSON menu files in   |             
                                        |      /menu folder      |             
                                        +------------------------+             
                                                    |                          
                                                    v                          
                                        +------------------------+             
                                        |  data_cleaning.py      |             
                                        | - Cleaning & formatting|             
                                        | - Gemini restaurant info|            
                                        +------------------------+             
                                                    |                          
                                                    v                          
                                        +------------------------+             
                                        |   chatbot.py           |             
                                        | - Embeddings via SBERT |             
                                        | - FAISS Vector Store   |             
                                        | - Gemini/LLaMA model   |             
                                        +------------------------+             
```

---

## Implementation Details & Design Decisions

### Module: `scraper_runner.py`
- Acts as the **driver script** to initiate scraping across multiple Zomato URLs.
- Maps restaurant names to their respective URLs and invokes `scrape_zomato()` from `scraper.py`.

### Module: `scraper.py`
Scrapes restaurant information and menu data from a Zomato restaurant page and saves it in structured JSON format.
- Uses **Selenium WebDriver** (headless Chrome) to render and interact with the dynamic content of Zomato pages.
- Clicks all "Read more" buttons to expand hidden descriptions.
- Parses restaurant name, location, contact, menu categories, and items using **BeautifulSoup**.
- Each menu item includes:
  - Name, Price, Description
  - Vegetarian/Non-Vegetarian type
  - Estimated spice level (based on keywords in description)
- Automatically saves the scraped data to a JSON file in the `/menu` folder.

### Module: `data_cleaning.py`

**Purpose:**  
This module processes raw restaurant menu data extracted from Zomato (stored in JSON format), cleans and enriches it using preprocessing techniques and the Gemini LLM, and prepares it for embedding and retrieval in the chatbot.

**Key Functionalities:**

- **Text Cleaning (`clean_text`)**  
  Normalizes and standardizes string content: converts to lowercase, removes symbols, trims whitespace.

- **Price Normalization (`normalize_price`)**  
  Extracts numeric values from price fields, removing symbols and unwanted characters.

- **Synonym Handling (`apply_synonyms`)**  
  Replaces domain-specific terms like “non-veg”, “combo”, or “spicy” with standardized phrases to ensure semantic consistency.

- **Menu Data Enrichment (`load_and_clean_menus_from_json`)**
  - Loads JSON files from the `/menu` directory.
  - Extracts restaurant-level metadata: name, location, and contact info.
  - Sends a structured prompt to **Gemini** to generate:
    - Restaurant summary
    - Types of cuisine served
    - Operational hours
  - Combines this info with detailed item data (category, item name, description, price, veg/non-veg, spice level).
  - Outputs a flat list of all text chunks and saves them to `database.csv`.

**Returns:**  
A list of cleaned and enriched text strings describing restaurants and their menu items, suitable for use in retrieval-based systems.

### Module: `chatbot.py`

**Purpose:**  
Serves as the core logic for the restaurant chatbot. It handles embedding generation, similarity-based document retrieval, and response generation using an LLM (either Gemini or LLaMA).

 **Key Components:**

- **Data Loading (`load_data_from_json`)**  
  Calls the `load_and_clean_menus_from_json()` from `data_cleaning.py` to obtain processed restaurant/menu text data.

- **Embedding + Indexing (`build_faiss`)**  
  - Generates sentence embeddings using SentenceTransformers (`all-MiniLM-L6-v2`).
  - Constructs a **FAISS** index for fast vector similarity search.

- **Query Retrieval (`retrieve`)**  
  - Encodes the user query and searches the FAISS index.
  - Returns the top-k most relevant documents as context.

- **Response Generation (`query_llama`)**  
  - Builds a structured prompt using the current query, retrieved context, and previous chat history.
  - Calls Gemini (or optionally LLaMA) to generate a concise and contextually-aware answer.
  - Maintains conversation history for reference in follow-up queries.

- **Chatbot Handler (`chatbot`)**  
  Orchestrates the above steps to serve end-to-end interaction: load → embed → retrieve → respond.

**LLM Notes:**  
- By default, uses **Gemini-1.5-Pro** via the `google.generativeai` API.
- A commented-out section supports local **LLaMA models** via `llama_cpp`.

**Returns:**  
A conversational response and updated query history.

---

## Challenges Faced & Solutions

| Challenge | Solution |
|----------|----------|
| Dynamic elements and lazy loading on Zomato pages | Automated "Read more" button clicks using Selenium with retry loops. |
| Text inconsistencies across restaurants (non-veg vs non vegetarian etc.) | Implemented regex-based synonym replacement (e.g., "nonveg" → "non vegetarian"). |
| JSON structure variability | Standardized output format with proper schema (menu, restaurant block). |
| Gemini’s long latency in repeated calls | Minimized calls only during restaurant-level summarization and used local embedding for menus. |

---

## Future Improvement Opportunities

1. **Frontend UI**: Integrate with a web interface using Streamlit or Flask.
2. **Live Chat Memory**: Use session/state-based history persistence beyond `query_llama`.
3. **Multilingual Support**: Pre-process input/output using translation models.
4. **Enhance Dataset Schema**: Add delivery/dine-in ratings, popular items, cuisine tags.
5. **Parallel Scraping**: Enable multi-threading or async-based scrapers for speed.
6. **Model Upgrades**: Replace MiniLM with larger contextual models (e.g., `all-mpnet-base-v2`).


---

## Web Interface via Streamlit

A user-friendly web interface was developed using **Streamlit** to make the chatbot accessible and interactive.

### app.py Highlights
- Uses `streamlit` for a clean UI.
- Initializes the model and FAISS index on app load using `@st.cache_resource`.
- Accepts user input via a text box.
- Retrieves relevant document chunks using FAISS and passes them to the `query_llama` function.
- Maintains a running history of past queries and responses.
- Displays the bot's most recent answer and the full conversation history.

### Features:
- Lightweight and fast loading with caching.
- Context-aware follow-up question handling.
- Integrated Gemini or LLaMA response engine for conversational output.

---
