from django.core.management.base import BaseCommand
from scrapers.google_shopping_scraper import scrape_google_shopping
import json

class Command(BaseCommand):
    help = "Scrape Google Shopping for a given query"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Search query (e.g. hoodie)")
        parser.add_argument("--max", type=int, default=20, help="Max results to fetch")

    def handle(self, *args, **options):
        query = options["query"]
        max_results = options["max"]

        self.stdout.write(f"🔎 Searching Google Shopping for: {query}")
        results = scrape_google_shopping(query, max_results=max_results)

        if not results:
            self.stdout.write(self.style.WARNING("No results found. Selectors may need update."))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Found {len(results)} results"))
            self.stdout.write(json.dumps(results, indent=2, ensure_ascii=False))
