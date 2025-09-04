# scrapers/adidas_scraper.py
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def scrape_adidas(query: str):
    url = f"https://www.adidas.co.in/search?q={query}"
    results = []

    with sync_playwright() as p:
        # Run visible browser to debug – switch to headless=True later
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-http2", "--disable-features=NetworkService"]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/127.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )

        page = context.new_page()
        stealth_sync(page)  # 👈 disguises Playwright

        print(f"Scraping Adidas for '{query}'...")
        page.goto(url, timeout=60000, wait_until="networkidle")

        # Wait for product grid to load
        page.wait_for_selector("div.gl-product-card", timeout=15000)

        # Extract products
        product_elements = page.query_selector_all("div.gl-product-card")
        for el in product_elements[:20]:  # limit first 20
            title = el.query_selector("div.gl-product-card__name")
            price = el.query_selector("div.gl-price")
            link = el.query_selector("a.gl-product-card__assets-link")

            results.append({
                "title": title.inner_text().strip() if title else None,
                "price": price.inner_text().strip() if price else None,
                "url": link.get_attribute("href") if link else None,
            })

        browser.close()

    return results
