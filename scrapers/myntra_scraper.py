from playwright.sync_api import sync_playwright
from products.models import Product

def scrape_myntra(query="hoodie", pages=1):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.myntra.com/",
            },
        )
        page = context.new_page()

        for page_num in range(1, pages + 1):
            url = f"https://www.myntra.com/{query}?p={page_num}"
            print(f"Navigating to {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            page.wait_for_selector(".product-base", timeout=15000)
            items = page.query_selector_all(".product-base")

            for item in items:
                title = item.query_selector("h3").inner_text() if item.query_selector("h3") else None
                brand = item.query_selector("h4").inner_text() if item.query_selector("h4") else None
                price_elem = item.query_selector(".product-price span")
                price = price_elem.inner_text().replace("Rs. ", "").replace(",", "") if price_elem else None
                link_elem = item.query_selector("a")
                product_url = link_elem.get_attribute("href") if link_elem else None
                image_elem = item.query_selector("img")
                image_url = image_elem.get_attribute("src") if image_elem else None

                if title and brand and price and product_url:
                    # ✅ store product synchronously (outside async)
                    product, _ = Product.objects.get_or_create(
                        title=f"{brand} {title}",
                        product_url="https://www.myntra.com" + product_url,
                        defaults={
                            "image_url": image_url,
                            "price": price,
                            "source": "Myntra",
                            "brand": brand,
                        },
                    )
                    results.append(product)

        browser.close()

    return results
