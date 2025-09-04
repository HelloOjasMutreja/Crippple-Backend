from django.core.management.base import BaseCommand
from scrapers.myntra_scraper import scrape_myntra

class Command(BaseCommand):
    help = "Scrape products from Myntra"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Search query, e.g. hoodie")

    def handle(self, *args, **kwargs):
        query = kwargs["query"]
        products = scrape_myntra(query)
        self.stdout.write(self.style.SUCCESS(f"Scraped {len(products)} products from Myntra for '{query}'"))
