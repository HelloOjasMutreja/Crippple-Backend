"""
Unified scraper service that aggregates results from multiple apparel websites.
This service scrapes products from Google Shopping, Amazon, Myntra, and other platforms.
"""
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapers.google_shopping_scraper import scrape_google_shopping
from scrapers.amazon_scraper import scrape_amazon
from scrapers.myntra_scraper import scrape_myntra
from scrapers.adidas_scraper import scrape_adidas

logger = logging.getLogger(__name__)


def scrape_all_platforms(query: str, max_results_per_platform: int = 20) -> Dict[str, Any]:
    """
    Scrape multiple platforms concurrently and aggregate results.
    
    Args:
        query: Search query for apparel items
        max_results_per_platform: Maximum number of results to fetch from each platform
        
    Returns:
        Dictionary containing aggregated results from all platforms
    """
    results = {
        'query': query,
        'platforms': {},
        'total_results': 0,
        'errors': []
    }
    
    # Define scraping tasks for all platforms
    scraping_tasks = [
        ('google_shopping', lambda: scrape_google_shopping(query, max_results=max_results_per_platform, headless=True)),
        ('amazon', lambda: scrape_amazon(query, max_results=max_results_per_platform, headless=True)),
        ('myntra', lambda: scrape_myntra(query, max_results=max_results_per_platform, headless=True)),
        ('adidas', lambda: scrape_adidas(query, max_results=max_results_per_platform, headless=True)),
    ]
    
    # Execute scrapers concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_platform = {
            executor.submit(task_func): platform_name 
            for platform_name, task_func in scraping_tasks
        }
        
        for future in as_completed(future_to_platform):
            platform_name = future_to_platform[future]
            try:
                platform_results = future.result(timeout=90)
                results['platforms'][platform_name] = {
                    'count': len(platform_results),
                    'results': platform_results
                }
                results['total_results'] += len(platform_results)
                logger.info(f"Successfully scraped {len(platform_results)} results from {platform_name}")
            except Exception as e:
                error_msg = f"Error scraping {platform_name}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['platforms'][platform_name] = {
                    'count': 0,
                    'results': [],
                    'error': str(e)
                }
    
    return results


def aggregate_and_deduplicate_results(scraping_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Aggregate results from all platforms and remove duplicates.
    
    Args:
        scraping_results: Results from scrape_all_platforms
        
    Returns:
        List of unique products
    """
    all_products = []
    seen_urls = set()
    
    for platform_name, platform_data in scraping_results.get('platforms', {}).items():
        for product in platform_data.get('results', []):
            # Normalize product data
            normalized_product = {
                'title': product.get('title', ''),
                'price': product.get('price', ''),
                'vendor': product.get('vendor', platform_name),
                'link': product.get('link', product.get('url', product.get('product_url', ''))),
                'image': product.get('image', product.get('image_url', '')),
                'source': platform_name,
                'brand': product.get('brand', product.get('vendor', ''))
            }
            
            # Deduplicate by URL
            product_url = normalized_product['link']
            if product_url and product_url not in seen_urls:
                seen_urls.add(product_url)
                all_products.append(normalized_product)
    
    return all_products

