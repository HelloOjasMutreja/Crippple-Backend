from django.http import JsonResponse
from django.views.decorators.http import require_GET
from scrapers.google_shopping_scraper import scrape_google_shopping

@require_GET
def google_shopping_search(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"error": "query parameter 'q' required"}, status=400)

    # Quick, synchronous call — keep pages small in HTTP request
    results = scrape_google_shopping(q, headless=True)
    return JsonResponse({"query": q, "count": len(results), "results": results})
