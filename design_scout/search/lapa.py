"""Lapa.ninja scraper - Landing page gallery"""

import httpx
from typing import List
import re


async def search_lapa(keyword: str, count: int = 15) -> List[str]:
    """Search Lapa.ninja for landing page inspiration.
    
    Lapa.ninja curates real landing pages from operating businesses.
    
    Args:
        keyword: Search term (e.g., "fintech", "saas")
        count: Max URLs to return
        
    Returns:
        List of website URLs
    """
    encoded_keyword = keyword.replace(" ", "+")
    url = f"https://www.lapa.ninja/search/?q={encoded_keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            
            urls = extract_lapa_urls(response.text)
            return urls[:count]
        except httpx.TimeoutException:
            print(f"Lapa.ninja search timeout")
            return []
        except httpx.HTTPStatusError as e:
            print(f"Lapa.ninja HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"Lapa.ninja search error: {e}")
            return []


def extract_lapa_urls(html: str) -> List[str]:
    """Extract website URLs from Lapa.ninja HTML."""
    urls = []
    
    # Lapa.ninja stores links to actual websites
    # Look for external links that aren't lapa.ninja itself
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
    ]
    
    url_lower = url.lower()
    for exc in excluded:
        if exc in url_lower:
            return False
    
    return url.startswith('http')
