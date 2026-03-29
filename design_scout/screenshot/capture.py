"""Screenshot capture — parallel batch capture with retry."""

import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from urllib.parse import urlparse

from .browser import BrowserManager


# Viewport configurations
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}

MAX_RETRIES = 2


async def capture(url: str, output_dir: str, timeout: int = 30) -> Optional[Dict[str, str]]:
    """Capture desktop + mobile screenshots for *url*.

    Returns ``{"desktop": path, "mobile": path}`` or ``None`` on failure.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    filename_base = url_to_filename(url)

    results: Dict[str, str] = {}
    for device, viewport in VIEWPORTS.items():
        path = output_path / f"{filename_base}_{device}.png"
        screenshot = await _capture_single(url, viewport, path, timeout)
        if screenshot:
            results[device] = str(screenshot)

    return results or None


async def _capture_single(
    url: str,
    viewport: dict,
    output_path: Path,
    timeout: int = 30,
) -> Optional[Path]:
    """Capture one screenshot with retry logic."""
    for attempt in range(1, MAX_RETRIES + 1):
        context = None
        page = None
        try:
            context = await BrowserManager.new_context(viewport)
            page = await context.new_page()

            # domcontentloaded is faster & more reliable than networkidle
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)

            # Small pause for late-rendering elements / fonts
            await asyncio.sleep(1)

            await page.screenshot(path=str(output_path), full_page=False, type="png")
            return output_path

        except Exception as e:
            if attempt < MAX_RETRIES:
                await asyncio.sleep(1)  # brief pause before retry
            else:
                print(f"Screenshot failed for {url} after {MAX_RETRIES} attempts: {e}")
                return None
        finally:
            if page:
                await page.close()
            if context:
                await context.close()

    return None  # unreachable, but keeps type checkers happy


async def capture_batch(
    urls: List[str],
    output_dir: str,
    concurrency: int = 5,
    timeout: int = 30,
) -> Dict[str, Optional[Dict[str, str]]]:
    """Capture screenshots for many URLs in parallel.

    Uses a semaphore to limit concurrency so we don't overwhelm the browser.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def _limited(url: str) -> tuple:
        async with semaphore:
            result = await capture(url, output_dir, timeout)
            return (url, result)

    tasks = [_limited(u) for u in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output: Dict[str, Optional[Dict[str, str]]] = {}
    for r in results:
        if isinstance(r, tuple):
            url, shots = r
            output[url] = shots
        # exceptions are silently skipped (already printed inside capture)

    await BrowserManager.close()
    return output


def url_to_filename(url: str) -> str:
    """Convert URL to a filesystem-safe filename."""
    parsed = urlparse(url)
    name = parsed.netloc + parsed.path
    for ch in ["/", "\\", ":", "*", "?", '"', "<", ">", "|", "."]:
        name = name.replace(ch, "_")
    return name.strip("_")[:100]
