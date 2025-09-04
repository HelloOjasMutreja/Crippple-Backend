from django.core.management.base import BaseCommand
from scrapers.amazon_scraper import scrape_amazon

class Command(BaseCommand):
    help = "Scrape products from Amazon and save to DB"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Search query, e.g. hoodie")

    def handle(self, *args, **kwargs):
        query = kwargs["query"]
        products = scrape_amazon(query)
        self.stdout.write(self.style.SUCCESS(f"Scraped {len(products)} products for '{query}'"))
