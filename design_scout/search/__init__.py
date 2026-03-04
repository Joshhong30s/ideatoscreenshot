"""Search module - multi-source design search

Sources:
- Google Search
- Awwwards
- Dribbble
- SiteInspire
"""

from .aggregator import search, search_async, TARGET_URLS
from .google import search_google
from .awwwards import search_awwwards
from .dribbble import search_dribbble
from .siteinspire import search_siteinspire

__all__ = [
    'search',
    'search_async',
    'TARGET_URLS',
    'search_google',
    'search_awwwards', 
    'search_dribbble',
    'search_siteinspire',
]
