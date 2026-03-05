"""Search module - multi-source competitor landing page research

Sources (updated 2026-03-05):
- DuckDuckGo (25) - General web search
- Product Hunt (15) - Trending products
- Landingfolio (10) - Curated landing pages
- Lapa.ninja (10) - Landing page gallery
"""

from .aggregator import search, search_async, TARGET_URLS
from .duckduckgo import search_duckduckgo
from .producthunt import search_producthunt
from .landingfolio import search_landingfolio
from .lapa import search_lapa

__all__ = [
    'search',
    'search_async',
    'TARGET_URLS',
    'search_duckduckgo',
    'search_producthunt',
    'search_landingfolio',
    'search_lapa',
]
