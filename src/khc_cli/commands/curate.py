"""Commands for curating Awesome lists."""

import typer
from rich.console import Console
from pathlib import Path
from typing_extensions import Annotated
from dotenv import load_dotenv

app = typer.Typer()
console = Console()
# Load environment variables from .env file
load_dotenv()

@app.command()
def validate(
    readme_path: Annotated[Path, typer.Argument(help="Path to the README.md file to validate")],
):
    """Validate the format of an Awesome list."""
    from khc_cli.awesomecure.awesome2py import AwesomeList
    
    if not readme_path.exists():
        console.print(f"[red]File {readme_path} does not exist[/red]")
        raise typer.Exit(1)
    
    try:
        awesome_list = AwesomeList(str(readme_path))
        rubrics_count = len(awesome_list.rubrics)
        entries_count = sum(len(rubric.entries) for rubric in awesome_list.rubrics)
        
        console.print(f"[green]Awesome list is valid![/green]")
        console.print(f"[green]Number of rubrics: {rubrics_count}[/green]")
        console.print(f"[green]Number of entries: {entries_count}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def add_project(
    repo_url: Annotated[str, typer.Argument(help="GitHub repository URL")],
    readme_path: Annotated[Path, typer.Option(help="Path to the README.md")] = Path("README.md"),
    section: Annotated[str, typer.Option(help="Section where to add the project")] = None,
    github_api_key: Annotated[str, typer.Option(envvar="GITHUB_API_KEY", help="GitHub API Key")] = None,
):
    """Add a project to an Awesome list."""
    from urllib.parse import urlparse
    from khc_cli.github_client import GitHubClient
    
    if not readme_path.exists():
        console.print(f"[red]File {readme_path} does not exist[/red]")
        raise typer.Exit(1)
    
    # Check that the URL is a GitHub URL
    parsed_url = urlparse(repo_url)
    if parsed_url.netloc != "github.com":
        console.print("[red]Only GitHub repositories are supported for now[/red]")
        raise typer.Exit(1)
    
    repo_path = parsed_url.path.strip("/")
    
    # Get repository information
    github_client = GitHubClient(github_api_key)
    repo = github_client.client.get_repo(repo_path)
    
    if not repo:
        console.print(f"[red]Repository {repo_path} not found[/red]")
        raise typer.Exit(1)
    
    # Build the new entry
    new_entry = f"* [{repo.name}]({repo_url}) - {repo.description or 'No description'}"
    
    # Read the README
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # If a section is specified, add the project to that section
    if section:
        section_marker = f"## {section}"
        if section_marker not in content:
            console.print(f"[red]Section '{section}' not found in {readme_path}[/red]")
            raise typer.Exit(1)
        
        # Find the insertion position
        section_pos = content.find(section_marker)
        next_section_pos = content.find("##", section_pos + 1)
        if next_section_pos == -1:
            next_section_pos = len(content)
        
        # Insert the project at the end of the section
        new_content = content[:next_section_pos] + new_entry + "\n\n" + content[next_section_pos:]
    else:
        # Add to the end of the file
        new_content = content + "\n\n" + new_entry + "\n"
    
    # Write the new content
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    console.print(f"[green]Project {repo.name} successfully added to {readme_path}[/green]")