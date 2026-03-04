"""Google search using Playwright (same browser as screenshots)"""

import asyncio
from typing import List
from urllib.parse import urlparse, quote_plus

from ..screenshot.browser import BrowserManager


async def search_google(keyword: str, count: int = 15) -> List[str]:
    """Search Google using Playwright browser.
    
    Uses the same Playwright instance as screenshots - no separate API needed.
    """
    query = f"{keyword} site design inspiration"
    url = f"https://www.google.com/search?q={quote_plus(query)}&num={count * 2}"
    
    context = None
    page = None
    
    try:
        context = await BrowserManager.new_context({'width': 1280, 'height': 900})
        page = await context.new_page()
        
        # Go to Google
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for results (Google changes selectors often)
        await asyncio.sleep(2)  # Simple wait instead of flaky selector
        
        # Extract all links from search results
        links = await page.eval_on_selector_all(
            'div#search a[href^="http"]',
            '''elements => elements.map(el => el.href).filter(href => 
                href && 
                !href.includes('google.com') &&
                !href.includes('youtube.com') &&
                !href.includes('facebook.com') &&
                !href.includes('twitter.com') &&
                !href.includes('instagram.com') &&
                !href.includes('linkedin.com') &&
                !href.includes('reddit.com') &&
                !href.includes('wikipedia.org')
            )'''
        )
        
        # Dedupe and limit
        seen = set()
        unique_urls = []
        for link in links:
            domain = urlparse(link).netloc
            if domain not in seen:
                seen.add(domain)
                unique_urls.append(link)
                if len(unique_urls) >= count:
                    break
        
        return unique_urls
        
    except Exception as e:
        print(f"Google search error: {e}")
        return []
        
    finally:
        if page:
            await page.close()
        if context:
            await context.close()
