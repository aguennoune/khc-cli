"""ETL pipeline for Awesome lists."""

import logging
import typer
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from pathlib import Path
from dotenv import load_dotenv
from typing_extensions import Annotated
from urllib.parse import urlparse
from termcolor import colored
import traceback

from khc_cli.github_client import GitHubClient
from khc_cli.utils.helpers import fetch_awesome_readme_content, initialize_csv_writers, crawl_github_dependents

console = Console()
LOGGER = logging.getLogger(__name__)
# Load environment variables from .env file
load_dotenv()

def run_etl_pipeline(
    awesome_repo_url: str,
    awesome_readme_filename: str,
    local_readme_path: Path,
    projects_csv_path: Path,
    orgs_csv_path: Path,
    github_api_key: str = None,
):
    """
    Run the ETL pipeline for an Awesome list.
    
    Args:
        awesome_repo_url: URL of the GitHub repository containing the Awesome list
        awesome_readme_filename: Name of the README file (usually "README.md")
        local_readme_path: Path where to save the local copy of the README
        projects_csv_path: Path where to save the CSV file with projects information
        orgs_csv_path: Path where to save the CSV file with organizations information
        github_api_key: GitHub API key for authentication
    """
    # Initialization
    g = GitHubClient(github_api_key).client
    awesome_repo_path = urlparse(awesome_repo_url).path.strip("/")
    
    # Extraction
    try:
        awesome_repo_data = fetch_awesome_readme_content(g, awesome_repo_path, awesome_readme_filename, local_readme_path)
    except Exception as e:
        console.print(f"[red]Error extracting README: {e}[/red]")
        LOGGER.error(f"Error fetching or parsing Awesome README: {e}", exc_info=True)
        raise typer.Exit(code=1)
    
    # Initialize CSV writers
    try:
        writer_projects, writer_github_organizations, existing_orgs, csv_projects_file, csv_orgs_file = initialize_csv_writers(
            projects_csv_path, orgs_csv_path
        )
    except Exception as e:
        console.print(f"[red]Error initializing CSV writers: {e}[/red]")
        LOGGER.error(f"Error initializing CSV writers: {e}", exc_info=True)
        raise typer.Exit(code=1)
    
    # Transformation and loading
    failures = []
    retry = False
    total_entries = sum(len(rubric.entries) for rubric in awesome_repo_data.rubrics)
    
    progress_columns = [
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
    ]
    
    with Progress(*progress_columns, transient=False) as progress_bar:
        task = progress_bar.add_task("Processing projects...", total=total_entries)
        
        # Main processing logic
        # This function is simplified and focuses on the main structure
        # The complete project processing code should be moved here
        
        for r_idx, rubric in enumerate(awesome_repo_data.rubrics):
            for entry_idx, entry in enumerate(rubric.entries):
                progress_bar.update(task, advance=1, description=f"Processing: {entry.name[:30]}...")
                LOGGER.info(f"Processing project: {entry.name} ({entry.url}) from rubric: {rubric.key}")
                
                # Project processing code here...
                # This code is very simplified compared to the original
                
                try:
                    # Check the platform type (GitHub, GitLab, other)
                    url_parts = urlparse(entry.url)
                    platform = url_parts.netloc
                    
                    project_data = {
                        "project_name": entry.name,
                        "oneliner": entry.text[2:] if entry.text.startswith("- ") else entry.text,
                        "git_url": entry.url,
                        "rubric": rubric.key,
                        "platform": platform
                    }
                    
                    if platform == "github.com":
                        # GitHub-specific processing
                        repo_path = url_parts.path.strip("/")
                        # Call to a function that would process GitHub repos
                        # process_github_repo(g, repo_path, project_data, writer_github_organizations, existing_orgs)
                    
                    # Write project data
                    writer_projects.writerow(project_data)
                    
                except Exception as e:
                    console.print(colored(f"Failed to process {entry.url}: {e}", "red"))
                    failures.append(entry.url)
    
    # Close files
    csv_projects_file.close()
    csv_orgs_file.close()
    
    # Final report
    console.print("------------------------")
    console.print(colored("ETL Processing finished.", "green"))
    if failures:
        console.print(colored(f"Failed to process {len(failures)} projects:", "yellow"))
        for failed_url in failures:
            console.print(f"  - {failed_url}")
    else:
        console.print(colored("All projects processed successfully.", "green"))
    
    return failures