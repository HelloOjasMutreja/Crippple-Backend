#!/usr/bin/env python3
"""
Environment checker for Crippple Backend scrapers.
Verifies that all required dependencies are installed and configured.
"""

import sys
import os

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need Python 3.8+)")
        return False

def check_module(module_name, package_name=None):
    """Check if a Python module is installed"""
    package = package_name or module_name
    try:
        __import__(module_name)
        print(f"  ✓ {package} installed")
        return True
    except ImportError:
        print(f"  ✗ {package} NOT installed - run: pip install {package}")
        return False

def check_playwright_browsers():
    """Check if Playwright browsers are installed"""
    print("Checking Playwright browsers...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print(f"  ✓ Chromium browser installed")
                return True
            except Exception as e:
                print(f"  ✗ Chromium browser NOT installed - run: playwright install chromium")
                print(f"     Error: {e}")
                return False
    except ImportError:
        print(f"  ✗ Playwright not installed")
        return False

def check_django_settings():
    """Check if Django settings are accessible"""
    print("Checking Django configuration...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crippple_backend.settings')
        import django
        django.setup()
        print(f"  ✓ Django settings loaded")
        return True
    except Exception as e:
        print(f"  ✗ Django settings error: {e}")
        return False

def check_scrapers():
    """Check if scraper modules can be imported"""
    print("Checking scraper modules...")
    scrapers = [
        'scrapers.google_shopping_scraper',
        'scrapers.amazon_scraper',
        'scrapers.myntra_scraper',
        'scrapers.adidas_scraper',
        'scrapers.unified_scraper',
    ]
    
    all_ok = True
    for scraper in scrapers:
        try:
            __import__(scraper)
            print(f"  ✓ {scraper}")
        except Exception as e:
            print(f"  ✗ {scraper}: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 70)
    print("Crippple Backend - Environment Check")
    print("=" * 70)
    print()
    
    checks = []
    
    # Check Python version
    checks.append(("Python version", check_python_version()))
    print()
    
    # Check required modules
    print("Checking required Python packages...")
    checks.append(("playwright", check_module("playwright")))
    checks.append(("playwright-stealth", check_module("playwright_stealth", "playwright-stealth")))
    checks.append(("django", check_module("django", "Django")))
    checks.append(("rest_framework", check_module("rest_framework", "djangorestframework")))
    checks.append(("requests", check_module("requests")))
    print()
    
    # Check Playwright browsers
    checks.append(("Playwright browsers", check_playwright_browsers()))
    print()
    
    # Check Django settings
    checks.append(("Django settings", check_django_settings()))
    print()
    
    # Check scrapers
    checks.append(("Scraper modules", check_scrapers()))
    print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print()
        print("✓ All checks passed! Environment is ready.")
        print()
        print("You can now:")
        print("  - Run scrapers: python test_scrapers.py unified \"hoodie\"")
        print("  - Start server: python manage.py runserver")
        print("  - Test API: curl http://localhost:8000/api/search/?q=hoodie")
        return 0
    else:
        print()
        print("✗ Some checks failed. Please fix the issues above.")
        print()
        print("Quick fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Install browsers: playwright install chromium")
        print("  - Install system deps: playwright install-deps chromium")
        return 1

if __name__ == '__main__':
    sys.exit(main())
