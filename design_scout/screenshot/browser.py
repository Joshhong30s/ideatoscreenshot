"""Browser management for Playwright"""

from playwright.async_api import async_playwright, Browser, BrowserContext
from typing import Optional


class BrowserManager:
    """Manages Playwright browser instance."""
    
    _browser: Optional[Browser] = None
    _playwright = None
    
    @classmethod
    async def get_browser(cls) -> Browser:
        """Get or create browser instance."""
        if cls._browser is None:
            cls._playwright = await async_playwright().start()
            cls._browser = await cls._playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
        return cls._browser
    
    @classmethod
    async def close(cls) -> None:
        """Close browser and cleanup."""
        if cls._browser:
            await cls._browser.close()
            cls._browser = None
        if cls._playwright:
            await cls._playwright.stop()
            cls._playwright = None
    
    @classmethod
    async def new_context(cls, viewport: dict) -> BrowserContext:
        """Create a new browser context with specified viewport."""
        browser = await cls.get_browser()
        context = await browser.new_context(
            viewport=viewport,
            device_scale_factor=2,  # Retina
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        return context
