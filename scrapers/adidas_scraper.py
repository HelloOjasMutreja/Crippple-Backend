# scrapers/adidas_scraper.py
from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)


def scrape_adidas(query: str, max_results=20, headless=True):
    """
    Scrape Adidas India for products matching the query.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        headless: Run browser in headless mode
        
    Returns:
        List of product dictionaries
    """
    url = f"https://www.adidas.co.in/search?q={query}"
    results = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=headless,
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
            
            # Apply stealth if available
            try:
                from playwright_stealth import stealth_sync
                stealth_sync(page)
            except ImportError:
                logger.warning("playwright-stealth not available, skipping stealth mode")

            logger.info(f"Scraping Adidas: {url}")
            page.goto(url, timeout=60000, wait_until="networkidle")

            # Wait for product grid to load
            page.wait_for_selector("div.gl-product-card", timeout=15000)

            # Extract products
            product_elements = page.query_selector_all("div.gl-product-card")
            for el in product_elements[:max_results]:
                try:
                    title = el.query_selector("div.gl-product-card__name")
                    price = el.query_selector("div.gl-price")
                    link = el.query_selector("a.gl-product-card__assets-link")
                    image = el.query_selector("img.gl-product-card__image")

                    if title and link:
                        product_link = link.get_attribute("href")
                        if product_link and not product_link.startswith("http"):
                            product_link = f"https://www.adidas.co.in{product_link}"
                            
                        results.append({
                            "title": title.inner_text().strip() if title else None,
                            "price": price.inner_text().strip() if price else None,
                            "vendor": "Adidas",
                            "link": product_link,
                            "image": image.get_attribute("src") if image else None,
                        })
                except Exception as e:
                    logger.warning(f"Error parsing Adidas product: {e}")
                    continue

            browser.close()
            logger.info(f"Adidas scraping completed: {len(results)} products found")
            
        except Exception as e:
            logger.error(f"Error scraping Adidas: {e}")

    return results

