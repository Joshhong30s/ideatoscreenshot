"""Web search using Playwright (DuckDuckGo - bot friendly)"""

import asyncio
from typing import List
from urllib.parse import urlparse, quote_plus

from ..screenshot.browser import BrowserManager


async def search_google(keyword: str, count: int = 15) -> List[str]:
    """Search using DuckDuckGo (more bot-friendly than Google).
    
    Uses Playwright browser for reliable results.
    """
    query = f"{keyword} site design inspiration"
    url = f"https://duckduckgo.com/?q={quote_plus(query)}&ia=web"
    
    context = None
    page = None
    
    try:
        context = await BrowserManager.new_context({'width': 1280, 'height': 900})
        page = await context.new_page()
        
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for results to render
        await asyncio.sleep(3)
        
        # Extract all result links
        links = await page.eval_on_selector_all(
            'a[data-testid="result-title-a"], article a[href^="http"]',
            '''elements => elements
                .map(el => el.href)
                .filter(href => 
                    href &&
                    href.startsWith('http') &&
                    !href.includes('duckduckgo.com') &&
                    !href.includes('google.com') &&
                    !href.includes('youtube.com') &&
                    !href.includes('facebook.com') &&
                    !href.includes('twitter.com') &&
                    !href.includes('instagram.com') &&
                    !href.includes('linkedin.com') &&
                    !href.includes('reddit.com') &&
                    !href.includes('wikipedia.org') &&
                    !href.includes('pinterest.com')
                )'''
        )
        
        # Dedupe by domain
        seen = set()
        unique_urls = []
        for link in links:
            try:
                domain = urlparse(link).netloc
                if domain and domain not in seen:
                    seen.add(domain)
                    unique_urls.append(link)
                    if len(unique_urls) >= count:
                        break
            except:
                continue
        
        return unique_urls
        
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return []
        
    finally:
        if page:
            await page.close()
        if context:
            await context.close()
