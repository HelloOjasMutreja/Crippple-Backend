"""
Example usage of the Crippple Backend API

This script demonstrates how to use the unified search endpoint
to search for apparel across multiple platforms.
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def search_apparel(query, format="flat", max_per_platform=20):
    """
    Search for apparel across multiple platforms
    
    Args:
        query: Search term (e.g., "hoodie", "jeans")
        format: Response format - "flat" or "grouped"
        max_per_platform: Maximum results per platform
        
    Returns:
        API response as dictionary
    """
    endpoint = f"{BASE_URL}/api/search/"
    params = {
        "q": query,
        "format": format,
        "max_per_platform": max_per_platform
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


def main():
    print("=" * 60)
    print("Crippple Backend - Unified Apparel Search Example")
    print("=" * 60)
    
    # Example 1: Basic search with flat format
    print("\n1. Basic Search - Flat Format")
    print("-" * 60)
    query = "hoodie"
    print(f"Searching for: {query}")
    result = search_apparel(query, format="flat")
    
    if result:
        print(f"✓ Found {result.get('count', 0)} products")
        print(f"✓ Query: {result.get('query')}")
        
        # Show first 3 results
        products = result.get('results', [])
        for i, product in enumerate(products[:3], 1):
            print(f"\n  Product {i}:")
            print(f"    Title: {product.get('title')}")
            print(f"    Price: {product.get('price')}")
            print(f"    Source: {product.get('source')}")
            print(f"    Link: {product.get('link')}")
    else:
        print("✗ Search failed")
    
    # Example 2: Search with grouped format
    print("\n\n2. Search - Grouped Format")
    print("-" * 60)
    query = "sneakers"
    print(f"Searching for: {query}")
    result = search_apparel(query, format="grouped", max_per_platform=10)
    
    if result:
        print(f"✓ Total results: {result.get('total_results', 0)}")
        print(f"✓ Platforms:")
        
        platforms = result.get('platforms', {})
        for platform_name, platform_data in platforms.items():
            count = platform_data.get('count', 0)
            error = platform_data.get('error')
            
            if error:
                print(f"    {platform_name}: ERROR - {error}")
            else:
                print(f"    {platform_name}: {count} products")
    else:
        print("✗ Search failed")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\nNOTE: Make sure the Django server is running:")
    print("  python manage.py runserver")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
