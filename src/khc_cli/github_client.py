"""GitHub client for interacting with the GitHub API."""

import os
import logging
import time
from datetime import datetime
from github import Github
from rich.console import Console
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

console = Console()
LOGGER = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, token=None):
        """Initialize the GitHub client with a token."""
        self.token = token or os.getenv("GITHUB_API_KEY")
        if not self.token:
            console.print("[red]Error: GitHub token not found. Use --github-api-key or set GITHUB_API_KEY[/red]")
            raise ValueError("GitHub token is required")
            
        self.client = Github(self.token)
    
    def get_repo(self, repo_path):
        """Retrieve a GitHub repository."""
        try:
            return self.client.get_repo(repo_path)
        except Exception as e:
            console.print(f"[red]Error retrieving repo {repo_path}: {e}[/red]")
            return None
    
    def get_rate_limit(self):
        """Check the API rate limits."""
        rate_limit = self.client.rate_limiting
        reset_time = self.client.rate_limiting_resettime
        return {
            "remaining": rate_limit[0],
            "total": rate_limit[1],
            "reset_time": datetime.fromtimestamp(reset_time)
        }
        
    def check_rate_limit(self, min_requests_remaining=100):
        """Check if API limit is approaching and wait if necessary."""
        limit_info = self.get_rate_limit()
        remaining, total = limit_info["remaining"], limit_info["total"]
        reset_time = self.client.rate_limiting_resettime
        
        LOGGER.info(f"GitHub API Rate Limit: {remaining}/{total} requests remaining. Resets at {limit_info['reset_time']}.")
        
        if remaining < min_requests_remaining:
            wait_time = max(0, (reset_time - datetime.now().timestamp()) + 5)  # Add 5s buffer
            LOGGER.warning(f"Approaching GitHub rate limit. Waiting for {wait_time:.0f} seconds...")
            console.print(f"Waiting for {wait_time:.0f} seconds for GitHub API rate limit to reset...")
            self._countdown(wait_time)
    
    def _countdown(self, t):
        """Countdown timer for waiting."""
        while t:
            mins, secs = divmod(int(t), 60)
            timeformat = "{:02d}:{:02d}".format(mins, secs)
            console.print(timeformat, end="\r")
            time.sleep(1)
            t -= 1
        console.print("\n\n\n\n\n")