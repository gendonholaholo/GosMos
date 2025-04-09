#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from commands import (
    scrape,
    analyze,
    ai_toolbox,
    live_monitor,
    export,
    config
)

app = typer.Typer(
    name="mosscli",
    help="GosMos CLI - TikTok Shop Data Analysis Tool",
    add_completion=False,
)

# Add subcommands
app.add_typer(scrape.app, name="scrape", help="Scrape data from TikTok Shop")
app.add_typer(analyze.app, name="analyze", help="Analyze scraped data")
app.add_typer(ai_toolbox.app, name="ai-toolbox", help="AI-powered content generation")
app.add_typer(live_monitor.app, name="live-monitor", help="Monitor TikTok Shop live streams")
app.add_typer(export.app, name="export", help="Export data to various formats")
app.add_typer(config.app, name="config", help="Manage configuration")

console = Console()

def version_callback(value: bool):
    if value:
        console.print("[bold green]gosmoscli v1.0.0[/bold green]")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    GosMos CLI - A powerful tool for TikTok Shop data analysis and content generation.
    """
    pass

if __name__ == "__main__":
    app() 