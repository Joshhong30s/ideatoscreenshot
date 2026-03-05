"""DuckDuckGo search - no API key needed"""

import httpx
from typing import List
import re
from urllib.parse import unquote


async def search_duckduckgo(keyword: str, count: int = 15) -> List[str]:
    """Search DuckDuckGo for design-related websites.
    
    Uses DuckDuckGo HTML search (no API key required).
    
    Args:
        keyword: Search term (e.g., "fintech dashboard")
        count: Max URLs to return
        
    Returns:
        List of website URLs
    """
    # Add design-related terms to improve results
    search_query = f"{keyword} landing page design website"
    encoded_query = search_query.replace(" ", "+")
    
    # DuckDuckGo HTML endpoint
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            
            urls = extract_duckduckgo_urls(response.text)
            return urls[:count]
        except httpx.TimeoutException:
            print(f"DuckDuckGo search timeout")
            return []
        except httpx.HTTPStatusError as e:
            print(f"DuckDuckGo HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []


def extract_duckduckgo_urls(html: str) -> List[str]:
    """Extract URLs from DuckDuckGo HTML results."""
    urls = []
    
    # DuckDuckGo HTML results have URLs in result links
    # Pattern: class="result__a" href="..."
    # The href is often a redirect URL containing the actual URL
    
    # Find result links
    result_pattern = r'class="result__a"[^>]*href="([^"]+)"'
    matches = re.findall(result_pattern, html)
    
    for match in matches:
        # Extract actual URL from DuckDuckGo redirect
        actual_url = extract_actual_url(match)
        if actual_url and is_valid_design_url(actual_url):
            if actual_url not in urls:
                urls.append(actual_url)
    
    # Also try direct href patterns
    direct_pattern = r'href="(https?://(?!duckduckgo\.com)[^"]+)"'
    direct_matches = re.findall(direct_pattern, html)
    
    for match in direct_matches:
        if is_valid_design_url(match):
            if match not in urls:
                urls.append(match)
    
    return urls


def extract_actual_url(ddg_url: str) -> str:
    """Extract actual URL from DuckDuckGo redirect URL."""
    # DuckDuckGo sometimes wraps URLs
    # Pattern: //duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com
    
    if 'uddg=' in ddg_url:
        # Extract the encoded URL
        match = re.search(r'uddg=([^&]+)', ddg_url)
        if match:
            return unquote(match.group(1))
    
    # If it's already a direct URL
    if ddg_url.startswith('http'):
        return ddg_url
    
    return ""


def is_valid_design_url(url: str) -> bool:
    """Check if URL is likely a design website."""
    excluded = [
        'duckduckgo.com',
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
        'amazon.com',
        'wikipedia.org',
        'reddit.com',
        'medium.com',
        'cdn.',
        'assets.',
        '.js',
        '.css',
        '.png',
        '.jpg',
        '.gif',
        '.svg',
        '.pdf',
    ]
    
    url_lower = url.lower()
    for exc in excluded:
        if exc in url_lower:
            return False
    
    return url.startswith('http')
