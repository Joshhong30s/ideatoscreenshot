"""Design Scout CLI - 全自動設計靈感搜集工具

Flow (按照 spec):
1. 搜尋 30-40 個候選 URL（Google + Awwwards + Dribbble + SiteInspire）
2. 全部截圖（Desktop 1440px + Mobile 390px）
3. AI 評分全部截圖（Vision 0-100 + 評語）
4. 排序取 Top N
5. 輸出 HTML 報告 + JSON 資料
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

import click

from design_scout import __version__
from design_scout.search.aggregator import search_async, TARGET_URLS
from design_scout.screenshot.capture import capture_batch
from design_scout.screenshot.browser import BrowserManager
from design_scout.scoring.evaluator import evaluate
from design_scout.report.generator import generate_html, generate_json, format_result


def print_progress(message: str, emoji: str = "🔄") -> None:
    """Print progress message."""
    click.echo(f"{emoji} {message}")


@click.command()
@click.argument("keyword")
@click.option("--count", "-c", default=5, help="Number of TOP results to return (default: 5)")
@click.option("--output", "-o", default="./output", help="Output directory (default: ./output)")
@click.option("--no-score", is_flag=True, help="Skip AI scoring (faster, no API needed)")
@click.option("--search-count", "-s", default=40, help="Number of URLs to search (default: 40)")
@click.version_option(version=__version__, prog_name="design-scout")
def main(keyword: str, count: int, output: str, no_score: bool, search_count: int) -> None:
    """Search for design inspiration based on KEYWORD.
    
    Searches 30-40 URLs, screenshots ALL of them, scores ALL with AI,
    then returns the TOP N results sorted by score.
    
    Example: design-scout "fintech dashboard"
    """
    click.echo(click.style(f"\n🎨 Design Scout v{__version__}", fg="cyan", bold=True))
    click.echo(click.style(f'   Searching for: "{keyword}"', fg="white"))
    click.echo(click.style(f'   Will search {search_count} URLs, return Top {count}\n', fg="white"))
    
    try:
        asyncio.run(run_scout(keyword, count, output, no_score, search_count))
    except KeyboardInterrupt:
        click.echo("\n⛔ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"))
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def run_scout(keyword: str, top_n: int, output: str, no_score: bool, search_count: int) -> None:
    """Run the design scout pipeline.
    
    按照 spec 的完整流程：
    1. 搜尋 30-40 個 URL（4 個來源）
    2. 全部截圖
    3. 全部評分
    4. 排序取 Top N
    """
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # ============================================
    # Step 1: 搜尋候選 (30-40 URLs from 4 sources)
    # ============================================
    print_progress(f"Step 1: 搜尋候選 URL（目標 {search_count} 個）", "🔍")
    urls = await search_async(keyword, search_count)
    
    if not urls:
        click.echo(click.style("No URLs found. Try different keywords.", fg="yellow"))
        return
    
    click.echo(click.style(f"   ✓ 找到 {len(urls)} 個候選 URL", fg="green"))
    
    # ============================================
    # Step 2: 批量截圖 (ALL URLs, Desktop + Mobile)
    # ============================================
    print_progress(f"Step 2: 批量截圖（{len(urls)} 個 URL × 2 viewports）", "📸")
    screenshots_dir = output_path / "screenshots"
    
    # Screenshot ALL URLs, not just top_n
    screenshots = await capture_batch(urls, str(screenshots_dir), concurrency=5, timeout=30)
    
    successful = {k: v for k, v in screenshots.items() if v is not None}
    failed = len(screenshots) - len(successful)
    
    click.echo(click.style(f"   ✓ 成功截圖 {len(successful)}/{len(screenshots)} 個網站", fg="green"))
    if failed > 0:
        click.echo(click.style(f"   ⚠ {failed} 個網站截圖失敗（timeout 或載入錯誤）", fg="yellow"))
    
    if not successful:
        click.echo(click.style("No screenshots captured. Check network connection.", fg="yellow"))
        return
    
    # ============================================
    # Step 3: AI 評分 (ALL screenshots)
    # ============================================
    results: List[Dict[str, Any]] = []
    
    if no_score:
        print_progress("Step 3: 跳過 AI 評分（--no-score）", "⏭️")
        for url, shots in successful.items():
            results.append(format_result(url, shots, None))
    else:
        print_progress(f"Step 3: AI 評分（{len(successful)} 組截圖）", "🤖")
        
        scored_count = 0
        for url, shots in successful.items():
            # Evaluate desktop screenshot (primary)
            evaluation = None
            if shots.get('desktop'):
                evaluation = await evaluate(shots['desktop'])
            
            results.append(format_result(url, shots, evaluation))
            
            scored_count += 1
            score = evaluation.get('total_score', '?') if evaluation else '?'
            # Progress indicator
            if scored_count % 5 == 0 or scored_count == len(successful):
                click.echo(f"   評分進度: {scored_count}/{len(successful)}")
        
        click.echo(click.style(f"   ✓ 完成 {scored_count} 個網站評分", fg="green"))
    
    # ============================================
    # Step 4: 排序取 Top N
    # ============================================
    print_progress(f"Step 4: 排序取 Top {top_n}", "📊")
    
    # Sort by score descending
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    top_results = sorted_results[:top_n]
    
    click.echo(f"   Top {top_n} 分數範圍: {top_results[-1]['score']}-{top_results[0]['score']}" if top_results and top_results[0].get('score') else "   （無評分）")
    
    # ============================================
    # Step 5: 輸出報告 (HTML + JSON)
    # ============================================
    print_progress("Step 5: 生成報告", "📝")
    
    html_path = generate_html(top_results, str(output_path), keyword)
    json_path = generate_json(sorted_results, str(output_path), keyword)  # JSON 包含全部結果
    
    click.echo(f"   HTML 報告（Top {top_n}）: {html_path}")
    click.echo(f"   JSON 資料（全部 {len(sorted_results)}）: {json_path}")
    
    # ============================================
    # Summary
    # ============================================
    click.echo(click.style(f"\n✅ 完成！", fg="green", bold=True))
    click.echo(f"   搜尋: {len(urls)} URLs")
    click.echo(f"   截圖: {len(successful)} 成功")
    click.echo(f"   評分: {len(results)} 個")
    click.echo(f"   輸出: Top {top_n}")
    click.echo(f"\n   👉 open {html_path}\n")


if __name__ == "__main__":
    main()
