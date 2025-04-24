"""
Zomato Menu Scraper

This module provides functionality to scrape restaurant menu data from Zomato.
It extracts restaurant information including name, location, contact details,
and complete menu data with categories, items, prices, and descriptions.
The data is saved in JSON format for further processing.
"""

import time
import re
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_zomato(url, filename="zomato_menu.json"):
    """
    Scrape restaurant menu data from a Zomato restaurant page.
    
    This function uses Selenium to navigate to a Zomato restaurant page,
    expand all "Read More" buttons, and extract detailed information about
    the restaurant and its menu items using BeautifulSoup.
    
    Parameters:
        url (str): The URL of the Zomato restaurant page to scrape.
        filename (str): The name of the JSON file to save the data to.
                        Default is "zomato_menu.json".
    
    Returns:
        None: The function saves the scraped data to a JSON file and prints
              confirmation messages to the console.
    
    The scraped data includes:
    - Restaurant information (name, location, contact)
    - Menu categories
    - Menu items with details (name, price, description, vegetarian status, spice level)
    """
    # Configure Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(4)  # Wait for page to load completely
    
    # Expand all "Read More" buttons to get complete descriptions
    try:
        while True:
            read_more_buttons = driver.find_elements(By.XPATH, "//span[contains(translate(text(), 'READ MORE', 'read more'), 'read more')]")
            if not read_more_buttons:
                break
            for btn in read_more_buttons:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                except Exception:
                    pass
            time.sleep(0.5)
    except Exception:
        pass

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()
    
    # Extract restaurant information
    restaurant_info = {}
    rest_name = soup.find("h1")
    restaurant_info["name"] = rest_name.get_text(strip=True) if rest_name else ""
    
    location = ""
    loc_tag = soup.find("div", class_=re.compile("sc-clNaTc"))
    if loc_tag:
        location = loc_tag.get_text(strip=True)
    restaurant_info["location"] = location
    
    contact = ""
    phone_tag = soup.find("a", href=re.compile(r"tel:"))
    if phone_tag:
        contact = phone_tag.get_text(strip=True)
    restaurant_info["contact"] = contact

    # Extract menu data
    menu_data = []
    menu_sections = soup.find_all("section", class_=re.compile("sc-bZVNgQ"))
    for section in menu_sections:
        cat_tag = section.find("h4")
        category = cat_tag.get_text(strip=True) if cat_tag else ""
        category_data = {"category": category, "items": []}
        
        # Extract items in each category
        item_blocks = section.find_all("div", class_=re.compile("sc-jhLVlY"))
        for item in item_blocks:
            # Determine vegetarian status
            veg_type = "Unknown"
            veg_div = item.find("div", class_=re.compile("sc-gcpVEs"))
            if veg_div and veg_div.has_attr("type"):
                if veg_div["type"] == "veg":
                    veg_type = "Veg"
                elif veg_div["type"] == "non-veg":
                    veg_type = "Non-Veg"
            
            # Extract item details
            name_tag = item.find("h4", class_=re.compile("sc-cGCqpu"))
            name = name_tag.get_text(strip=True) if name_tag else ""
            
            price_tag = item.find("span", class_=re.compile("sc-17hyc2s-1"))
            price = price_tag.get_text(strip=True) if price_tag else ""
            
            # Extract and clean description
            desc_tag = item.find("p", class_=re.compile("sc-gsxalj"))
            desc = ""
            if desc_tag:
                for rm in desc_tag.find_all("span", string=re.compile("read more", re.I)):
                    rm.extract()
                desc = desc_tag.get_text(" ", strip=True)
            
            # Determine spice level based on description keywords
            spice_level = "Spicy" if re.search(r"spicy|fiery|peri peri|chilli|hot", desc, re.I) else "Normal"
            
            # Add item to category if it has a name
            if name:
                category_data["items"].append({
                    "name": name,
                    "price": price,
                    "description": desc,
                    "veg_nonveg": veg_type,
                    "spice_level": spice_level
                })
        
        menu_data.append(category_data)
    
    # Print summary of scraped data
    print("Restaurant:", restaurant_info["name"])
    print("Location:", restaurant_info["location"])
    print("Contact:", restaurant_info["contact"])
    print("Sample menu items:", menu_data[0]["items"][:3])

    # Ensure directory exists and prepare filepath
    os.makedirs("menu", exist_ok=True)
    filename = filename.replace(".csv", ".json")
    filepath = os.path.join("menu", filename)

    # Prepare final data structure
    final_data = {
        "restaurant": restaurant_info,
        "menu": menu_data
    }

    # Save data to JSON file
    with open(filepath, 'w') as f:
        import json
        json.dump(final_data, f, indent=4)
    print(f"✅ Saved to {filepath}")
