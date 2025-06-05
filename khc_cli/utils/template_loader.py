"""Utilities for loading templates."""

import os
import importlib.resources

def get_awesome_list_template():
    """
    Retrieve the Awesome List template from the package resources.
    
    Returns:
        str: The content of the Awesome List template.
    """
    try:
        # Modern method with importlib.resources (Python 3.9+)
        with importlib.resources.files("khc_cli.resources").joinpath("awesome_list_template.md").open("r", encoding="utf-8") as f:
            return f.read()
    except (ImportError, AttributeError, FileNotFoundError):
        # Fallback with relative path
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(current_dir, "resources", "awesome_list_template.md")
        
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()