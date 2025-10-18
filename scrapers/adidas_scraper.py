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
                args=[
                    "--disable-http2",
                    "--disable-features=NetworkService",
                    "--disable-blink-features=AutomationControlled",
                ]
            )

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/127.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
            )

            page = context.new_page()
            
            # Apply stealth if available
            try:
                from playwright_stealth import stealth_sync
                stealth_sync(page)
            except ImportError:
                logger.warning("playwright-stealth not available, skipping stealth mode")

            logger.info(f"Scraping Adidas: {url}")
            
            # Try to load the page with fallback wait strategies
            try:
                page.goto(url, timeout=60000, wait_until="networkidle")
            except Exception as e:
                logger.warning(f"Adidas page load with networkidle failed: {e}, trying domcontentloaded...")
                try:
                    page.goto(url, timeout=45000, wait_until="domcontentloaded")
                    # Give extra time for JS to render products
                    page.wait_for_timeout(3000)
                except Exception as e2:
                    logger.error(f"Adidas page load failed completely: {e2}")
                    raise

            # Wait for product grid to load with more flexible timeout
            try:
                page.wait_for_selector("div.gl-product-card", timeout=20000)
            except Exception as e:
                logger.warning(f"Product cards not found within timeout, checking if any loaded: {e}")
                # Continue anyway in case some products loaded

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

