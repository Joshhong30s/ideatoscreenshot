"""Product Hunt scraper - Find trending products and their landing pages"""

import httpx
from typing import List
import re


async def search_producthunt(keyword: str, count: int = 15) -> List[str]:
    """Search Product Hunt for product landing pages.
    
    Product Hunt showcases new tech products with links to their websites.
    Great for finding real, operating startup landing pages.
    
    Args:
        keyword: Search term (e.g., "fintech", "saas")
        count: Max URLs to return
        
    Returns:
        List of website URLs (not producthunt.com links)
    """
    encoded_keyword = keyword.replace(" ", "+")
    url = f"https://www.producthunt.com/search?q={encoded_keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            
            urls = extract_producthunt_urls(response.text)
            return urls[:count]
        except httpx.TimeoutException:
            print(f"Product Hunt search timeout")
            return []
        except httpx.HTTPStatusError as e:
            print(f"Product Hunt HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"Product Hunt search error: {e}")
            return []


def extract_producthunt_urls(html: str) -> List[str]:
    """Extract external website URLs from Product Hunt HTML."""
    urls = []
    
    # Product Hunt links to actual product websites
    # Look for external links that aren't producthunt.com
    patterns = [
        r'href="(https?://(?!(?:www\.)?producthunt\.com)[^"]+)"',
        r'data-href="(https?://[^"]+)"',
        r'"website":\s*"(https?://[^"]+)"',
        r'"url":\s*"(https?://(?!(?:www\.)?producthunt\.com)[^"]+)"',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            if is_valid_product_url(match):
                if match not in urls:
                    urls.append(match)
    
    return urls


def is_valid_product_url(url: str) -> bool:
    """Check if URL is likely a real product website."""
    excluded = [
        'producthunt.com',
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
        'gravatar.com',
        'cloudflare',
        'stripe.com',
        'intercom.io',
        'crisp.chat',
        'hotjar.com',
    ]
    
    url_lower = url.lower()
    for exc in excluded:
        if exc in url_lower:
            return False
    
    return url.startswith('http')
