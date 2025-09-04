# products/management/commands/scrape_adidas.py
from django.core.management.base import BaseCommand
from scrapers.adidas_scraper import scrape_adidas
from products.models import Product  # adjust if your model path differs

class Command(BaseCommand):
    help = "Scrape Adidas for products by query"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Search query (e.g., hoodie)")

    def handle(self, *args, **options):
        query = options["query"]
        products_data = scrape_adidas(query)

        self.stdout.write(self.style.SUCCESS(f"Scraped {len(products_data)} products."))

        saved_count = 0
        for data in products_data:
            if data["title"] and data["url"]:
                Product.objects.get_or_create(
                    title=data["title"],
                    defaults={
                        "price": data.get("price"),
                        "url": data.get("url"),
                        "source": "adidas",
                    },
                )
                saved_count += 1

        self.stdout.write(self.style.SUCCESS(f"Saved {saved_count} new products."))
