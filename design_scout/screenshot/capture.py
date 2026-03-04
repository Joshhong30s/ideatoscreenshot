"""Screenshot capture functionality"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Optional, List
from urllib.parse import urlparse

from .browser import BrowserManager


# Viewport configurations
VIEWPORTS = {
    'desktop': {'width': 1440, 'height': 900},
    'mobile': {'width': 390, 'height': 844},
}


async def capture(url: str, output_dir: str, timeout: int = 30) -> Optional[Dict[str, str]]:
    """Capture screenshots of a URL in both desktop and mobile viewports.
    
    Args:
        url: URL to screenshot
        output_dir: Directory to save screenshots
        timeout: Page load timeout in seconds
        
    Returns:
        Dict with 'desktop' and 'mobile' screenshot paths, or None if failed
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from URL
    filename_base = url_to_filename(url)
    
    results = {}
    
    for device, viewport in VIEWPORTS.items():
        try:
            screenshot_path = await capture_single(
                url=url,
                viewport=viewport,
                output_path=output_path / f"{filename_base}_{device}.png",
                timeout=timeout
            )
            if screenshot_path:
                results[device] = str(screenshot_path)
        except Exception as e:
            print(f"Error capturing {device} screenshot for {url}: {e}")
    
    # Return None if no screenshots were captured
    if not results:
        return None
    
    return results


async def capture_single(
    url: str, 
    viewport: dict, 
    output_path: Path,
    timeout: int = 30
) -> Optional[Path]:
    """Capture a single screenshot.
    
    Args:
        url: URL to screenshot
        viewport: Viewport dimensions
        output_path: Path to save screenshot
        timeout: Timeout in seconds
        
    Returns:
        Path to screenshot or None if failed
    """
    context = None
    page = None
    
    try:
        context = await BrowserManager.new_context(viewport)
        page = await context.new_page()
        
        # Navigate with timeout
        await page.goto(url, wait_until='networkidle', timeout=timeout * 1000)
        
        # Wait a bit for any animations/lazy loading
        await asyncio.sleep(1)
        
        # Take screenshot
        await page.screenshot(
            path=str(output_path),
            full_page=False,  # Just viewport, not full page
            type='png'
        )
        
        return output_path
        
    except Exception as e:
        print(f"Screenshot failed for {url}: {e}")
        return None
        
    finally:
        if page:
            await page.close()
        if context:
            await context.close()


async def capture_batch(
    urls: List[str], 
    output_dir: str, 
    concurrency: int = 3,
    timeout: int = 30
) -> Dict[str, Optional[Dict[str, str]]]:
    """Capture screenshots for multiple URLs in parallel.
    
    Args:
        urls: List of URLs to screenshot
        output_dir: Directory to save screenshots
        concurrency: Max concurrent captures
        timeout: Page load timeout per URL
        
    Returns:
        Dict mapping URL to screenshot results
    """
    semaphore = asyncio.Semaphore(concurrency)
    
    async def capture_with_limit(url: str) -> tuple:
        async with semaphore:
            result = await capture(url, output_dir, timeout)
            return (url, result)
    
    tasks = [capture_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    output = {}
    for result in results:
        if isinstance(result, tuple):
            url, screenshots = result
            output[url] = screenshots
        # Ignore exceptions, just skip failed URLs
    
    # Cleanup browser after batch
    await BrowserManager.close()
    
    return output


def url_to_filename(url: str) -> str:
    """Convert URL to safe filename."""
    parsed = urlparse(url)
    
    # Use domain + path
    name = parsed.netloc + parsed.path
    
    # Remove/replace unsafe characters
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '.']:
        name = name.replace(char, '_')
    
    # Limit length
    if len(name) > 100:
        name = name[:100]
    
    return name.strip('_')
