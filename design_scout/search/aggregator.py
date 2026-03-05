"""Search aggregator - combines multiple sources to get 30-40 URLs

Sources (updated 2026-03-05):
- DuckDuckGo (general web search)
- Awwwards (award-winning sites)
- SiteInspire (curated designs)
- Lapa.ninja (landing pages)
- Landingfolio (landing pages)
- OnePageLove (one-page sites)

Removed: Dribbble, Behance (mockups, not real sites)
"""

import asyncio
from typing import List
from urllib.parse import urlparse

from .duckduckgo import search_duckduckgo
from .awwwards import search_awwwards
from .siteinspire import search_siteinspire
from .lapa import search_lapa
from .landingfolio import search_landingfolio
from .onepagelove import search_onepagelove


# Target: 30-40 unique URLs from all sources
TARGET_URLS = 40
URLS_PER_SOURCE = 10  # Request 10 from each source to get ~40 after dedup


def search(keyword: str, count: int = TARGET_URLS) -> List[str]:
    """Synchronous wrapper for async search (for non-async callers).
    
    Combines results from multiple sources, deduplicates, and normalizes URLs.
    Returns 30-40 unique URLs for comprehensive coverage.
    """
    return asyncio.run(search_async(keyword, count))


async def search_async(keyword: str, count: int = TARGET_URLS) -> List[str]:
    """Search multiple sources for design inspiration.
    
    Sources:
    - DuckDuckGo (~10 URLs)
    - Awwwards (~10 URLs)
    - SiteInspire (~10 URLs)
    - Lapa.ninja (~10 URLs)
    - Landingfolio (~10 URLs)
    - OnePageLove (~10 URLs)
    
    After deduplication, returns 30-40 unique URLs.
    
    Args:
        keyword: Search term (e.g., "fintech dashboard")
        count: Target number of URLs (default: 40)
        
    Returns:
        List of unique, normalized URLs (30-40)
    """
    print(f"   Searching DuckDuckGo...")
    ddg_results = await search_duckduckgo(keyword, URLS_PER_SOURCE)
    print(f"   → DuckDuckGo: {len(ddg_results)} URLs")
    
    print(f"   Searching Awwwards...")
    awwwards_results = await search_awwwards(keyword, URLS_PER_SOURCE)
    print(f"   → Awwwards: {len(awwwards_results)} URLs")
    
    print(f"   Searching SiteInspire...")
    siteinspire_results = await search_siteinspire(keyword, URLS_PER_SOURCE)
    print(f"   → SiteInspire: {len(siteinspire_results)} URLs")
    
    print(f"   Searching Lapa.ninja...")
    lapa_results = await search_lapa(keyword, URLS_PER_SOURCE)
    print(f"   → Lapa.ninja: {len(lapa_results)} URLs")
    
    print(f"   Searching Landingfolio...")
    landingfolio_results = await search_landingfolio(keyword, URLS_PER_SOURCE)
    print(f"   → Landingfolio: {len(landingfolio_results)} URLs")
    
    print(f"   Searching OnePageLove...")
    onepagelove_results = await search_onepagelove(keyword, URLS_PER_SOURCE)
    print(f"   → OnePageLove: {len(onepagelove_results)} URLs")
    
    # Combine all results
    all_urls = []
    all_urls.extend(ddg_results)
    all_urls.extend(awwwards_results)
    all_urls.extend(siteinspire_results)
    all_urls.extend(lapa_results)
    all_urls.extend(landingfolio_results)
    all_urls.extend(onepagelove_results)
    
    print(f"   Total before dedup: {len(all_urls)}")
    
    # Normalize and deduplicate
    unique_urls = deduplicate_urls(all_urls)
    
    print(f"   After dedup: {len(unique_urls)} unique URLs")
    
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
