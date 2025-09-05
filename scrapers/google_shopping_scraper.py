import json
import time
from playwright.sync_api import sync_playwright

# Load selectors from JSON file
def load_selectors(config_path="scrapers/google_selectors.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def scrape_google_shopping(query="hoodie", max_results=20, headless=True, config_path="scrapers/google_selectors.json"):
    selectors = load_selectors(config_path)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/117.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = f"https://www.google.com/search?tbm=shop&q={query}"
        page.goto(url, timeout=60000)
        time.sleep(2)

        cards = page.query_selector_all(selectors["product_card"])
        if not cards:
            print("⚠️ No product nodes found. Selectors may be stale. Update google_selectors.json")
            return []

        for card in cards[:max_results]:
            try:
                title = card.query_selector(selectors["title"]).inner_text() if card.query_selector(selectors["title"]) else None
                price = card.query_selector(selectors["price"]).inner_text() if card.query_selector(selectors["price"]) else None
                vendor = card.query_selector(selectors["vendor"]).inner_text() if card.query_selector(selectors["vendor"]) else None
                link = card.query_selector(selectors["link"]).get_attribute("href") if card.query_selector(selectors["link"]) else None
                image = card.query_selector(selectors["image"]).get_attribute("src") if card.query_selector(selectors["image"]) else None

                results.append({
                    "title": title,
                    "price": price,
                    "vendor": vendor,
                    "link": f"https://www.google.com{link}" if link and link.startswith("/") else link,
                    "image": image,
                })
            except Exception as e:
                print(f"⚠️ Error parsing product card: {e}")
                continue

        browser.close()

    return results
