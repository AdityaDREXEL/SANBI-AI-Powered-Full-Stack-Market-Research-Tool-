import httpx
from bs4 import BeautifulSoup
import re
from typing import List
import os

def scrape_sold_ebay_listings(search_term: str) -> List[float]:
    scrapeops_api_key = os.getenv("SCRAPEOPS_API_KEY")
    if not scrapeops_api_key:
        print("ERROR: SCRAPEOPS_API_KEY not found in environment variables.")
        return []

    ebay_url = (
        f"https://www.ebay.com/sch/i.html?_nkw={search_term.replace(' ', '+')}"
        f"&LH_Complete=1&LH_Sold=1"
    )

    proxy_url = "https://proxy.scrapeops.io/v1/"
    params = {
        "api_key": scrapeops_api_key,
        "url": ebay_url,
    }
    prices = []
    try:
        with httpx.Client() as client:
            response = client.get(proxy_url, params=params, timeout=120.0)
            response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")
        listings = soup.select("li.s-card, li.s-item")

        for item in listings:
            title_element = item.select_one("div.s-card__title, div.s-item__title span[role='heading']")
            price_element = item.select_one("span.s-card__price, span.s-item__price")
            
            if title_element and price_element:
                title = title_element.text.strip()
                price_text = price_element.text.strip()
                
                price_cleaned = re.search(r'(\d{1,3}(,\d{3})*(\.\d+)?)', price_text)
                price = float(price_cleaned.group(0).replace(',', '')) if price_cleaned else 0.0
                
                if price > 0 and "Shop on eBay" not in title:
                    prices.append(price)
        return prices
    except Exception as e:
        print(f"Scraping failed for '{search_term}': {e}")
        return []