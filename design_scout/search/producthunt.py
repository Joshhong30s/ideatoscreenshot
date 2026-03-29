"""Product Hunt scraper — uses Playwright to render JS-heavy SPA."""

from typing import List
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

import httpx


async def search_producthunt(keyword: str, count: int = 15) -> List[str]:
    """Search Product Hunt for product landing pages.

    Product Hunt is a React SPA — httpx alone cannot extract links.
    Falls back to httpx if Playwright is unavailable (likely 0 results).
    """
    if HAS_PLAYWRIGHT:
        return await _search_playwright(keyword, count)
    return await _search_httpx(keyword, count)


async def _search_playwright(keyword: str, count: int) -> List[str]:
    encoded = keyword.replace(" ", "+")
    url = f"https://www.producthunt.com/search?q={encoded}"
    urls: List[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=20000, wait_until="domcontentloaded")
            # Wait for search results to render
            await page.wait_for_timeout(3000)

            # Product Hunt product cards link to /posts/xxx with an external
            # "visit" link, or show the product URL in data attributes.
            # Strategy: grab all <a> hrefs, then keep external ones.
            hrefs = await page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => e.href)",
            )

            for href in hrefs:
                if _is_external_product_url(href):
                    if href not in urls:
                        urls.append(href)
        except Exception as e:
            print(f"Product Hunt Playwright error: {e}")
        finally:
            await browser.close()

    return urls[:count]


async def _search_httpx(keyword: str, count: int) -> List[str]:
    """Fallback — unlikely to yield results for this SPA site."""
    encoded = keyword.replace(" ", "+")
    url = f"https://www.producthunt.com/search?q={encoded}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            resp.raise_for_status()
            # Best-effort: look for JSON-embedded URLs
            import re
            pattern = r'"(https?://(?!(?:www\.)?producthunt\.com)[^"]+)"'
            matches = re.findall(pattern, resp.text)
            return [m for m in matches if _is_external_product_url(m)][:count]
        except Exception as e:
            print(f"Product Hunt httpx error: {e}")
            return []


def _is_external_product_url(url: str) -> bool:
    """Keep real product websites, filter noise."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
    except Exception:
        return False

    if not url.startswith("http"):
        return False

    blocked_domains = {
        "producthunt.com", "www.producthunt.com",
        "facebook.com", "twitter.com", "x.com",
        "linkedin.com", "instagram.com", "youtube.com",
        "pinterest.com", "google.com", "apple.com",
        "github.com", "gravatar.com",
        "fonts.googleapis.com", "cdn.jsdelivr.net",
    }
    if domain in blocked_domains:
        return False

    blocked_substrings = [
        "cdn.", "assets.", "analytics", "tracking",
        ".js", ".css", ".png", ".jpg", ".gif", ".svg",
        ".woff", ".ttf", "cloudflare", "stripe.com",
        "intercom.io", "crisp.chat", "hotjar.com",
        "sentry.io", "segment.com",
    ]
    url_lower = url.lower()
    return not any(b in url_lower for b in blocked_substrings)
