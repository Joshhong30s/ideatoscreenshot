"""Dribbble search using Playwright"""

from typing import List
from urllib.parse import urlparse

from ..screenshot.browser import BrowserManager


async def search_dribbble(keyword: str, count: int = 15) -> List[str]:
    """Search Dribbble using Playwright browser.
    
    Dribbble shows design shots - we extract external website links.
    """
    encoded_keyword = keyword.replace(" ", "+")
    url = f"https://dribbble.com/search/{encoded_keyword}"
    
    context = None
    page = None
    
    try:
        context = await BrowserManager.new_context({'width': 1280, 'height': 900})
        page = await context.new_page()
        
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for shots to load
        await page.wait_for_selector('.shot-thumbnail', timeout=5000)
        
        # Get all external links from shot cards
        links = await page.eval_on_selector_all(
            'a[href^="http"]',
            '''elements => elements
                .map(el => el.href)
                .filter(href => 
                    href &&
                    !href.includes('dribbble.com') &&
                    !href.includes('facebook.com') &&
                    !href.includes('twitter.com') &&
                    !href.includes('x.com') &&
                    !href.includes('google.com') &&
                    !href.includes('cdn.') &&
                    !href.endsWith('.png') &&
                    !href.endsWith('.jpg')
                )'''
        )
        
        # Dedupe by domain
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
        print(f"Dribbble search error: {e}")
        return []
        
    finally:
        if page:
            await page.close()
        if context:
            await context.close()
