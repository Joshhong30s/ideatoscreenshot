"""Search aggregator - combines multiple sources for competitor landing page research

Sources (updated 2026-03-05):
- DuckDuckGo (25) - General web search, main source
- Product Hunt (15) - Trending products & startups
- Landingfolio (10) - Curated landing pages
- Lapa.ninja (10) - Landing page gallery

Focus: Real operating websites for competitive research
"""

import asyncio
from typing import List
from urllib.parse import urlparse

from .duckduckgo import search_duckduckgo
from .producthunt import search_producthunt
from .landingfolio import search_landingfolio
from .lapa import search_lapa


# Target: 40-60 unique URLs from all sources
TARGET_URLS = 50

# Source quotas
DDG_COUNT = 25
PH_COUNT = 15
LF_COUNT = 10
LAPA_COUNT = 10


def search(keyword: str, count: int = TARGET_URLS) -> List[str]:
    """Synchronous wrapper for async search (for non-async callers).
    
    Combines results from multiple sources, deduplicates, and normalizes URLs.
    Returns up to `count` unique URLs for competitive research.
    """
    return asyncio.run(search_async(keyword, count))


async def search_async(keyword: str, count: int = TARGET_URLS) -> List[str]:
    """Search multiple sources for competitor landing pages.
    
    Sources:
    - DuckDuckGo (~25 URLs) - Primary source
    - Product Hunt (~15 URLs) - Trending products
    - Landingfolio (~10 URLs) - Curated landing pages
    - Lapa.ninja (~10 URLs) - Landing page gallery
    
    After deduplication, returns 40-60 unique URLs.
    
    Args:
        keyword: Search term (e.g., "fintech dashboard")
        count: Target number of URLs (default: 50)
        
    Returns:
        List of unique, normalized URLs
    """
    print(f"   Searching DuckDuckGo...")
    ddg_results = await search_duckduckgo(keyword, DDG_COUNT)
    print(f"   → DuckDuckGo: {len(ddg_results)} URLs")
    
    print(f"   Searching Product Hunt...")
    ph_results = await search_producthunt(keyword, PH_COUNT)
    print(f"   → Product Hunt: {len(ph_results)} URLs")
    
    print(f"   Searching Landingfolio...")
    landingfolio_results = await search_landingfolio(keyword, LF_COUNT)
    print(f"   → Landingfolio: {len(landingfolio_results)} URLs")
    
    print(f"   Searching Lapa.ninja...")
    lapa_results = await search_lapa(keyword, LAPA_COUNT)
    print(f"   → Lapa.ninja: {len(lapa_results)} URLs")
    
    # Combine all results
    all_urls = []
    all_urls.extend(ddg_results)
    all_urls.extend(ph_results)
    all_urls.extend(landingfolio_results)
    all_urls.extend(lapa_results)
    
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
