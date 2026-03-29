"""Design Scout CLI — fully automated design inspiration collector.

Flow:
1. Search 4 sources in parallel  (or read a URL list file)
2. Deduplicate & health-check
3. Screenshot all URLs (desktop + mobile) — skip cached
4. AI-score all screenshots in parallel  — skip cached
5. Rank & output HTML + JSON report
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

import click

from design_scout import __version__
from design_scout.cache import Cache
from design_scout.search.aggregator import search_async, TARGET_URLS
from design_scout.screenshot.capture import capture_batch
from design_scout.screenshot.browser import BrowserManager
from design_scout.scoring.evaluator import evaluate
from design_scout.report.generator import generate_html, generate_json, format_result


def _echo(msg: str, **kw) -> None:
    click.echo(click.style(msg, **kw))


@click.command()
@click.argument("keyword", required=False, default=None)
@click.option("--urls", "-u", type=click.Path(exists=True), help="Text file with one URL per line (skips search)")
@click.option("--count", "-c", default=5, help="Number of TOP results to return (default: 5)")
@click.option("--output", "-o", default="./output", help="Output directory (default: ./output)")
@click.option("--no-score", is_flag=True, help="Skip AI scoring (faster, no API needed)")
@click.option("--no-cache", is_flag=True, help="Ignore cache, re-process everything")
@click.option("--search-count", "-s", default=TARGET_URLS, help=f"Target search URLs (default: {TARGET_URLS})")
@click.version_option(version=__version__, prog_name="design-scout")
def main(
    keyword: Optional[str],
    urls: Optional[str],
    count: int,
    output: str,
    no_score: bool,
    no_cache: bool,
    search_count: int,
) -> None:
    """Search for design inspiration based on KEYWORD.

    Two input modes:

      design-scout "fintech dashboard"          # auto-search

      design-scout --urls sites.txt             # provide URL list
    """
    if not keyword and not urls:
        click.echo("Error: provide a KEYWORD or --urls file.")
        raise SystemExit(1)

    _echo(f"\n🎨 Design Scout v{__version__}", fg="cyan", bold=True)
    if keyword:
        _echo(f'   Keyword: "{keyword}"', fg="white")
    if urls:
        _echo(f"   URL list: {urls}", fg="white")
    _echo(f"   Top {count} results → {output}\n", fg="white")

    try:
        asyncio.run(run_scout(
            keyword=keyword,
            urls_file=urls,
            top_n=count,
            output=output,
            no_score=no_score,
            no_cache=no_cache,
            search_count=search_count,
        ))
    except KeyboardInterrupt:
        click.echo("\n⛔ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        _echo(f"\n❌ Error: {e}", fg="red")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

async def run_scout(
    *,
    keyword: Optional[str],
    urls_file: Optional[str],
    top_n: int,
    output: str,
    no_score: bool,
    no_cache: bool,
    search_count: int,
) -> None:
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    cache = Cache(str(output_path)) if not no_cache else None

    # ── Step 1: Collect URLs ──────────────────────────────────────────
    if urls_file:
        _echo("Step 1: 讀取 URL 清單", fg="white")
        url_list = _read_url_file(urls_file)
        _echo(f"   ✓ {len(url_list)} URLs from file", fg="green")
    else:
        _echo(f"Step 1: 並行搜尋（目標 {search_count} URLs）", fg="white")
        url_list, report = await search_async(keyword, search_count)
        click.echo(report.summary())
        if report.all_failed:
            _echo("   ✗ 所有搜尋來源都失敗，請檢查網路連線。", fg="red")
            return
        _echo(f"   ✓ 取得 {len(url_list)} unique URLs", fg="green")

    if not url_list:
        _echo("沒有找到 URL，請換個關鍵字試試。", fg="yellow")
        return

    # ── Step 2: Screenshot (with cache) ───────────────────────────────
    screenshots_dir = output_path / "screenshots"
    urls_to_capture: List[str] = []
    cached_shots: Dict[str, Dict[str, str]] = {}

    for url in url_list:
        cached = cache.get_screenshots(url) if cache else None
        if cached:
            cached_shots[url] = cached
        else:
            urls_to_capture.append(url)

    total = len(url_list)
    from_cache = len(cached_shots)
    to_capture = len(urls_to_capture)

    _echo(f"Step 2: 截圖（{total} URLs — {from_cache} cached, {to_capture} new）", fg="white")

    new_shots: Dict[str, Optional[Dict[str, str]]] = {}
    if urls_to_capture:
        new_shots = await capture_batch(urls_to_capture, str(screenshots_dir), concurrency=5, timeout=30)
        # Update cache
        for url, shots in new_shots.items():
            if shots and cache:
                cache.set_screenshots(url, shots)

    # Merge
    all_shots: Dict[str, Dict[str, str]] = {**cached_shots}
    for url, shots in new_shots.items():
        if shots:
            all_shots[url] = shots

    success = len(all_shots)
    failed = total - success
    _echo(f"   ✓ 截圖成功 {success}/{total}", fg="green")
    if failed:
        _echo(f"   ⚠ {failed} 個失敗（timeout / 載入錯誤）", fg="yellow")

    if not all_shots:
        _echo("沒有截圖成功。請檢查網路連線。", fg="yellow")
        return

    # ── Step 3: AI Scoring (parallel, with cache) ─────────────────────
    results: List[Dict[str, Any]] = []

    if no_score:
        _echo("Step 3: 跳過 AI 評分（--no-score）", fg="white")
        for url, shots in all_shots.items():
            results.append(format_result(url, shots, None))
    else:
        _echo(f"Step 3: 並行 AI 評分（{len(all_shots)} 組截圖）", fg="white")

        async def _score_one(url: str, shots: Dict[str, str]) -> Dict[str, Any]:
            # Check cache first
            if cache:
                cached_score = cache.get_score(url)
                if cached_score:
                    return format_result(url, shots, cached_score)

            evaluation = None
            desktop = shots.get("desktop")
            if desktop:
                evaluation = await evaluate(desktop)
                if evaluation and cache:
                    cache.set_score(url, evaluation)
            return format_result(url, shots, evaluation)

        tasks = [_score_one(url, shots) for url, shots in all_shots.items()]
        results = await asyncio.gather(*tasks)

        scored = sum(1 for r in results if r.get("score", 0) > 0)
        _echo(f"   ✓ {scored}/{len(results)} 有評分", fg="green")

    # Save cache
    if cache:
        cache.save()

    # ── Step 4: Rank ──────────────────────────────────────────────────
    _echo(f"Step 4: 排序取 Top {top_n}", fg="white")
    sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    top_results = sorted_results[:top_n]

    if top_results and top_results[0].get("score"):
        lo = top_results[-1]["score"]
        hi = top_results[0]["score"]
        click.echo(f"   分數範圍: {lo}–{hi}")

    # ── Step 5: Report ────────────────────────────────────────────────
    _echo("Step 5: 生成報告", fg="white")
    display_keyword = keyword or "URL list"
    html_path = generate_html(top_results, str(output_path), display_keyword)
    json_path = generate_json(sorted_results, str(output_path), display_keyword)

    click.echo(f"   HTML（Top {top_n}）: {html_path}")
    click.echo(f"   JSON（全部 {len(sorted_results)}）: {json_path}")

    # ── Summary ───────────────────────────────────────────────────────
    _echo(f"\n✅ 完成！", fg="green", bold=True)
    click.echo(f"   URLs:  {total}")
    click.echo(f"   截圖:  {success}")
    click.echo(f"   評分:  {len(results)}")
    click.echo(f"   輸出:  Top {top_n}")
    click.echo(f"\n   👉 open {html_path}\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_url_file(path: str) -> List[str]:
    """Read a text file with one URL per line."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and line.strip().startswith("http")]


if __name__ == "__main__":
    main()
