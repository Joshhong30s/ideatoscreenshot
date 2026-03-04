"""Design Scout CLI - 全自動設計靈感搜集工具"""

import asyncio
import sys
from pathlib import Path

import click

from design_scout import __version__
from design_scout.search.aggregator import search_async
from design_scout.screenshot.capture import capture_batch, BrowserManager
from design_scout.screenshot.browser import BrowserManager
from design_scout.scoring.evaluator import evaluate
from design_scout.report.generator import generate_html, generate_json, format_result


def print_progress(message: str, emoji: str = "🔄") -> None:
    """Print progress message."""
    click.echo(f"{emoji} {message}")


@click.command()
@click.argument("keyword")
@click.option("--count", "-c", default=5, help="Number of results to return (default: 5)")
@click.option("--output", "-o", default="./output", help="Output directory (default: ./output)")
@click.option("--no-score", is_flag=True, help="Skip AI scoring (faster, no API needed)")
@click.version_option(version=__version__, prog_name="design-scout")
def main(keyword: str, count: int, output: str, no_score: bool) -> None:
    """Search for design inspiration based on KEYWORD.
    
    Example: design-scout "fintech dashboard"
    """
    click.echo(click.style(f"\n🎨 Design Scout v{__version__}", fg="cyan", bold=True))
    click.echo(click.style(f'   Searching for: "{keyword}"\n', fg="white"))
    
    try:
        asyncio.run(run_scout(keyword, count, output, no_score))
    except KeyboardInterrupt:
        click.echo("\n⛔ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"))
        sys.exit(1)


async def run_scout(keyword: str, count: int, output: str, no_score: bool) -> None:
    """Run the design scout pipeline."""
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Search
    print_progress(f"Searching for '{keyword}'...", "🔍")
    urls = await search_async(keyword, count * 2)  # Get extra for failures
    
    if not urls:
        click.echo(click.style("No URLs found. Try different keywords.", fg="yellow"))
        return
    
    click.echo(f"   Found {len(urls)} candidate URLs")
    
    # Step 2: Screenshots
    print_progress("Capturing screenshots...", "📸")
    screenshots_dir = output_path / "screenshots"
    screenshots = await capture_batch(urls[:count + 2], str(screenshots_dir), concurrency=3)
    
    successful = {k: v for k, v in screenshots.items() if v is not None}
    click.echo(f"   Captured {len(successful)}/{len(screenshots)} screenshots")
    
    if not successful:
        click.echo(click.style("No screenshots captured. Check network connection.", fg="yellow"))
        return
    
    # Step 3: Scoring (optional)
    results = []
    
    if no_score:
        print_progress("Skipping AI scoring (--no-score)", "⏭️")
        for url, shots in list(successful.items())[:count]:
            results.append(format_result(url, shots, None))
    else:
        print_progress("Evaluating designs with AI...", "🤖")
        for url, shots in list(successful.items())[:count]:
            # Evaluate desktop screenshot
            if shots.get('desktop'):
                evaluation = await evaluate(shots['desktop'])
            else:
                evaluation = None
            
            results.append(format_result(url, shots, evaluation))
            score = evaluation.get('total_score', '?') if evaluation else '?'
            click.echo(f"   {url[:50]}... → {score}/100")
    
    # Step 4: Generate reports
    print_progress("Generating reports...", "📝")
    
    html_path = generate_html(results, str(output_path), keyword)
    json_path = generate_json(results, str(output_path), keyword)
    
    click.echo(f"   HTML: {html_path}")
    click.echo(f"   JSON: {json_path}")
    
    # Summary
    click.echo(click.style(f"\n✅ Done! {len(results)} designs found", fg="green", bold=True))
    click.echo(f"   Open {html_path} to view results\n")


if __name__ == "__main__":
    main()
