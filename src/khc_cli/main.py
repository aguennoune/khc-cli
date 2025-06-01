"""Main entrypoint to the KHC CLI."""

import typer
from rich.console import Console
from rich.table import Table
import logging
from typing_extensions import Annotated

from khc_cli.github_client import GitHubClient
from khc_cli.commands import analyze, curate
from khc_cli.version import __version__
from khc_cli.utils.template_loader import get_awesome_list_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

# Application Typer instance
app = typer.Typer(
    name="khc-cli",
    help="CLI tool for curating and analyzing Awesome lists, focusing on Open Sustainable Technology.",
    rich_help_panel=True
)

# Rich console for enhanced displays
console = Console()

# Add subcommands to the main app
app.add_typer(analyze.app, name="analyze", help="Analyze awesome lists and repositories")
app.add_typer(curate.app, name="curate", help="Curate awesome lists")

@app.command()
def status(
    github_api_key: Annotated[str, typer.Option(envvar="GITHUB_API_KEY", help="GitHub API Key")] = None,
):
    """Check the status of the GitHub API."""
    try:
        github_client = GitHubClient(github_api_key)
        rate_limit = github_client.get_rate_limit()
        
        table = Table(title="GitHub API Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Remaining requests", str(rate_limit["remaining"]))
        table.add_row("Total limit", str(rate_limit["total"]))
        table.add_row("Reset at", str(rate_limit["reset_time"]))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show the version of khc-cli")
):
    """
    KHC CLI - Tool for analyzing and curating Awesome lists
    focused on sustainable and open source technologies.
    """
    if version:
        typer.echo(f"khc-cli version: {__version__}")
        raise typer.Exit()
    # If no version flag, invoke help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    

def run(prog_name="khc-cli"):
    """Entry point function to run the application."""
    app(prog_name=prog_name)

if __name__ == "__main__":
    run()