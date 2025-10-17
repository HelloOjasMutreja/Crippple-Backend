#!/usr/bin/env python
"""
Scraper testing utility

This script allows you to test individual scrapers without running the full Django server.
Useful for debugging and verifying scraper functionality.
"""

import sys
import os
import json
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_google_shopping(query, max_results=10):
    """Test Google Shopping scraper"""
    print(f"\n{'='*60}")
    print("Testing Google Shopping Scraper")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Max results: {max_results}")
    print("-" * 60)
    
    try:
        from scrapers.google_shopping_scraper import scrape_google_shopping
        results = scrape_google_shopping(query, max_results=max_results, headless=True)
        
        print(f"✓ Successfully scraped {len(results)} products\n")
        for i, product in enumerate(results[:3], 1):
            print(f"Product {i}:")
            print(f"  Title: {product.get('title', 'N/A')}")
            print(f"  Price: {product.get('price', 'N/A')}")
            print(f"  Vendor: {product.get('vendor', 'N/A')}")
            print(f"  Link: {product.get('link', 'N/A')[:50]}...")
            print()
        
        return results
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_amazon(query, max_results=10):
    """Test Amazon scraper"""
    print(f"\n{'='*60}")
    print("Testing Amazon Scraper")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Max results: {max_results}")
    print("-" * 60)
    
    try:
        from scrapers.amazon_scraper import scrape_amazon
        results = scrape_amazon(query, max_results=max_results, headless=True)
        
        print(f"✓ Successfully scraped {len(results)} products\n")
        for i, product in enumerate(results[:3], 1):
            print(f"Product {i}:")
            print(f"  Title: {product.get('title', 'N/A')}")
            print(f"  Price: {product.get('price', 'N/A')}")
            print(f"  Vendor: {product.get('vendor', 'N/A')}")
            print(f"  Link: {product.get('link', 'N/A')[:50]}...")
            print()
        
        return results
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_myntra(query, max_results=10):
    """Test Myntra scraper"""
    print(f"\n{'='*60}")
    print("Testing Myntra Scraper")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Max results: {max_results}")
    print("-" * 60)
    
    try:
        from scrapers.myntra_scraper import scrape_myntra
        results = scrape_myntra(query, max_results=max_results, headless=True)
        
        print(f"✓ Successfully scraped {len(results)} products\n")
        for i, product in enumerate(results[:3], 1):
            print(f"Product {i}:")
            print(f"  Title: {product.get('title', 'N/A')}")
            print(f"  Price: {product.get('price', 'N/A')}")
            print(f"  Brand: {product.get('brand', 'N/A')}")
            print(f"  Link: {product.get('link', 'N/A')[:50]}...")
            print()
        
        return results
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_adidas(query, max_results=10):
    """Test Adidas scraper"""
    print(f"\n{'='*60}")
    print("Testing Adidas Scraper")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Max results: {max_results}")
    print("-" * 60)
    
    try:
        from scrapers.adidas_scraper import scrape_adidas
        results = scrape_adidas(query, max_results=max_results, headless=True)
        
        print(f"✓ Successfully scraped {len(results)} products\n")
        for i, product in enumerate(results[:3], 1):
            print(f"Product {i}:")
            print(f"  Title: {product.get('title', 'N/A')}")
            print(f"  Price: {product.get('price', 'N/A')}")
            print(f"  Link: {product.get('link', 'N/A')[:50]}...")
            print()
        
        return results
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_unified(query, max_results=10):
    """Test unified scraper"""
    print(f"\n{'='*60}")
    print("Testing Unified Scraper")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Max results per platform: {max_results}")
    print("-" * 60)
    
    try:
        from scrapers.unified_scraper import scrape_all_platforms, aggregate_and_deduplicate_results
        
        results = scrape_all_platforms(query, max_results_per_platform=max_results)
        
        print(f"\n✓ Scraping completed")
        print(f"  Total results: {results['total_results']}")
        print(f"  Platforms:")
        
        for platform, data in results['platforms'].items():
            if 'error' in data:
                print(f"    {platform}: ERROR - {data['error']}")
            else:
                print(f"    {platform}: {data['count']} products")
        
        if results.get('errors'):
            print(f"\n  Errors:")
            for error in results['errors']:
                print(f"    - {error}")
        
        # Show aggregated results
        print(f"\n  Aggregated & Deduplicated:")
        aggregated = aggregate_and_deduplicate_results(results)
        print(f"    Total unique products: {len(aggregated)}")
        
        return results
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}


def main():
    parser = argparse.ArgumentParser(description='Test Crippple Backend scrapers')
    parser.add_argument('scraper', choices=['google', 'amazon', 'myntra', 'adidas', 'unified', 'all'],
                      help='Scraper to test')
    parser.add_argument('query', help='Search query (e.g., "hoodie")')
    parser.add_argument('--max', type=int, default=10, help='Maximum results (default: 10)')
    parser.add_argument('--save', metavar='FILE', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    print("\nCrippple Backend - Scraper Testing Utility")
    print("Note: Make sure Playwright browsers are installed:")
    print("  playwright install chromium")
    
    results = []
    
    if args.scraper == 'google' or args.scraper == 'all':
        results.append(('google_shopping', test_google_shopping(args.query, args.max)))
    
    if args.scraper == 'amazon' or args.scraper == 'all':
        results.append(('amazon', test_amazon(args.query, args.max)))
    
    if args.scraper == 'myntra' or args.scraper == 'all':
        results.append(('myntra', test_myntra(args.query, args.max)))
    
    if args.scraper == 'adidas' or args.scraper == 'all':
        results.append(('adidas', test_adidas(args.query, args.max)))
    
    if args.scraper == 'unified':
        results.append(('unified', test_unified(args.query, args.max)))
    
    # Save results if requested
    if args.save and results:
        output = {
            'query': args.query,
            'scrapers': {name: data for name, data in results}
        }
        with open(args.save, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n✓ Results saved to {args.save}")
    
    print(f"\n{'='*60}")
    print("Testing completed")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
