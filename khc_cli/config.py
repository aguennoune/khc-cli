"""Configuration management for khc-cli."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "version": 1.0,
    "config": {
        "default_output_format": "markdown",
        "cache_dir": str(Path.home() / ".cache" / "khc-cli"),
        "log_level": "info",
        "api_keys": {"github": ""}
    },
    "commands": {
        "analyze": {
            "description": "Analyze a GitHub repository or an Awesome list",
            "usage": "khc-cli analyze [OPTIONS] TYPE TARGET",
            "options": {
                "--format": "Output format (markdown, json, csv)",
                "--output": "Output file (default: stdout)"
            },
            "examples": [
                "khc-cli analyze repo Krypto-Hashers-Community/khc-cli",
                "khc-cli analyze awesome https://github.com/sindresorhus/awesome"
            ]
        },
        "curate": {
            "description": "Help curate an Awesome list",
            "usage": "khc-cli curate [OPTIONS] TARGET",
            "options": {
                "--check-links": "Check for dead links",
                "--suggest": "Suggest improvements"
            },
            "examples": [
                "khc-cli curate ./awesome-list.md --check-links"
            ]
        },
        "status": {
            "description": "Show CLI and configuration status",
            "usage": "khc-cli status [OPTIONS]",
            "options": {
                "--verbose": "Show detailed information"
            },
            "examples": [
                "khc-cli status --verbose"
            ]
        }
    },
    "installation": {
        "pip": {
            "command": "pip install khc-cli"
        },
        "from_source": {
            "steps": [
                "git clone https://github.com/Krypto-Hashers-Community/khc-cli.git",
                "cd khc-cli",
                "pip install -e ."
            ]
        },
        "verify": {
            "command": "khc-cli --version"
        }
    },
    "readthedocs": {
        "url": "https://khc-cli.readthedocs.io/",
        "setup": [
            "mkdir -p docs/source",
            "cd docs",
            "sphinx-quickstart --sep --project=\"KHC CLI\" --author=\"Your Name\" --language=en"
        ],
        "conf_py": {
            "content": """
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_click',
]

html_theme = 'sphinx_rtd_theme'
"""
        },
        "requirements": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme",
            "sphinx-click"
        ],
        "build_locally": {
            "command": "cd docs && make html"
        },
        "yml_config": """
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: '3.10'
python:
  install:
    - method: pip
      path: .
    - requirements: docs/requirements.txt
sphinx:
  configuration: docs/source/conf.py
  fail_on_warning: false
"""
    }
}

CONFIG_PATH = Path.home() / ".khc_cli_rc"

def load_config() -> Dict[str, Any]:
    """
    Load configuration from ~/.khc_cli_rc if it exists.
    Returns default configuration otherwise.
    """
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, "r") as f:
            user_config = yaml.safe_load(f)
        # Recursive merge
        def update_recursive(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = update_recursive(d[k], v)
                else:
                    d[k] = v
            return d
        merged_config = DEFAULT_CONFIG.copy()
        if user_config and isinstance(user_config, dict):
            merged_config = update_recursive(merged_config, user_config)
        return merged_config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG

def get_config_value(key: str, default=None):
    """Quick access to a config key (root level)."""
    config = load_config()
    return config.get(key, default)
