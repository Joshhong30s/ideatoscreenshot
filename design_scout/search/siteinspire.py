"""SiteInspire search using Playwright"""

from typing import List
from urllib.parse import urlparse

from ..screenshot.browser import BrowserManager


async def search_siteinspire(keyword: str, count: int = 15) -> List[str]:
    """Search SiteInspire using Playwright browser.
    
    SiteInspire is a curated showcase of the finest web design.
    """
    encoded_keyword = keyword.replace(" ", "+")
    url = f"https://www.siteinspire.com/websites?search={encoded_keyword}"
    
    context = None
    page = None
    
    try:
        context = await BrowserManager.new_context({'width': 1280, 'height': 900})
        page = await context.new_page()
        
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for page to load
        import asyncio
        await asyncio.sleep(2)
        
        # Get external website links
        links = await page.eval_on_selector_all(
            'a.website-link[href^="http"], a[data-url^="http"]',
            '''elements => elements
                .map(el => el.href || el.dataset.url)
                .filter(href => 
                    href &&
                    !href.includes('siteinspire.com')
                )'''
        )
        
        # If no links found with specific selectors, try broader search
        if not links:
            links = await page.eval_on_selector_all(
                '.website a[href^="http"]',
                '''elements => elements
                    .map(el => el.href)
                    .filter(href => 
                        href &&
                        !href.includes('siteinspire.com') &&
                        !href.includes('facebook.com') &&
                        !href.includes('twitter.com')
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
        print(f"SiteInspire search error: {e}")
        return []
        
    finally:
        if page:
            await page.close()
        if context:
            await context.close()
