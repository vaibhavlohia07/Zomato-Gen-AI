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

## 📁 Table of Contents
1. [System Architecture](#system-architecture)
2. [Implementation Details & Design Decisions](#implementation-details--design-decisions)
3. [Challenges Faced & Solutions](#challenges-faced--solutions)
4. [Future Improvement Opportunities](#future-improvement-opportunities)

