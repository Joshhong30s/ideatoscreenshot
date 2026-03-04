"""Web search - disabled (search engines block headless browsers)

Awwwards + Dribbble provide enough URLs (20+) for the pipeline.
This module is kept as a placeholder for future improvements.
"""

from typing import List


async def search_google(keyword: str, count: int = 15) -> List[str]:
    """Placeholder - search engines block headless browsers.
    
    Future options:
    - SerpAPI (paid)
    - Browserless.io
    - Residential proxies
    
    For now, rely on Awwwards + Dribbble which work reliably.
    """
    # Return empty - let other sources provide URLs
    return []
