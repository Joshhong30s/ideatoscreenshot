"""Lapa.ninja scraper — uses Playwright for JS-rendered gallery pages."""

from typing import List
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

import httpx
import re


async def search_lapa(keyword: str, count: int = 15) -> List[str]:
    """Search Lapa.ninja for landing page inspiration.

    Lapa.ninja curates real landing pages. Content is JS-rendered,
    so Playwright is strongly preferred.
    """
    if HAS_PLAYWRIGHT:
        return await _search_playwright(keyword, count)
    return await _search_httpx(keyword, count)


async def _search_playwright(keyword: str, count: int) -> List[str]:
    slug = keyword.lower().replace(" ", "-")
    category_url = f"https://www.lapa.ninja/category/{slug}/"
    search_url = f"https://www.lapa.ninja/search/?q={keyword.replace(' ', '+')}"

    urls: List[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # Try category page first (better structured)
            await page.goto(category_url, timeout=15000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            # Lapa uses card links — target links that point to external sites
            hrefs = await page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => e.href)",
            )
            for href in hrefs:
                if _is_valid_landing_url(href) and href not in urls:
                    urls.append(href)

            # If category gave few results, also try search
            if len(urls) < 5:
                await page.goto(search_url, timeout=15000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)

                hrefs = await page.eval_on_selector_all(
                    "a[href]",
                    "els => els.map(e => e.href)",
                )
                for href in hrefs:
                    if _is_valid_landing_url(href) and href not in urls:
                        urls.append(href)

        except Exception as e:
            print(f"Lapa.ninja Playwright error: {e}")
        finally:
            await browser.close()

    return urls[:count]


async def _search_httpx(keyword: str, count: int) -> List[str]:
    """Fallback — limited results expected."""
    slug = keyword.lower().replace(" ", "-")
    url = f"https://www.lapa.ninja/category/{slug}/"
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
                r'href="(https?://(?!(?:www\.)?lapa\.ninja)[^"]+)"',
                r'data-url="(https?://[^"]+)"',
                r'data-href="(https?://[^"]+)"',
            ]
            urls: List[str] = []
            for pat in patterns:
                for m in re.findall(pat, resp.text):
                    if _is_valid_landing_url(m) and m not in urls:
                        urls.append(m)
            return urls[:count]
        except Exception as e:
            print(f"Lapa.ninja httpx error: {e}")
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
        "lapa.ninja", "www.lapa.ninja",
        "facebook.com", "twitter.com", "x.com",
        "linkedin.com", "instagram.com", "youtube.com",
        "pinterest.com", "google.com", "apple.com",
        "producthunt.com", "buymeacoffee.com",
        "fonts.googleapis.com",
        "webflow.com", "try.webflow.com",
    }
    if domain in blocked_domains:
        return False

    blocked_substrings = [
        "cdn.", "assets.", "analytics", "tracking",
        "framer.link",
        ".js", ".css", ".png", ".jpg", ".gif", ".svg",
        ".woff", ".ttf", "cloudflare", "gravatar.com",
    ]
    url_lower = url.lower()
    return not any(b in url_lower for b in blocked_substrings)
