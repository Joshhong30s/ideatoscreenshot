"""SiteInspire search integration"""

import httpx
from typing import List
import re


async def search_siteinspire(keyword: str, count: int = 15) -> List[str]:
    """Search SiteInspire for curated web designs.
    
    SiteInspire is a showcase of the finest web and interactive design.
    """
    encoded_keyword = keyword.replace(" ", "+")
    url = f"https://www.siteinspire.com/websites?search={encoded_keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            
            urls = extract_siteinspire_urls(response.text)
            return urls[:count]
        except Exception as e:
            print(f"SiteInspire search error: {e}")
            return []


def extract_siteinspire_urls(html: str) -> List[str]:
    """Extract website URLs from SiteInspire HTML."""
    urls = []
    
    # SiteInspire lists actual website URLs
    patterns = [
        r'href="(https?://(?!www\.siteinspire\.com)[^"]+)"',
        r'data-href="(https?://[^"]+)"',
        r'class="website-link"[^>]*href="(https?://[^"]+)"',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            if is_valid_design_url(match):
                if match not in urls:
                    urls.append(match)
    
    return urls


def is_valid_design_url(url: str) -> bool:
    """Check if URL is likely a real website."""
    excluded = [
        'siteinspire.com',
        'facebook.com',
        'twitter.com',
        'linkedin.com',
        'instagram.com',
        'google.com',
        'youtube.com',
        'cdn.',
        'assets.',
        '.js',
        '.css',
    ]
    
    url_lower = url.lower()
    for exc in excluded:
        if exc in url_lower:
            return False
    
    return url.startswith('http')
