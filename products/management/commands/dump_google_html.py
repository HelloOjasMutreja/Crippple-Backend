from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
import os

class Command(BaseCommand):
    help = "Dump Google Shopping HTML snapshot for a given query"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Search query (e.g. hoodie)")

    def handle(self, *args, **options):
        query = options["query"]
        os.makedirs("snapshots", exist_ok=True)
        file_path = f"snapshots/google_{query}.html"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = f"https://www.google.com/search?tbm=shop&q={query}"
            page.goto(url, timeout=60000)
            html = page.content()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)

            browser.close()

        self.stdout.write(self.style.SUCCESS(f"✅ HTML snapshot saved to {file_path}"))
