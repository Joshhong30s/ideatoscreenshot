"""Landingfolio scraper — uses Playwright to render JS content."""

from typing import List
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

import httpx
import re


async def search_landingfolio(keyword: str, count: int = 15) -> List[str]:
    """Search Landingfolio for landing page inspiration.

    Landingfolio is JS-rendered — Playwright is preferred.
    """
    if HAS_PLAYWRIGHT:
        return await _search_playwright(keyword, count)
    return await _search_httpx(keyword, count)


async def _search_playwright(keyword: str, count: int) -> List[str]:
    encoded = keyword.replace(" ", "+")
    url = f"https://www.landingfolio.com/?search={encoded}"
    urls: List[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            hrefs = await page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => e.href)",
            )

            for href in hrefs:
                if _is_valid_landing_url(href):
                    if href not in urls:
                        urls.append(href)
        except Exception as e:
            print(f"Landingfolio Playwright error: {e}")
        finally:
            await browser.close()

    return urls[:count]


async def _search_httpx(keyword: str, count: int) -> List[str]:
    """Fallback — may get limited results."""
    encoded = keyword.replace(" ", "+")
    url = f"https://www.landingfolio.com/?search={encoded}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            resp.raise_for_status()
            patterns = [
                r'href="(https?://(?!(?:www\.)?landingfolio\.com)[^"]+)"',
                r'data-url="(https?://[^"]+)"',
                r'data-site="(https?://[^"]+)"',
            ]
            urls: List[str] = []
            for pat in patterns:
                for m in re.findall(pat, resp.text):
                    if _is_valid_landing_url(m) and m not in urls:
                        urls.append(m)
            return urls[:count]
        except Exception as e:
            print(f"Landingfolio httpx error: {e}")
            return []


def _is_valid_landing_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
    except Exception:
        return False

    if not url.startswith("http"):
        return False

    blocked_domains = {
        "landingfolio.com", "www.landingfolio.com",
        "facebook.com", "twitter.com", "x.com",
        "linkedin.com", "instagram.com", "youtube.com",
        "pinterest.com", "google.com", "apple.com",
        "fonts.googleapis.com",
    }
    if domain in blocked_domains:
        return False

    blocked_substrings = [
        "cdn.", "assets.", "analytics", "tracking",
        ".js", ".css", ".png", ".jpg", ".gif", ".svg",
        ".woff", ".ttf", "cloudflare",
    ]
    url_lower = url.lower()
    return not any(b in url_lower for b in blocked_substrings)
