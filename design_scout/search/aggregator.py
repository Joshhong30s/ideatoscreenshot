"""Search aggregator - parallel multi-source search with health reporting.

Sources:
- DuckDuckGo  — General web search (httpx, reliable)
- Product Hunt — Trending products (Playwright)
- Landingfolio — Curated landing pages (Playwright)
- Lapa.ninja   — Landing page gallery (Playwright)
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Dict
from urllib.parse import urlparse

from .duckduckgo import search_duckduckgo
from .producthunt import search_producthunt
from .landingfolio import search_landingfolio
from .lapa import search_lapa


# Source quotas (how many URLs to request from each source)
DDG_COUNT = 25
PH_COUNT = 15
LF_COUNT = 10
LAPA_COUNT = 10

TARGET_URLS = DDG_COUNT + PH_COUNT + LF_COUNT + LAPA_COUNT


@dataclass
class SourceResult:
    name: str
    urls: List[str] = field(default_factory=list)
    error: str = ""
    ok: bool = True


@dataclass
class SearchReport:
    """Health report for a search run."""
    sources: List[SourceResult] = field(default_factory=list)
    total_before_dedup: int = 0
    total_after_dedup: int = 0

    @property
    def all_failed(self) -> bool:
        return all(not s.ok or len(s.urls) == 0 for s in self.sources)

    def summary(self) -> str:
        lines = []
        for s in self.sources:
            status = f"✓ {len(s.urls)} URLs" if s.ok and s.urls else f"✗ {s.error or '0 URLs'}"
            lines.append(f"   {s.name:15s} {status}")
        lines.append(f"   {'─' * 30}")
        lines.append(f"   Before dedup: {self.total_before_dedup}")
        lines.append(f"   After dedup:  {self.total_after_dedup}")
        return "\n".join(lines)


def search(keyword: str, count: int = TARGET_URLS) -> tuple[List[str], SearchReport]:
    """Synchronous wrapper."""
    return asyncio.run(search_async(keyword, count))


async def search_async(keyword: str, count: int = TARGET_URLS) -> tuple[List[str], SearchReport]:
    """Search all sources **in parallel**, deduplicate, and return URLs + health report."""

    async def _run(name: str, coro) -> SourceResult:
        try:
            urls = await coro
            return SourceResult(name=name, urls=urls)
        except Exception as e:
            return SourceResult(name=name, urls=[], error=str(e), ok=False)

    results = await asyncio.gather(
        _run("DuckDuckGo", search_duckduckgo(keyword, DDG_COUNT)),
        _run("Product Hunt", search_producthunt(keyword, PH_COUNT)),
        _run("Landingfolio", search_landingfolio(keyword, LF_COUNT)),
        _run("Lapa.ninja", search_lapa(keyword, LAPA_COUNT)),
    )

    report = SearchReport(sources=list(results))

    # Combine
    all_urls: List[str] = []
    for r in results:
        all_urls.extend(r.urls)

    report.total_before_dedup = len(all_urls)

    # Deduplicate
    unique = deduplicate_urls(all_urls)
    report.total_after_dedup = len(unique)

    return unique[:count], report


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def deduplicate_urls(urls: List[str]) -> List[str]:
    """One URL per domain, normalized."""
    seen_domains: set[str] = set()
    unique: List[str] = []

    for url in urls:
        normalized = normalize_url(url)
        if not normalized:
            continue
        domain = get_domain(normalized)
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            unique.append(normalized)

    return unique


def normalize_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        scheme = "https"
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        path = parsed.path.rstrip("/")
        return f"{scheme}://{netloc}{path}"
    except Exception:
        return ""


def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""
