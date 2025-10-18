# Scraping Fixes Documentation

## Issues Addressed

This document describes the fixes applied to resolve web scraping issues reported in the GitHub issue.

### Original Problems

1. **Myntra**: `ERR_HTTP2_PROTOCOL_ERROR` when trying to scrape products
2. **Adidas**: `Timeout 60000ms exceeded` - pages taking too long to load
3. **Google Shopping**: "No product nodes found" - stale selectors

## Solutions Implemented

### 1. Myntra Scraper Fixes

**Problem**: HTTP/2 protocol errors preventing page loads

**Solutions**:
- Added `--disable-http2` browser launch flag to force HTTP/1.1
- Added `--disable-blink-features=AutomationControlled` to reduce bot detection
- Implemented retry logic (2 attempts) for page loads
- Updated User-Agent to Chrome 127
- Increased viewport size to 1920x1080 for more realistic browsing
- Added comprehensive HTTP headers (Accept, Accept-Language, DNT, etc.)

**Code Changes** (`scrapers/myntra_scraper.py`):
```python
browser = p.chromium.launch(
    headless=headless,
    args=[
        "--disable-http2",
        "--disable-blink-features=AutomationControlled",
    ]
)
# ... with retry logic
max_retries = 2
for attempt in range(max_retries):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            logger.warning(f"Myntra page load attempt {attempt + 1} failed: {e}, retrying...")
            page.wait_for_timeout(2000)
        else:
            raise
```

### 2. Adidas Scraper Fixes

**Problem**: Timeout errors when waiting for page to become idle

**Solutions**:
- Added `--disable-http2` flag to avoid protocol issues
- Implemented fallback wait strategy: tries `networkidle` first, falls back to `domcontentloaded`
- Added extra 3-second wait after domcontentloaded for JS rendering
- Increased product card wait timeout to 20 seconds
- Made selector waiting non-blocking (continues even if timeout occurs)
- Updated browser configuration with anti-detection measures

**Code Changes** (`scrapers/adidas_scraper.py`):
```python
# Fallback wait strategy
try:
    page.goto(url, timeout=60000, wait_until="networkidle")
except Exception as e:
    logger.warning(f"Adidas page load with networkidle failed: {e}, trying domcontentloaded...")
    try:
        page.goto(url, timeout=45000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)  # Extra time for JS
    except Exception as e2:
        logger.error(f"Adidas page load failed completely: {e2}")
        raise

# Non-blocking selector wait
try:
    page.wait_for_selector("div.gl-product-card", timeout=20000)
except Exception as e:
    logger.warning(f"Product cards not found within timeout, checking if any loaded: {e}")
    # Continue anyway in case some products loaded
```

### 3. Google Shopping Scraper Fixes

**Problem**: Stale selectors causing "No product nodes found" errors

**Solutions**:
- Added alternative selector fallback system
- Added `--disable-blink-features=AutomationControlled` for better access
- Updated User-Agent and viewport
- Added comprehensive HTTP headers

**Code Changes** (`scrapers/google_shopping_scraper.py`):
```python
cards = page.query_selector_all(selectors["product_card"])
if not cards:
    print("⚠️ No product nodes found. Selectors may be stale. Update google_selectors.json")
    # Try alternative selectors as fallback
    alternative_selectors = [
        "div.sh-dgr__grid-result",
        "div[data-docid]",
        "div.sh-dgr__content",
    ]
    for alt_selector in alternative_selectors:
        print(f"⚠️ Trying alternative selector: {alt_selector}")
        cards = page.query_selector_all(alt_selector)
        if cards:
            print(f"✓ Found {len(cards)} products with alternative selector: {alt_selector}")
            break
```

### 4. Amazon Scraper Improvements

**Problem**: General improvements for consistency

**Solutions**:
- Updated browser configuration for consistency with other scrapers
- Added `--disable-blink-features=AutomationControlled`
- Changed wait strategy to `domcontentloaded` with explicit 2-second wait
- Updated User-Agent and viewport
- Added comprehensive HTTP headers

## Common Improvements Applied to All Scrapers

1. **Browser Launch Arguments**:
   - `--disable-http2`: Forces HTTP/1.1 to avoid HTTP/2 protocol issues
   - `--disable-blink-features=AutomationControlled`: Reduces bot detection
   - `--disable-features=NetworkService`: Additional network-related fixes (Adidas)

2. **User-Agent**:
   - Updated to Chrome 127: `Chrome/127.0.0.0`
   - More recent and realistic user agent string

3. **Viewport**:
   - Increased from 1280x800 to 1920x1080
   - More common desktop resolution

4. **HTTP Headers**:
   - Added `Accept` header with proper MIME types
   - Added `Accept-Language` for localization
   - Added `Accept-Encoding` for compression support
   - Added `DNT` (Do Not Track) header
   - Added `Connection: keep-alive`
   - Added `Upgrade-Insecure-Requests`

5. **Error Handling**:
   - Better logging of errors
   - Graceful degradation (continues when possible)
   - Retry logic where appropriate

## Testing Recommendations

To verify these fixes work:

1. **Test Individual Scrapers**:
   ```bash
   python test_scrapers.py myntra "sweatshirt" --max 10
   python test_scrapers.py adidas "sweatshirt" --max 10
   python test_scrapers.py google "sweatshirt" --max 10
   python test_scrapers.py amazon "sweatshirt" --max 10
   ```

2. **Test Unified Scraper**:
   ```bash
   python test_scrapers.py unified "sweatshirt" --max 10
   ```

3. **Test via Django API**:
   ```bash
   python manage.py runserver
   # Then visit: http://localhost:8000/api/search/?q=sweatshirt
   ```

## Troubleshooting

### If Myntra Still Fails

1. Check if Myntra has additional anti-scraping measures
2. Try adding delays: `page.wait_for_timeout(3000)` after page load
3. Consider using residential proxies
4. Check if the URL format is still valid

### If Adidas Still Times Out

1. Increase timeout values in `page.goto()`
2. Try disabling images to speed up loading:
   ```python
   context = browser.new_context(
       ...,
       permissions=[],
       extra_http_headers={...},
       # Block images
       ignore_https_errors=True,
   )
   await context.route("**/*.{png,jpg,jpeg,gif,svg,ico,webp}", lambda route: route.abort())
   ```
3. Check network connectivity to Adidas India website

### If Google Shopping Selectors Fail

1. Update `google_selectors.json` with current selectors
2. Use browser DevTools to inspect current Google Shopping page structure
3. The fallback selectors should handle most cases, but Google changes their HTML frequently

### General Tips

1. **Playwright Stealth**: The code already tries to use `playwright-stealth` for Adidas if available
2. **Rate Limiting**: Add delays between requests if scraping multiple queries
3. **Proxies**: Consider using proxy rotation if getting blocked
4. **Headless Mode**: Try running with `headless=False` for debugging
5. **Captchas**: Some sites may still present captchas - monitor logs for such issues

## Expected Improvements

After these fixes:
- **Myntra**: Should load successfully without HTTP/2 errors
- **Adidas**: Should load with fallback wait strategy, avoiding most timeouts
- **Google Shopping**: Should find products using fallback selectors
- **Amazon**: Should load more reliably with improved configuration

## Monitoring

Watch server logs for these messages:
- ✓ Success: `"Myntra scraping completed: X products found"`
- ✓ Success: `"Adidas scraping completed: X products found"`
- ⚠️ Warning: `"playwright-stealth not available"` (non-critical)
- ⚠️ Warning: `"Product cards not found within timeout"` (may still get partial results)
- ✗ Error: `"Error scraping [Platform]"` (check specific error message)

## Future Improvements

Consider implementing:
1. **Proxy Rotation**: Use proxy services to avoid IP-based blocking
2. **Session Management**: Reuse browser contexts for faster subsequent requests
3. **Caching**: Cache results for popular queries
4. **Monitoring**: Add metrics for scraper success rates
5. **Dynamic Selector Updates**: Automatically detect and adapt to selector changes
6. **API Alternatives**: Use official APIs where available instead of scraping
