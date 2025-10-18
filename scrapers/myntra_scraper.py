from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)


def scrape_myntra(query="hoodie", max_results=20, headless=True):
    """
    Scrape Myntra for products matching the query.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        headless: Run browser in headless mode
        
    Returns:
        List of product dictionaries
    """
    results = []

    with sync_playwright() as p:
        try:
            # Disable HTTP/2 to avoid ERR_HTTP2_PROTOCOL_ERROR
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-http2",
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
                    "Referer": "https://www.myntra.com/",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
            )
            page = context.new_page()

            url = f"https://www.myntra.com/{query}"
            logger.info(f"Scraping Myntra: {url}")
            
            # Try to load the page with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Myntra page load attempt {attempt + 1} failed: {e}, retrying...")
                        page.wait_for_timeout(2000)
                    else:
                        raise

            page.wait_for_selector(".product-base", timeout=15000)
            items = page.query_selector_all(".product-base")

            for item in items[:max_results]:
                try:
                    title = item.query_selector("h3").inner_text() if item.query_selector("h3") else None
                    brand = item.query_selector("h4").inner_text() if item.query_selector("h4") else None
                    price_elem = item.query_selector(".product-price span")
                    price = price_elem.inner_text().replace("Rs. ", "").replace(",", "") if price_elem else None
                    link_elem = item.query_selector("a")
                    product_url = link_elem.get_attribute("href") if link_elem else None
                    image_elem = item.query_selector("img")
                    image_url = image_elem.get_attribute("src") if image_elem else None

                    if title and brand and product_url:
                        results.append({
                            "title": f"{brand} {title}".strip(),
                            "price": f"₹{price}" if price else None,
                            "vendor": "Myntra",
                            "brand": brand,
                            "link": f"https://www.myntra.com{product_url}" if product_url.startswith("/") else product_url,
                            "image": image_url,
                        })
                except Exception as e:
                    logger.warning(f"Error parsing Myntra product: {e}")
                    continue

            browser.close()
            logger.info(f"Myntra scraping completed: {len(results)} products found")
            
        except Exception as e:
            logger.error(f"Error scraping Myntra: {e}")

    return results

