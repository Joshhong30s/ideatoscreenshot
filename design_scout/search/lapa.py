"""Lapa.ninja scraper - Landing page gallery (uses Playwright for JS rendering)"""

import asyncio
from typing import List
import re

# Try Playwright first, fall back to httpx
try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

import httpx


async def search_lapa(keyword: str, count: int = 15) -> List[str]:
    """Search Lapa.ninja for landing page inspiration.
    
    Lapa.ninja curates real landing pages from operating businesses.
    Uses category pages which have better structure than search.
    
    Args:
        keyword: Search term (e.g., "fintech", "saas")
        count: Max URLs to return
        
    Returns:
        List of website URLs
    """
    if HAS_PLAYWRIGHT:
        return await search_lapa_playwright(keyword, count)
    else:
        return await search_lapa_httpx(keyword, count)


async def search_lapa_playwright(keyword: str, count: int = 15) -> List[str]:
    """Use Playwright to handle JS-rendered content."""
    # Try category page first (more reliable)
    category_url = f"https://www.lapa.ninja/category/{keyword.lower().replace(' ', '-')}/"
    search_url = f"https://www.lapa.ninja/search/?q={keyword.replace(' ', '+')}"
    
    urls = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Try category page first
            await page.goto(category_url, timeout=15000)
            await page.wait_for_timeout(2000)  # Wait for JS
            
            # Extract links from the page
            links = await page.eval_on_selector_all(
                'a[href^="http"]',
                'elements => elements.map(e => e.href)'
            )
            
            for link in links:
                if is_valid_landing_url(link):
                    if link not in urls:
                        urls.append(link)
            
            # If category didn't work, try search
            if len(urls) < 5:
                await page.goto(search_url, timeout=15000)
                await page.wait_for_timeout(2000)
                
                links = await page.eval_on_selector_all(
                    'a[href^="http"]',
                    'elements => elements.map(e => e.href)'
                )
                
                for link in links:
                    if is_valid_landing_url(link):
                        if link not in urls:
                            urls.append(link)
                            
        except Exception as e:
            print(f"Lapa.ninja Playwright error: {e}")
        finally:
            await browser.close()
    
    return urls[:count]


async def search_lapa_httpx(keyword: str, count: int = 15) -> List[str]:
    """Fallback to httpx (may get limited results due to JS rendering)."""
    # Try category URL format
    category_url = f"https://www.lapa.ninja/category/{keyword.lower().replace(' ', '-')}/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(category_url, headers=headers, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            
            urls = extract_lapa_urls(response.text)
            return urls[:count]
        except Exception as e:
            print(f"Lapa.ninja httpx error: {e}")
            return []


def extract_lapa_urls(html: str) -> List[str]:
    """Extract website URLs from Lapa.ninja HTML."""
    urls = []
    
    # Look for external links
    patterns = [
        r'href="(https?://(?!(?:www\.)?lapa\.ninja)[^"]+)"',
        r'data-url="(https?://[^"]+)"',
        r'data-href="(https?://[^"]+)"',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            if is_valid_landing_url(match):
                if match not in urls:
                    urls.append(match)
    
    return urls


def is_valid_landing_url(url: str) -> bool:
    """Check if URL is likely a real landing page."""
    excluded = [
        'lapa.ninja',
        'facebook.com',
        'twitter.com',
        'linkedin.com',
        'instagram.com',
        'youtube.com',
        'pinterest.com',
        'google.com',
        'apple.com',
        'producthunt.com',
        'buymeacoffee.com',
        'cdn.',
        'assets.',
        '.js',
        '.css',
        '.png',
        '.jpg',
        '.gif',
        '.svg',
        '.woff',
        '.ttf',
        'fonts.googleapis',
        'analytics',
        'tracking',
        'gravatar.com',
        'cloudflare',
    ]
    
    url_lower = url.lower()
    for exc in excluded:
        if exc in url_lower:
            return False
    
    return url.startswith('http')
