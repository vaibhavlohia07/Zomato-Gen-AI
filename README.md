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

### scraper_runner.py
- Acts as the **driver script** to initiate scraping across multiple Zomato URLs.
- Maps restaurant names to their respective URLs and invokes `scrape_zomato()` from `scraper.py`.

### scraper.py
Scrapes restaurant information and menu data from a Zomato restaurant page and saves it in structured JSON format.
- Uses **Selenium WebDriver** (headless Chrome) to render and interact with the dynamic content of Zomato pages.
- Clicks all "Read more" buttons to expand hidden descriptions.
- Parses restaurant name, location, contact, menu categories, and items using **BeautifulSoup**.
- Each menu item includes:
  - Name, Price, Description
  - Vegetarian/Non-Vegetarian type
  - Estimated spice level (based on keywords in description)
- Automatically saves the scraped data to a JSON file in the `/menu` folder.

  ### data_cleaning.py
  This module processes raw restaurant menu data extracted from Zomato (stored in JSON format), cleans and enriches it using preprocessing techniques and the Gemini LLM, and prepares it for embedding and retrieval in the chatbot.
- key function:-
   -
- Cleans and normalizes text, price, and synonyms.
- Loads JSON files from `/menu`, and extracts:
  - Restaurant summary (via **Gemini** prompt).
  - Item descriptions into structured text chunks.
- Stores all output into a CSV (`database.csv`) and returns text corpus for embedding.

  ### chatbot.py
- Loads text data from `data_cleaning`.
- Uses **SentenceTransformers (MiniLM)** to generate embeddings.
- Constructs a **FAISS vector store** for fast similarity search.
- Retrieves top-k relevant chunks for user queries.
- Passes them as **context to Gemini or LLaMA** for generating conversational answers.

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
