"""Behance search using Playwright"""

import asyncio
from typing import List
from urllib.parse import urlparse, quote_plus

from ..screenshot.browser import BrowserManager


async def search_behance(keyword: str, count: int = 15) -> List[str]:
    """Search Behance for design projects.
    
    Note: Behance shows design mockups, not live websites.
    Still useful for design inspiration.
    """
    url = f"https://www.behance.net/search/projects?search={quote_plus(keyword)}"
    
    context = None
    page = None
    
    try:
        context = await BrowserManager.new_context({'width': 1280, 'height': 900})
        page = await context.new_page()
        
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(3)
        
        # Get Behance project links
        links = await page.eval_on_selector_all(
            'a[href*="/gallery/"]',
            '''elements => {
                const urls = elements.map(el => el.href);
                // Dedupe and clean tracking params
                const seen = new Set();
                return urls.filter(url => {
                    const clean = url.split('?')[0];
                    if (seen.has(clean)) return false;
                    seen.add(clean);
                    return true;
                });
            }'''
        )
        
        return links[:count]
        
    except Exception as e:
        print(f"Behance search error: {e}")
        return []
        
    finally:
        if page:
            await page.close()
        if context:
            await context.close()
