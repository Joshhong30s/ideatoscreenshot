"""Awwwards scraper"""

import httpx
from typing import List
import re


async def search_awwwards(keyword: str, count: int = 10) -> List[str]:
    """Search Awwwards for award-winning designs.
    
    Awwwards showcases the best web design talent.
    """
    # Awwwards search URL
    encoded_keyword = keyword.replace(" ", "+")
    url = f"https://www.awwwards.com/websites/?q={encoded_keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            
            urls = extract_awwwards_urls(response.text)
            return urls[:count]
        except Exception as e:
            print(f"Awwwards search error: {e}")
            return []


def extract_awwwards_urls(html: str) -> List[str]:
    """Extract website URLs from Awwwards HTML."""
    urls = []
    
    # Awwwards stores website URLs in data attributes or links
    # Pattern for site links (they usually link to the actual website)
    patterns = [
        r'href="(https?://(?!www\.awwwards\.com)[^"]+)"',
        r'data-url="(https?://[^"]+)"',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            if is_valid_design_url(match):
                if match not in urls:
                    urls.append(match)
    
    return urls


def is_valid_design_url(url: str) -> bool:
    """Check if URL is likely a design showcase site."""
    excluded = [
        'awwwards.com',
        'facebook.com',
        'twitter.com',
        'linkedin.com',
        'instagram.com',
        'youtube.com',
        'pinterest.com',
        'behance.net',
        'dribbble.com',
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
    ]
    
    url_lower = url.lower()
    for exc in excluded:
        if exc in url_lower:
            return False
    
    return url.startswith('http')
