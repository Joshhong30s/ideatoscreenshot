"""Design Scout CLI"""

import click
from design_scout import __version__


@click.command()
@click.argument("keyword")
@click.option("--count", "-c", default=5, help="Number of results to return (default: 5)")
@click.option("--output", "-o", default="./output", help="Output directory (default: ./output)")
@click.version_option(version=__version__, prog_name="design-scout")
def main(keyword: str, count: int, output: str) -> None:
    """Search for design inspiration based on KEYWORD.
    
    Example: design-scout "fintech dashboard"
    """
    click.echo(f"Searching for: {keyword}")
    click.echo(f"Results: {count}")
    click.echo(f"Output: {output}")
    # TODO: Implement search, screenshot, scoring, and report


if __name__ == "__main__":
    main()
