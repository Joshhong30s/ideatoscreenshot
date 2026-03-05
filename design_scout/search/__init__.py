"""Search module - multi-source design search

Sources (updated 2026-03-05):
- DuckDuckGo (general web search)
- Awwwards (award-winning sites)
- SiteInspire (curated designs)
- Lapa.ninja (landing pages)
- Landingfolio (landing pages)
- OnePageLove (one-page sites)
"""

from .aggregator import search, search_async, TARGET_URLS
from .duckduckgo import search_duckduckgo
from .awwwards import search_awwwards
from .siteinspire import search_siteinspire
from .lapa import search_lapa
from .landingfolio import search_landingfolio
from .onepagelove import search_onepagelove

__all__ = [
    'search',
    'search_async',
    'TARGET_URLS',
    'search_duckduckgo',
    'search_awwwards', 
    'search_siteinspire',
    'search_lapa',
    'search_landingfolio',
    'search_onepagelove',
]
