from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)


def scrape_amazon(query="hoodie", max_results=20, headless=True):
    """
    Scrape Amazon India for products matching the query.
    
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
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/117.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            url = f"https://www.amazon.in/s?k={query}"
            logger.info(f"Scraping Amazon: {url}")
            page.goto(url, timeout=30000)

            items = page.locator(".s-result-item[data-component-type='s-search-result']")
            count = min(items.count(), max_results)
            
            for i in range(count):
                try:
                    item = items.nth(i)
                    
                    # Extract title
                    title_elem = item.locator("h2 a span")
                    title = title_elem.inner_text(timeout=2000) if title_elem.count() > 0 else None
                    
                    # Extract link
                    link_elem = item.locator("h2 a")
                    link = link_elem.get_attribute("href", timeout=2000) if link_elem.count() > 0 else None
                    
                    # Extract price
                    price_elem = item.locator(".a-price-whole")
                    price = price_elem.inner_text(timeout=2000) if price_elem.count() > 0 else None
                    
                    # Extract image
                    img_elem = item.locator("img.s-image")
                    img = img_elem.get_attribute("src", timeout=2000) if img_elem.count() > 0 else None

                    if title and link:
                        product_url = f"https://www.amazon.in{link}" if link.startswith("/") else link
                        results.append({
                            "title": title.strip(),
                            "price": price.strip() if price else None,
                            "vendor": "Amazon India",
                            "link": product_url,
                            "image": img,
                        })
                except Exception as e:
                    logger.warning(f"Error parsing Amazon product {i}: {e}")
                    continue

            browser.close()
            logger.info(f"Amazon scraping completed: {len(results)} products found")
            
        except Exception as e:
            logger.error(f"Error scraping Amazon: {e}")
            
    return results

