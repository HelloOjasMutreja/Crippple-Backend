from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from scrapers.unified_scraper import scrape_all_platforms, aggregate_and_deduplicate_results
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def search_apparel(request):
    """
    Unified apparel search endpoint that scrapes multiple platforms.
    
    Query Parameters:
        q (str): Search query for apparel items (required)
        max_per_platform (int): Maximum results per platform (default: 20)
        format (str): Response format - 'grouped' or 'flat' (default: 'flat')
    
    Returns:
        JSON response with aggregated search results
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return Response(
            {"error": "query parameter 'q' is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    max_per_platform = int(request.GET.get("max_per_platform", 20))
    response_format = request.GET.get("format", "flat").lower()
    
    try:
        logger.info(f"Searching for: {query}")
        
        # Scrape all platforms
        scraping_results = scrape_all_platforms(query, max_results_per_platform=max_per_platform)
        
        if response_format == "grouped":
            # Return grouped by platform
            return Response({
                "query": query,
                "total_results": scraping_results['total_results'],
                "platforms": scraping_results['platforms'],
                "errors": scraping_results.get('errors', [])
            })
        else:
            # Return flat list of deduplicated products
            products = aggregate_and_deduplicate_results(scraping_results)
            return Response({
                "query": query,
                "count": len(products),
                "results": products,
                "errors": scraping_results.get('errors', [])
            })
            
    except Exception as e:
        logger.error(f"Error in search_apparel: {str(e)}", exc_info=True)
        return Response(
            {"error": f"Search failed: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Legacy endpoint for backward compatibility
@require_GET
def google_shopping_search(request):
    """
    Legacy Google Shopping search endpoint (deprecated - use /api/search/ instead).
    """
    from scrapers.google_shopping_scraper import scrape_google_shopping
    
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"error": "query parameter 'q' required"}, status=400)

    results = scrape_google_shopping(q, headless=True)
    return JsonResponse({"query": q, "count": len(results), "results": results})

