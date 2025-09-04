from playwright.sync_api import sync_playwright
from products.models import Product

def scrape_amazon(query="hoodie"):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://www.amazon.in/s?k={query}", timeout=10000)

        items = page.locator(".s-result-item")

        for i in range(items.count()):
            try:
                title = items.nth(i).locator("h2 a span").inner_text(timeout=2000)
                link = items.nth(i).locator("h2 a").get_attribute("href")
                price = items.nth(i).locator(".a-price-whole").inner_text(timeout=2000)
                img = items.nth(i).locator("img").get_attribute("src")

                if title and link and price and img:
                    product = Product.objects.create(
                        title=title,
                        image_url=img,
                        price=price.replace(",", ""),
                        source="Amazon",
                        product_url="https://www.amazon.in" + link,
                    )
                    results.append(product)
            except:
                continue

        browser.close()
    return results
