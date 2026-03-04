"""Google search integration"""

import httpx
from urllib.parse import quote_plus, urlparse, parse_qs
import re
from typing import List


async def search_google(keyword: str, count: int = 10) -> List[str]:
    """Search Google for design-related URLs.
    
    Uses Google search with design-focused query modifications.
    """
    # Add design-related terms to improve results
    query = f"{keyword} site design inspiration"
    encoded_query = quote_plus(query)
    
    url = f"https://www.google.com/search?q={encoded_query}&num={count * 2}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            
            # Extract URLs from search results
            urls = extract_urls_from_html(response.text)
            return urls[:count]
        except Exception as e:
            print(f"Google search error: {e}")
            return []


def extract_urls_from_html(html: str) -> List[str]:
    """Extract URLs from Google search results HTML."""
    urls = []
    
    # Pattern to find URLs in Google search results
    # Google wraps URLs in /url?q= format
    url_pattern = r'/url\?q=([^&]+)&'
    matches = re.findall(url_pattern, html)
    
    for match in matches:
        try:
            # Decode URL
            from urllib.parse import unquote
            decoded_url = unquote(match)
            
            # Filter out Google's own URLs and common non-design sites
            if should_include_url(decoded_url):
                urls.append(decoded_url)
        except Exception:
            continue
    
    return urls


def should_include_url(url: str) -> bool:
    """Filter out unwanted URLs."""
    excluded_domains = [
        'google.com',
        'youtube.com',
        'facebook.com',
        'twitter.com',
        'instagram.com',
        'linkedin.com',
        'pinterest.com',  # Could be useful but often low-quality
        'reddit.com',
        'wikipedia.org',
    ]
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Must be http/https
        if parsed.scheme not in ('http', 'https'):
            return False
        
        # Check against excluded domains
        for excluded in excluded_domains:
            if excluded in domain:
                return False
        
        return True
    except Exception:
        return False
