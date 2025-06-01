"""Utility functions for khc CLI."""

import re
import time
import base64
import logging
import requests
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path
from rich.console import Console
from datetime import datetime

console = Console()
LOGGER = logging.getLogger(__name__)

def countdown(t):
    """Visual countdown in console."""
    while t:
        mins, secs = divmod(int(t), 60)
        timeformat = "{:02d}:{:02d}".format(mins, secs)
        console.print(timeformat, end="\r")
        time.sleep(1)
        t -= 1
    console.print("\n\n\n\n\n")

def crawl_github_dependents(repo, page_num):
    """
    Retrieve the dependents of a GitHub repository.
    
    Args:
        repo (str): Repository name in format 'owner/repo'
        page_num (int): Number of pages to crawl
        
    Returns:
        list: List of repositories that depend on the given repo
    """
    url = 'https://github.com/{}/network/dependents'.format(repo)
    dependents_data = []
    list_end = False
    
    for i in range(page_num):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")

        page_data = [
            "{}/{}".format(
                t.find('a', {"data-repository-hovercards-enabled":""}).text,
                t.find('a', {"data-hovercard-type":"repository"}).text
            )
            for t in soup.findAll("div", {"class": "Box-row"})
        ]
        
        for dependent in page_data:
            if dependent in dependents_data:
                list_end = True 
        
        if list_end:
            break
        else:    
            dependents_data = dependents_data + page_data
        
        try:
            paginationContainer = soup.find("div", {"class":"paginate-container"}).find_all('a')
        except:
            break
        
        try:
            if len(paginationContainer) > 1:
                paginationContainer = paginationContainer[1]
            else:
                paginationContainer = paginationContainer[0]
        except:
            break
        
        if paginationContainer:
            url = paginationContainer["href"]
        else:
            break
        
    return dependents_data

def fetch_awesome_readme_content(github_client, awesome_repo_path, readme_filename, local_readme_path):
    """
    Fetch the README content of an Awesome list.
    
    Args:
        github_client: GitHub client instance
        awesome_repo_path (str): Path to the repository (owner/repo)
        readme_filename (str): Name of the README file
        local_readme_path (Path): Path where to save the README locally
        
    Returns:
        AwesomeList: Parsed representation of the Awesome list
    """
    from khc_cli.awesomecure.awesome2py import AwesomeList
    
    awesome_repo = github_client.get_repo(awesome_repo_path)
    if not awesome_repo:
        raise ValueError(f"Repository {awesome_repo_path} not found")
        
    awesome_content_encoded = awesome_repo.get_contents(
        urllib.parse.quote(readme_filename)
    ).content
    awesome_content = base64.b64decode(awesome_content_encoded)
    
    # Create parent directory if needed
    Path(local_readme_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(local_readme_path, "w", encoding="utf-8") as filehandle:
        filehandle.write(awesome_content.decode("utf-8"))
    LOGGER.info(f"Awesome README saved to {local_readme_path}")
    return AwesomeList(str(local_readme_path))

def initialize_csv_writers(projects_csv_path, orgs_csv_path):
    """
    Initialize CSV writers for projects and organizations.
    
    Args:
        projects_csv_path (Path): Path to the projects CSV file
        orgs_csv_path (Path): Path to the organizations CSV file
        
    Returns:
        tuple: (writer_projects, writer_github_organizations, existing_orgs, csv_projects_file, csv_orgs_file)
    """
    import csv
    from pathlib import Path
    
    projects_csv_path = Path(projects_csv_path)
    orgs_csv_path = Path(orgs_csv_path)
    
    projects_csv_path.parent.mkdir(parents=True, exist_ok=True)
    orgs_csv_path.parent.mkdir(parents=True, exist_ok=True)

    csv_fieldnames = [
        "project_name", "oneliner", "git_namespace", "git_url", "platform",
        "topics", "rubric", "last_commit_date", "stargazers_count",
        "number_of_dependents", "stars_last_year", "project_active",
        "dominating_language", "organization", "organization_user_name",
        "languages", "homepage", "readme_content", "refs", "project_created",
        "project_age_in_days", "license", "total_commits_last_year",
        "total_number_of_commits", "last_issue_closed", "open_issues",
        "closed_pullrequests", "closed_issues", "issues_closed_last_year",
        "days_until_last_issue_closed", "open_pullrequests", "reviews_per_pr",
        "development_distribution_score", "last_released_date",
        "last_release_tag_name", "good_first_issue", "contributors",
        "accepts_donations", "donation_platforms", "code_of_conduct",
        "contribution_guide", "dependents_repos", "organization_name",
        "organization_github_url", "organization_website",
        "organization_location", "organization_country", "organization_form",
        "organization_avatar", "organization_public_repos",
        "organization_created", "organization_last_update",
    ]

    csv_github_organizations_fieldnames = [
        "organization_name", "organization_user_name", "organization_github_url",
        "organization_website", "organization_location", "organization_country",
        "organization_form", "organization_avatar", "organization_public_repos",
        "organization_created", "organization_last_update", "organization_rubric"
    ]

    csv_projects_file = open(projects_csv_path, "w", newline="", encoding="utf-8")
    writer_projects = csv.DictWriter(csv_projects_file, fieldnames=csv_fieldnames)
    writer_projects.writeheader()

    existing_orgs = set()
    if orgs_csv_path.exists():
        with open(orgs_csv_path, "r", newline="", encoding="utf-8") as f_org_read:
            reader_github_organizations = csv.DictReader(f_org_read)
            for entry in reader_github_organizations:
                if 'organization_user_name' in entry:
                    existing_orgs.add(entry['organization_user_name'])

    csv_orgs_file = open(orgs_csv_path, "a", newline="", encoding="utf-8")
    writer_github_organizations = csv.DictWriter(csv_orgs_file, fieldnames=csv_github_organizations_fieldnames)
    # Write header only if file is new/empty
    if orgs_csv_path.stat().st_size == 0:
        writer_github_organizations.writeheader()

    return writer_projects, writer_github_organizations, existing_orgs, csv_projects_file, csv_orgs_file