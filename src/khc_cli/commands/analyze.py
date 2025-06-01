"""Commands for analyzing GitHub repositories and Awesome lists."""

import typer
import logging
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from pathlib import Path
from dotenv import load_dotenv
from typing_extensions import Annotated
from urllib.parse import urlparse

from khc_cli.github_client import GitHubClient
from khc_cli.utils.helpers import crawl_github_dependents
from khc_cli.utils.template_loader import get_awesome_list_template

app = typer.Typer()
console = Console()
LOGGER = logging.getLogger(__name__)
# Load environment variables from .env file
load_dotenv()

@app.command()
def repo(
    repo_name: Annotated[str, typer.Argument(help="Repository name (e.g., owner/repo)")],
    output_format: Annotated[str, typer.Option("--format", "-f", help="Output format: table, json")] = "table",
    github_api_key: Annotated[str, typer.Option(envvar="GITHUB_API_KEY", help="GitHub API Key")] = None,
):
    """Analyze a specific GitHub repository."""
    
    with Progress() as progress:
        task = progress.add_task("Analyzing repository...", total=100)
        
        github_client = GitHubClient(github_api_key)
        
        try:
            repo = github_client.client.get_repo(repo_name)
            
            if not repo:
                console.print(f"[red]Repository {repo_name} not found[/red]")
                raise typer.Exit(1)
            
            progress.update(task, advance=50)
        
            # Collect information
            info = {
                "name": repo.name,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "description": repo.description,
                "last_update": repo.updated_at.isoformat() if repo.updated_at else None,
                "dependents": len(crawl_github_dependents(repo_name, 5))
            }
            
            progress.update(task, advance=50)
        except Exception as e:
            console.print(f"[red]Error analyzing repository {repo_name}: {e}[/red]")
            raise typer.Exit(1)
            
        if output_format == "json":
            import json
            console.print_json(json.dumps(info))
        else:
            table = Table(title=f"Analysis of {repo_name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in info.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)

@app.command()
def etl(
    awesome_repo_url: Annotated[str, typer.Option(help="URL of the Awesome list")] = "https://api.github.com/repos/Krypto-Hashers-Community/khc-cli/contents/README.md",
    output_dir: Annotated[Path, typer.Option(help="Output directory")] = Path("./csv"),
    github_api_key: Annotated[str, typer.Option(envvar="GITHUB_API_KEY", help="GitHub API Key")] = None,
    use_template: Annotated[bool, typer.Option(help="Use Awesome List template for analyze command")]= True,
):
    """Run the ETL pipeline for an Awesome list."""
    from khc_cli.commands.etl import run_etl_pipeline
    
    # Extract only owner/repo if a full URL is provided
    if "github.com" in awesome_repo_url:
        awesome_repo_path = urlparse(awesome_repo_url).path.strip("/")
    else:
        awesome_repo_path = awesome_repo_url # Already in owner/repo format
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    projects_csv_path = output_dir / "projects.csv"
    orgs_csv_path = output_dir / "github_organizations.csv"
    
    console.print(f"[green]Starting ETL pipeline for {awesome_repo_url}[/green]")
    console.print(f"[green]Output to {projects_csv_path} and {orgs_csv_path}[/green]")
    
    # Retrieve the Awesome List template if needed
    template_content = None
    if use_template:
        try:
            template_content = get_awesome_list_template()
            (output_dir / ".awesome-cache.md").write_text(template_content, encoding="utf-8")
            console.print(f"[green]Awesome List template retrieved and stored in {output_dir / '.awesome-cache.md'}[/green]")
        except Exception as e:
            console.print(f"[red]Error retrieving Awesome List template: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[yellow]Awesome List template usage disabled[/yellow]")
    
    run_etl_pipeline(
        awesome_repo_url=awesome_repo_url,
        awesome_readme_filename="README.md",
        local_readme_path=output_dir / ".awesome-cache.md",
        projects_csv_path=projects_csv_path,
        orgs_csv_path=orgs_csv_path,
        github_api_key=github_api_key
    )