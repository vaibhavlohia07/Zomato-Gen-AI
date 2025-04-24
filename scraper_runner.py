"""
Zomato Menu Scraper Runner

This script automates the scraping of multiple Zomato restaurant menu pages
by utilizing the scrape_zomato function from the scraper module. It processes
a predefined dictionary of restaurant URLs and saves each restaurant's menu
data to individual JSON files.
"""

from scraper import scrape_zomato

# Dictionary mapping restaurant identifiers to their Zomato order page URLs
urls = {
    "prakash_hotel": "https://www.zomato.com/roorkee/hotel-prakash-restaurant-roorkee-locality/order",
    "dominos": "https://www.zomato.com/roorkee/dominos-pizza-roorkee-locality/order",
    "pizza_hut": "https://www.zomato.com/roorkee/pizza-hut-roorkee-locality/order",
    "foodbay": "https://www.zomato.com/roorkee/foodbay-roorkee-locality/order",
    "kfc": "https://www.zomato.com/roorkee/kfc-1-roorkee-locality/order",
    "waffle_by_nature": "https://www.zomato.com/roorkee/waffle-by-nature-roorkee-locality/order",
    "patiala_lassi" : "https://www.zomato.com/roorkee/patiala-lassi-roorkee-locality/order",
    "desi_tadka": "https://www.zomato.com/roorkee/desi-tadka-2-roorkee-locality/order",
    "baap_of_rolls": "https://www.zomato.com/roorkee/baap-of-rolls-roorkee-locality/order"
}

def main():
    """
    Main function that iterates through the dictionary of restaurant URLs
    and scrapes menu data for each restaurant.
    
    The function attempts to scrape each restaurant's menu data using the
    scrape_zomato function. If successful, the data is saved to a JSON file
    named after the restaurant. If an error occurs during scraping, an error
    message is printed and the function continues to the next restaurant.
    
    Returns:
        None
    """
    for name, url in urls.items():
        print(f"\n==> Scraping {name} from {url}")
        filename = f"{name}_menu.csv"
        try:
            scrape_zomato(url, filename)
        except Exception as e:
            print(f"❌ Failed to scrape {name}: {e}")

if __name__ == "__main__":
    main()
