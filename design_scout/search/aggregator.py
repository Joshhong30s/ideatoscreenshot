"""Search aggregator - combines multiple sources"""

import asyncio
from typing import List
from urllib.parse import urlparse

from .google import search_google
from .awwwards import search_awwwards


def search(keyword: str, count: int = 10) -> List[str]:
    """Synchronous wrapper for async search.
    
    Combines results from multiple sources, deduplicates, and normalizes URLs.
    """
    return asyncio.run(search_async(keyword, count))


async def search_async(keyword: str, count: int = 10) -> List[str]:
    """Search multiple sources for design inspiration.
    
    Args:
        keyword: Search term (e.g., "fintech dashboard")
        count: Number of results to return
        
    Returns:
        List of unique, normalized URLs
    """
    # Request more than needed to account for duplicates
    request_count = count * 2
    
    # Search all sources in parallel
    results = await asyncio.gather(
        search_google(keyword, request_count),
        search_awwwards(keyword, request_count),
        return_exceptions=True
    )
    
    all_urls = []
    for result in results:
        if isinstance(result, list):
            all_urls.extend(result)
        # Silently ignore exceptions from individual sources
    
    # Normalize and deduplicate
    unique_urls = deduplicate_urls(all_urls)
    
    return unique_urls[:count]


def deduplicate_urls(urls: List[str]) -> List[str]:
    """Remove duplicate URLs based on normalized domain.
    
    - Removes query parameters
    - Normalizes protocol (prefer https)
    - Keeps only one URL per domain
    """
    seen_domains = set()
    unique_urls = []
    
    for url in urls:
        normalized = normalize_url(url)
        if not normalized:
            continue
            
        domain = get_domain(normalized)
        if domain not in seen_domains:
            seen_domains.add(domain)
            unique_urls.append(normalized)
    
    return unique_urls


def normalize_url(url: str) -> str:
    """Normalize a URL for comparison."""
    try:
        parsed = urlparse(url)
        
        # Use https by default
        scheme = 'https'
        
        # Remove www. prefix for consistency
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        
        # Remove query params and fragments for deduplication
        # but keep the path
        path = parsed.path.rstrip('/')
        
        return f"{scheme}://{netloc}{path}"
    except Exception:
        return ""


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""
